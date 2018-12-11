from datetime import datetime
import json

from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.management.base import BaseCommand
from projectroles.models import Project

from flowcells.models import FlowCell, Message, MSG_STATE_SENT


class Command(BaseCommand):
    help = "Import flow cell from legacy flowcelltool JSON export"

    def add_arguments(self, parser):
        parser.add_argument("--project-uuid", help="UUID of the project", required=True)
        parser.add_argument("--map-users", help="old=new mapping", nargs="+")
        parser.add_argument("json_file", help="Path to JSON file to import")

    @transaction.atomic
    def handle(self, *args, **options):
        project = Project.objects.get(sodar_uuid=options["project_uuid"])
        user_map = dict([key_value.split("=", 1) for key_value in (options["map_users"] or ())])
        with open(options["json_file"], "rt") as inputf:
            for msg_json in json.load(inputf):
                self.import_file(project, msg_json, user_map)

    def import_file(self, project, msg_json, user_map):
        print("Importing {} into {}".format(msg_json["uuid"], project.title))
        print("  author is {}".format(msg_json["author"]))
        message = Message.objects.create(
            sodar_uuid=msg_json["uuid"],
            author=get_user_model().objects.get(
                username=user_map.get(msg_json["author"], msg_json["author"])
            ),
            flow_cell=project.flowcell_set.get(sodar_uuid=msg_json["thread_object"]),
            state=MSG_STATE_SENT,
            body_format=msg_json["mime_type"],
            tags=[],
            body=msg_json["body"],
        )
        Message.objects.filter(pk=message.pk).update(
            date_created=datetime.strptime(msg_json["created"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            date_modified=datetime.strptime(msg_json["modified"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        )
