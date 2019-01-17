from test_plus.test import TestCase

from ..models import INDEX_WORKFLOW_A, MACHINE_MODEL_HISEQ2000
from ..forms import SequencingMachineForm
from ..tests import SetupUserMixin, SetupProjectMixin, SetupSequencingMachineMixin


class SequencingMachineFormTest(
    SetupSequencingMachineMixin, SetupProjectMixin, SetupUserMixin, TestCase
):
    """Test ``SequencingMachineForm``"""

    def testInitWithObject(self):
        """Test initialization of ``SequencingMachineForm`` with model object"""
        SequencingMachineForm()

    def testInitWithoutObject(self):
        """Test initialization of ``SequencingMachineForm`` without model object"""
        SequencingMachineForm(self.hiseq2000)

    def testIsValid(self):
        """Test ``SequencingMachineForm.is_valid()`` method"""
        form = SequencingMachineForm(
            {
                "project": self.project,
                "vendor_id": "Hzzzzzzzz",
                "label": "Some label",
                "machine_model": MACHINE_MODEL_HISEQ2000,
                "dual_index_workflow": INDEX_WORKFLOW_A,
                "slot_count": 2,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
