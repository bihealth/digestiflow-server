import datetime
import json

from ..models import (
    FlowCell,
    FlowCellTag,
    FLOWCELL_TAG_WATCHING,
    MSG_STATE_SENT,
    MSG_STATE_DRAFT,
    KnownIndexContamination,
)


class SetupFlowCellMixin:
    """Setup ``FlowCell`` for tests.

    This relies on the ``SetupBarcodeSetMixin`` and ``SetupSequencingMachineMixin`` to be also present.
    """

    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.flow_cell = FlowCell.objects.create(
            project=self.project,
            run_date=datetime.date(2019, 1, 18),
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
        self.flow_cell_form_post_data = {
            "project": self.project,
            "run_date": datetime.date(2019, 1, 18),
            "sequencing_machine": self.hiseq2000.vendor_id,
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
        self.flow_cell_api_post_data = {
            "project": self.project,
            "run_date": datetime.date(2019, 1, 18),
            "sequencing_machine": self.hiseq2000.vendor_id,
            "run_number": 2,
            "slot": "A",
            "vendor_id": "HxXxXxXxXxX",
            "label": "a_second_flow_cell",
            "description": "yay, my second one",
        }
        self.lane_index_histo_api_post_data = {
            "lane": 1,
            "index_read_no": 1,
            "sample_size": 1000,
            "histogram": json.dumps({"ACGT": 1000}),
        }
        self.user = self.make_user(username="author")
        self.tag_user_watches_flow_cell = FlowCellTag.objects.create(
            flowcell=self.flow_cell, user=self.user, name=FLOWCELL_TAG_WATCHING
        )
        self.sent_message = self.flow_cell.messages.create(
            author=self.user,
            state=MSG_STATE_SENT,
            subject="the message subject",
            body="The message body",
        )
        self.draft_message = self.flow_cell.messages.create(
            author=self.user,
            state=MSG_STATE_DRAFT,
            subject="the draft message subject",
            body="The draft message body",
        )
        for lane in range(1, 5):
            self.flow_cell.index_histograms.create(
                lane=lane,
                index_read_no=1,
                sample_size=1000,
                histogram={self.barcode_set_entry.sequence: 500, "ACGTACGTAG": 500},
            )
        self.known_index_contamination = KnownIndexContamination.objects.create(
            title="Some Contamination", description="Some description", sequence="CGATCGATCGAT"
        )

    def make_flow_cell(self, **kwargs):
        return FlowCell.objects.create(
            project=self.project,
            run_date=datetime.date.today(),
            sequencing_machine=self.hiseq2000,
            run_number=3,
            slot="A",
            vendor_id="Hasdfasdf",
            label="a_third_flow_cell",
            description="Let's see, the third.",
            **kwargs,
        )

    def make_library(self, flow_cell=None):
        return (flow_cell or self.flow_cell).libraries.create(
            name="THREE", barcode_seq="ATATATATA", barcode_seq2="GCGCGCGCG", lane_numbers=[3, 4, 5]
        )

    def make_message(self, flow_cell=None):
        return (flow_cell or self.flow_cell).messages.create(
            subject="the third subject", body="the third body", author=self.user
        )

    def make_known_index_contamination(self):
        return KnownIndexContamination.objects.create(
            title="Another contamination", description="Another description", sequence="ACACACACACA"
        )
