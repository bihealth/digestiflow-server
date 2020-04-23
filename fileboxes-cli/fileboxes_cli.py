#!/usr/bin/env python
"""DigestiFlow FileBoxes Client.

This is assumed to be running as the same user as Apache and setup writeable
directories for Apache.  Access control is the handled by Apache WebDAV File
System module.
"""

__author__ = "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>"

import argparse
import datetime
import difflib
import logging
import os
import shutil
import sys
import textwrap
import typing
import uuid

import attr
import cattr
import logzero
import pendulum
from logzero import logger
import requests

#: Template for constructing file box list URLs.
URL_TPL_LIST = "%(base_url)s/api/fileboxes/%(project)s/"
#: Template for fetch/upadate file box list URLs.
URL_TPL_DETAIL = "%(base_url)s/api/fileboxes/%(project)s/%(filebox)s/"
#: Template for constructing audit entries list URLs.
URL_TPL_AUDIT = "%(base_url)s/api/audit-entries/%(project)s/%(filebox)s/"
#: Template for .htaccess file.
TPL_HTACCESS = """
AuthType Basic
AuthName "Login with 'user@CHARITE' or 'user@MDC-BERLIN'."
AuthBasicProvider PAM
AuthPAMService httpd
Require user {users}
"""


@attr.s(frozen=True, auto_attribs=True)
class Config:
    """Configuration of he fileboxes_cli tool."""

    #: The URL of the DigestiFlow server.
    digestiflow_url: str
    #: Whether or not to check certificates when connecting via HTTPs.
    cert_check: bool
    #: List of project UUID(s) to pull from DigestiFlow.
    projects: typing.List[str]
    #: Base directory to manage directories below.
    base_dir: str
    #: The auth token to use.
    auth_token: str = attr.ib(repr=lambda value: repr("%s%s" % (value[:3], "***")))
    #: The directory creation mode.
    mode: int


@attr.s(frozen=True, auto_attribs=True)
class AccountGrant:
    sodar_uuid: uuid.uuid4
    username: str


@attr.s(frozen=True, auto_attribs=True)
class FileBox:
    sodar_uuid: uuid.uuid4
    project: uuid.uuid4
    title: str
    description: str
    date_frozen: datetime.datetime
    date_expiry: datetime.datetime
    state_meta: str
    state_data: str
    account_grants: typing.List[AccountGrant]


#: Custom converter to use between JSON-like structs and types.
converter = cattr.Converter()
converter.register_structure_hook(uuid.uuid4, lambda s, _: uuid.UUID(s))
converter.register_structure_hook(datetime.datetime, lambda s, _: pendulum.parse(s))


def setup_dir(config: Config, project_uuid: str, file_box: FileBox, log_lines=None):
    """Create directory for file box."""
    path = os.path.join(config.base_dir, str(file_box.sodar_uuid))
    log_lines = log_lines if log_lines is not None else []
    if not os.path.exists(path):
        log_lines.append("Creating directory %s" % path)

    logger.info("Creating directory %s...", path)
    os.makedirs(path, exist_ok=True)
    return "ACTIVE"


def sync_grants(config: Config, project_uuid: str, file_box: FileBox, log_lines=None):
    """Create directory for file box."""
    log_lines = log_lines if log_lines is not None else []
    path = os.path.join(config.base_dir, str(file_box.sodar_uuid))
    logger.info("Synchronizing access grants for %s...", path)

    htaccess_path = os.path.join(path, ".htaccess")
    if os.path.exists(htaccess_path):
        old_htaccess_path = ".htaccess"
        with open(htaccess_path, "rt") as inf:
            old_htaccess_txt = inf.read()
    else:
        old_htaccess_path = "/dev/null"
        old_htaccess_txt = ""

    new_htaccess_path = ".htaccess"
    htaccess_tpl = textwrap.dedent(TPL_HTACCESS).strip()
    users = [g.username for g in file_box.account_grants]
    htaccess_txt = htaccess_tpl.format(users=" ".join(users))

    diff_lines = list(
        difflib.unified_diff(
            old_htaccess_txt.splitlines(False),
            htaccess_txt.splitlines(False),
            old_htaccess_path,
            new_htaccess_path,
        )
    )
    if "".join(diff_lines):
        log_lines.append("Apply diff to %s/.htaccess" % path)
        log_lines.append("==== 8< ==== 8< ====")
        log_lines += diff_lines
        log_lines.append("==== 8< ==== 8< ====")

    logging.debug("Writing to %s", htaccess_path)
    with open(htaccess_path, "wt") as outf:
        print(htaccess_txt, file=outf)


def delete_dir(config: Config, project_uuid: str, file_box: FileBox, log_lines=None):
    """Delete directory for file box."""
    log_lines = log_lines if log_lines is not None else []
    path = os.path.join(config.base_dir, str(file_box.sodar_uuid))
    logger.info("Deleting directory %s...", path)
    log_lines.append("Deleting directory %s" % path)
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except OSError as e:
        log_lines.append("Problem with deletion of %s: %s" % (path, e))
        logger.warn("Problem with deletion of %s: %s", path, e)
    else:
        return "DELETED"


