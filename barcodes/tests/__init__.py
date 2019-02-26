import json

from ..models import BarcodeSet, BARCODE_SET_GENERIC


class SetupBarcodeSetMixin:
    def setUp(self):
        super().setUp()
        self.barcode_set = BarcodeSet.objects.create(
            project=self.project,
            name="Test Set",
            short_name="TS",
            description="This is an example barcode set",
        )
        self.barcode_set_entry = self.barcode_set.entries.create(
            name="First entry", sequence="AAAAAAAA"
        )
        # Additional data for posting to views
        self.barcode_set_form_post_data = {
            "name": "Another Test Set",
            "short_name": "ATS",
            "description": "This is another example barcode set",
            "entries_json": json.dumps(
                [
                    {"name": "First entry", "aliases": "", "sequence": "AAAAAAAA"},
                    {"name": "one", "aliases": "", "sequence": "CCCCCCCC"},
                ]
            ),
            "set_type": BARCODE_SET_GENERIC,
        }
        # Additional data for posting to API
        self.barcode_set_api_post_data = {
            "name": "Another Test Set",
            "short_name": "ATS",
            "description": "This is another example barcode set",
            "set_type": BARCODE_SET_GENERIC,
        }
        self.barcode_set_entry_api_post_data = {"name": "Second Entry", "sequence": "GTGAGTG"}

    def make_barcode_set(self):
        return BarcodeSet.objects.create(
            project=self.project,
            name="A Third Test Set",
            short_name="3TS",
            description="This is a third example barcode set",
        )

    def make_barcode_set_entry(self, barcode_set=None):
        return (barcode_set or self.barcode_set).entries.create(
            name="Third Entry", sequence="GATTACA"
        )
