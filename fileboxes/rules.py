"""Permissions configured using django-rules."""

import rules
from projectroles import rules as pr_rules


rules.add_perm("fileboxes", rules.always_allow)
# NB: attachment is handled directly via files
rules.add_perm(
    "fileboxes.view_%s" % "data",
    pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)
for action in ("add", "change", "delete"):
    rules.add_perm(
        "fileboxes.%s_%s" % (action, "data"),
        pr_rules.is_project_owner | pr_rules.is_project_delegate | pr_rules.is_project_contributor,
    )
