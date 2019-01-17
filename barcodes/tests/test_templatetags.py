from test_plus.test import TestCase

from ..templatetags import barcodes
from digestiflow.test_utils import SetupUserMixin, SetupProjectMixin
from ..tests import SetupBarcodeSetMixin


class TemplateTagsTest(SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, TestCase):
    """Test the template tags."""

    def testGetDetailsBarcodeSets(self):
        result = barcodes.get_details_barcodesets(self.project)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.first(), self.barcode_set)
