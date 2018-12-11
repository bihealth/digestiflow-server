from datetime import datetime
import json

from django.db import transaction
from django.core.management.base import BaseCommand
from projectroles.models import Project

from ...models import BarcodeSet, BarcodeSetEntry


class Command(BaseCommand):
    help = "Import barcode sets from legacy flowcelltool JSON export"

    def add_arguments(self, parser):
        parser.add_argument("--project-uuid", help="UUID of the project", required=True)
        parser.add_argument("json_file", help="Path to JSON file to import")

    @transaction.atomic
    def handle(self, *args, **options):
        project = Project.objects.get(sodar_uuid=options["project_uuid"])
        with open(options["json_file"], "rt") as inputf:
            for bc_json in json.load(inputf):
                self.import_file(project, bc_json)

    def import_file(self, project, bc_json):
        print("Importing {} into {}".format(bc_json["name"], project.title))
        barcodeset = project.barcodeset_set.create(
            sodar_uuid=bc_json["uuid"],
            name=bc_json["name"],
            short_name=bc_json["short_name"],
            description=bc_json["description"],
            set_type=bc_json["set_type"],
        )
        BarcodeSet.objects.filter(pk=barcodeset.pk).update(
            date_created=datetime.strptime(bc_json["created"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            date_modified=datetime.strptime(bc_json["modified"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        print("  inserting {} entries".format(len(bc_json["entries"])))
        for entry in bc_json["entries"]:
            bc_entry = barcodeset.entries.create(
                name=entry["name"], sodar_uuid=entry["uuid"], sequence=entry["sequence"]
            )
            BarcodeSetEntry.objects.filter(pk=bc_entry.pk).update(
                date_created=datetime.strptime(entry["created"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                date_modified=datetime.strptime(entry["modified"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            )
