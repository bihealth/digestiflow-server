from datetime import date, datetime
import json

from django.db import transaction
from django.core.management.base import BaseCommand
from projectroles.models import Project

from flowcells.models import FlowCell
from sequencers.models import SequencingMachine
from barcodes.models import BarcodeSetEntry


class Command(BaseCommand):
    help = "Import flow cell from legacy flowcelltool JSON export"

    def add_arguments(self, parser):
        parser.add_argument("--project-uuid", help="UUID of the project", required=True)
        parser.add_argument("json_file", help="Path to JSON file to import")

    @transaction.atomic
    def handle(self, *args, **options):
        project = Project.objects.get(sodar_uuid=options["project_uuid"])
        with open(options["json_file"], "rt") as inputf:
            for fc_json in json.load(inputf):
                self.import_file(project, fc_json)

    def import_file(self, project, fc_json):
        print("Importing {} into {}".format(fc_json["vendor_id"], project.title))
        flowcell = project.flowcell_set.create(
            sodar_uuid=fc_json["uuid"],
            run_date=datetime.strptime(fc_json["run_date"], "%Y-%m-%d"),
            sequencing_machine=SequencingMachine.objects.get(
                sodar_uuid=fc_json["sequencing_machine"]
            ),
            run_number=fc_json["run_number"],
            slot=fc_json["slot"],
            vendor_id=fc_json["vendor_id"],
            label=fc_json["label"],
            manual_label=fc_json.get("manual_label"),
            description=fc_json["description"],
            num_lanes=fc_json["num_lanes"],
            operator=fc_json["operator"],
            demux_operator=None,
            rta_version=fc_json["rta_version"],
            status_sequencing=fc_json["status_sequencing"],
            status_conversion=fc_json["status_conversion"],
            status_delivery=fc_json["status_delivery"],
            delivery_type=fc_json["delivery_type"],
            planned_reads="",
            current_reads="",
            barcode_mismatches=fc_json["barcode_mismatches"],
            silence_index_errors=False,
        )
        FlowCell.objects.filter(pk=flowcell.pk).update(
            date_created=datetime.strptime(fc_json["created"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            date_modified=datetime.strptime(fc_json["modified"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        print("  Importing {} libraries".format(len(fc_json["libraries"])))
        for library in fc_json["libraries"]:
            flowcell.libraries.create(
                sodar_uuid=library["uuid"],
                name=library["name"],
                reference=library["reference"],
                barcode=BarcodeSetEntry.objects.get(sodar_uuid=library["barcode"])
                if library.get("barcode")
                else None,
                barcode2=BarcodeSetEntry.objects.get(sodar_uuid=library["barcode2"])
                if library.get("barcode2")
                else None,
                lane_numbers=library["lane_numbers"],
            )
