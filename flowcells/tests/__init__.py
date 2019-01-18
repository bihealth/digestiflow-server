import datetime
import json

from ..models import FlowCell, FlowCellTag, FLOWCELL_TAG_WATCHING, MSG_STATE_SENT


class SetupFlowCellMixin:
    """Setup ``FlowCell`` for tests.

    This relies on the ``SetupBarcodeSetMixin`` and ``SetupSequencingMachineMixin`` to be also present.
    """

    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.flow_cell = FlowCell.objects.create(
            project=self.project,
            run_date=datetime.date.today(),
            sequencing_machine=self.hiseq2000,
            run_number=1,
            slot="A",
            vendor_id="Hasdfghijkl",
            label="my_flow_cell",
            manual_label="MyFlowCell",
            description="The first",
            planned_reads="150T10B150T",
        )
        self.library = self.flow_cell.libraries.create(
            name="ONE",
            barcode=self.barcode_set_entry,
            barcode2=self.barcode_set_entry,
            lane_numbers=[1, 2, 3, 4],
        )
        # Additional data for posting to views
        self.barcode_set_form_post_data = {
            "project": self.project,
            "run_date": datetime.date.today(),
            "sequencing_machine": self.hiseq2000,
            "run_number": 2,
            "slot": "A",
            "vendor_id": "HxXxXxXxXxX",
            "label": "a_second_flow_cell",
            "description": "yay, my second one",
            "libraries_json": json.dumps(
                [{"name": "TWO", "barcode": str(self.barcode_set_entry.sodar_uuid)}]
            ),
        }
        # Additional data for posting to API
        self.barcode_set_api_post_data = {
            "project": self.project,
            "run_date": datetime.date.today(),
            "sequencing_machine": self.hiseq2000,
            "run_number": 2,
            "slot": "A",
            "vendor_id": "HxXxXxXxXxX",
            "label": "a_second_flow_cell",
            "description": "yay, my second one",
        }
        self.barcode_set_entry_api_post_data = {
            # TODO
        }
        self.user = self.make_user(username="author")
        self.tag_user_watches_flow_cell = FlowCellTag.objects.create(
            flowcell=self.flow_cell, user=self.user, name=FLOWCELL_TAG_WATCHING
        )
        self.sent_message = self.flow_cell.messages.create(
            author=self.user, state=MSG_STATE_SENT, body="The message body"
        )
        for lane in range(1, 5):
            self.flow_cell.index_histograms.create(
                lane=lane,
                index_read_no=1,
                sample_size=1000,
                histogram={self.barcode_set_entry.sequence: 500, "ACGTACGTAG": 500},
            )

    def make_flow_cell(self):
        return FlowCell.objects.create(
            project=self.project,
            run_date=datetime.date.today(),
            sequencing_machine=self.hiseq2000,
            run_number=3,
            slot="A",
            vendor_id="Hasdfasdf",
            label="a_third_flow_cell",
            description="Let's see, the third.",
        )

    def make_library(self, barcode_set=None):
        return (barcode_set or self.barcode_set).entries.create(
            name="THREE",
            barcode=self.barcode_set_entry,
            barcode2=self.barcode_set_entry,
            lane_numbers=[3, 4, 5],
        )
