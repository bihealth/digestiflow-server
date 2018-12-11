from datetime import datetime
import json

from django.db import transaction
from django.core.management.base import BaseCommand
from projectroles.models import Project

from ...models import SequencingMachine


class Command(BaseCommand):
    help = "Import sequencing machine from legacy flowcelltool JSON export"

    def add_arguments(self, parser):
        parser.add_argument("--project-uuid", help="UUID of the project", required=True)
        parser.add_argument("json_file", help="Path to JSON file to import")

    @transaction.atomic
    def handle(self, *args, **options):
        project = Project.objects.get(sodar_uuid=options["project_uuid"])
        with open(options["json_file"], "rt") as inputf:
            for seq_json in json.load(inputf):
                self.import_file(project, seq_json)

    def import_file(self, project, seq_json):
        print("Importing {} into {}".format(seq_json["vendor_id"], project.title))
        sequencer = project.sequencingmachine_set.create(
            sodar_uuid=seq_json["uuid"],
            vendor_id=seq_json["vendor_id"],
            label=seq_json["label"],
            description=seq_json["description"],
            machine_model=seq_json["machine_model"],
            slot_count=seq_json["slot_count"],
            dual_index_workflow=seq_json["dual_index_workflow"],
        )
        SequencingMachine.objects.filter(pk=sequencer.pk).update(
            date_created=datetime.strptime(seq_json["created"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            date_modified=datetime.strptime(seq_json["modified"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        )
