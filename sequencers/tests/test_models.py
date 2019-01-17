from test_plus.test import TestCase
from django.shortcuts import reverse

from digestiflow.test_utils import SetupUserMixin, SetupProjectMixin
from ..models import SequencingMachine, MACHINE_MODEL_HISEQ2000, INDEX_WORKFLOW_A
from ..tests import SetupSequencingMachineMixin


class SequencingMachineTest(
    SetupSequencingMachineMixin, SetupProjectMixin, SetupUserMixin, TestCase
):
    """Test the ``SequencingMachine`` model"""

    def testCreate(self):
        """Test creating ``SequencingMachine`` objects"""
        self.assertEqual(SequencingMachine.objects.count(), 1)
        SequencingMachine.objects.create(
            project=self.project,
            vendor_id="Hyyyyyyyy",
            label="Another test machine",
            description="This is to be found",
            machine_model=MACHINE_MODEL_HISEQ2000,
            slot_count=2,
            dual_index_workflow=INDEX_WORKFLOW_A,
        )
        self.assertEqual(SequencingMachine.objects.count(), 2)

    def testUpdate(self):
        """Test updating ``SequencingMachine`` objects"""
        self.hiseq2000.vendor_id = "Hzzzzzzzz"
        self.hiseq2000.save()

        other = SequencingMachine.objects.get(pk=self.hiseq2000.pk)
        self.assertEqual(other.vendor_id, self.hiseq2000.vendor_id)

    def testDelete(self):
        """Test deleting``SequencingMachine`` objects"""
        self.assertEqual(SequencingMachine.objects.count(), 1)
        self.hiseq2000.delete()
        self.assertEqual(SequencingMachine.objects.count(), 0)

    def testStr(self):
        """Test ``__str__()``"""
        self.assertEqual(str(self.hiseq2000), "SequencingMachine: Hxxxxxxxx (Test machine)")

    def testGetAbsoluteUrl(self):
        """Test ``get_absolute_url()``"""
        self.assertEqual(
            self.hiseq2000.get_absolute_url(),
            reverse(
                "sequencers:sequencer-detail",
                kwargs={"project": self.project.sodar_uuid, "sequencer": self.hiseq2000.sodar_uuid},
            ),
        )


class SequencingMachineManagerTest(
    SetupSequencingMachineMixin, SetupProjectMixin, SetupUserMixin, TestCase
):
    """Test the ``SequencingMachineManager``"""

    def testFindByVendorId(self):
        """Test finding by ``vendor_id``"""
        machine = self.make_machine()
        result = SequencingMachine.objects.find("Hyyyyyyyy")
        self.assertEqual(list(result), [machine])

    def testFindByLabel(self):
        """Test finding by ``label``"""
        machine = self.make_machine()
        result = SequencingMachine.objects.find("another")
        self.assertEqual(list(result), [machine])

    def testFindByDescription(self):
        """Test finding by ``description``"""
        machine = self.make_machine()
        result = SequencingMachine.objects.find("this")
        self.assertEqual(list(result), [machine])
