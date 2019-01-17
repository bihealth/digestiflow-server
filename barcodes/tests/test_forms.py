from test_plus.test import TestCase

from digestiflow.test_utils import SetupUserMixin, SetupProjectMixin
from ..forms import BarcodeSetForm
from ..tests import SetupBarcodeSetMixin


class BarcodeSetFormTest(SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, TestCase):
    """Test ``BarcodeSetForm``"""

    def testInitWithoutObject(self):
        """Test initialization of ``BarcodeSetForm`` with model object"""
        BarcodeSetForm()

    def testInitWithObject(self):
        """Test initialization of ``BarcodeSetForm`` without model object"""
        BarcodeSetForm(self.barcode_set)

    def testIsValid(self):
        """Test ``BarcodeSetForm.is_valid()`` method"""
        form = BarcodeSetForm(self.barcode_set_form_post_data)
        self.assertTrue(form.is_valid(), form.errors)