def process_project(config: Config, project_uuid: str):
    """Process one project."""
    res = requests.get(
        URL_TPL_LIST % {"base_url": config.digestiflow_url, "project": project_uuid},
        headers={"Authorization": "Token %s" % config.auth_token},
        verify=config.cert_check,
    )
    res.raise_for_status()
    log_lines = []
    file_boxes = [converter.structure(box_data, FileBox) for box_data in res.json()]
    dispatch = {  # (state_data, state_meta)
        # initial in metadata == active
        ("INITIAL", "INITIAL"): (setup_dir, sync_grants,),
        ("INITIAL", "INITIAL"): (sync_grants,),
        ("ININITIAL", "INITIAL"): (setup_dir, sync_grants,),
        ("DELETING", "INITIAL"): (),
        ("DELETED", "INITIAL"): (setup_dir, sync_grants,),
        # active in metadata
        ("INITIAL", "ACTIVE"): (setup_dir, sync_grants,),
        ("ACTIVE", "ACTIVE"): (sync_grants,),
        ("INACTIVE", "ACTIVE"): (setup_dir, sync_grants,),
        ("DELETING", "ACTIVE"): (),
        ("DELETED", "ACTIVE"): (setup_dir, sync_grants,),
        # inactive in metadata
        ("INITIAL", "INACTIVE"): (),
        ("ACTIVE", "INACTIVE"): (sync_grants,),
        ("INACTIVE", "INACTIVE"): (),
        ("DELETING", "INACTIVE"): (),
        ("DELETED", "INACTIVE"): (),
        # deleted in metadata
        ("INITIAL", "DELETED"): (delete_dir,),
        ("ACTIVE", "DELETED"): (delete_dir,),
        ("INACTIVE", "DELETED"): (delete_dir,),
        ("DELETING", "DELETED"): (),
        ("DELETED", "DELETED"): (),
    }
    for file_box in file_boxes:
        logger.info("Processing file box %s", file_box.sodar_uuid)
        logger.debug("state = (%s, %s)", file_box.state_data, file_box.state_meta)
        new_state = None  # first function can return new state
        funcs = dispatch[(file_box.state_data, file_box.state_meta)]
        for func in funcs:
            new_state = new_state or func(config, project_uuid, file_box, log_lines)
        if log_lines:
            if delete_dir in funcs:
                data = {
                    "action": "FS_DATA_REMOVED",
                    "message": "Removed directory on file system.",
                    "raw_log": "\n".join(log_lines),
                }
            else:
                data = {
                    "action": "FS_APPLY_STATE",
                    "message": "Applied state to file system.",
                    "raw_log": "\n".join(log_lines),
                }
            url = URL_TPL_AUDIT % {
                "base_url": config.digestiflow_url,
                "project": project_uuid,
                "filebox": file_box.sodar_uuid,
            }
            logger.debug("POST to %s", url)
            res = requests.post(
                url,
                data=data,
                headers={"Authorization": "Token %s" % config.auth_token},
                verify=config.cert_check,
            )
            res.raise_for_status()
            url = URL_TPL_DETAIL % {
                "base_url": config.digestiflow_url,
                "project": project_uuid,
                "filebox": file_box.sodar_uuid,
            }
            logger.debug("PATCH to %s", url)
            res = requests.patch(
                url,
                data={"state_data": new_state},
                headers={"Authorization": "Token %s" % config.auth_token},
                verify=config.cert_check,
            )
    if log_lines:
        print("LOGS\n%s" % "\n".join(log_lines))
    else:
        print("NO LOGS")


def run(config: Config):
    logger.info("Starting fileboxes_cli...")
    logger.info("config = %s", config)

    os.makedirs(config.base_dir, exist_ok=True)

    for project in config.projects:
        logger.info("Querying project %s", project)
        process_project(config, project)

    logger.info("All done. Have a nice day!")


def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument("--digestiflow-url", required=True, help="Base URL of DigestiFlow server.")
    parser.add_argument(
        "--no-cert-check",
        dest="cert_check",
        default=True,
        action="store_false",
        help="Disable SSL certificate checking.",
    )
    parser.add_argument(
        "--projects", nargs="+", required=True, help="UUID(s) for the projects to manage."
    )
    parser.add_argument(
        "--base-dir",
        required=True,
        help="Path to the directory to manage the file box directories.",
    )
    parser.add_argument("--auth-token", required=True, help="The auth token to use.")
    parser.add_argument("--mode", type=str, default="0770", help="The default mode")

    logzero.formatter(
        logzero.LogFormatter(fmt="%(color)s[%(levelname)1.1s %(asctime)s]%(end_color)s %(message)s")
    )

    args = parser.parse_args(argv)
    args.mode = int(args.mode, 8)
    return run(Config(**vars(args)))


if __name__ == "__main__":
    sys.exit(main())
