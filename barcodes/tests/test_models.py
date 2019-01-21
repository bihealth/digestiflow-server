from test_plus.test import TestCase
from django.shortcuts import reverse

from digestiflow.test_utils import SetupUserMixin, SetupProjectMixin
from ..models import BarcodeSet, BarcodeSetEntry
from ..tests import SetupBarcodeSetMixin


class BarcodeSetTest(SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, TestCase):
    """Test the ``BarcodeSet`` model"""

    def testCreate(self):
        """Test creating ``BarcodeSet`` objects"""
        self.assertEqual(BarcodeSet.objects.count(), 1)
        BarcodeSet.objects.create(
            project=self.project, name="My name", short_name="MN", description="This is to be found"
        )
        self.assertEqual(BarcodeSet.objects.count(), 2)

    def testUpdate(self):
        """Test updating ``BarcodeSet`` objects"""
        self.barcode_set.short_name = "yay"
        self.barcode_set.save()

        other = BarcodeSet.objects.get(pk=self.barcode_set.pk)
        self.assertEqual(other.short_name, self.barcode_set.short_name)

    def testDelete(self):
        """Test deleting``BarcodeSet`` objects"""
        self.assertEqual(BarcodeSet.objects.count(), 1)
        self.barcode_set.delete()
        self.assertEqual(BarcodeSet.objects.count(), 0)

    def testStr(self):
        """Test ``__str__()``"""
        self.assertEqual(str(self.barcode_set), "Test Set (TS)")

    def testGetAbsoluteUrl(self):
        """Test ``get_absolute_url()``"""
        self.assertEqual(
            self.barcode_set.get_absolute_url(),
            reverse(
                "barcodes:barcodeset-detail",
                kwargs={
                    "project": self.project.sodar_uuid,
                    "barcodeset": self.barcode_set.sodar_uuid,
                },
            ),
        )

    def testGetFlowCells(self):
        self.assertEqual(list(self.barcode_set.get_flowcells()), [])


class BarcodeSetManagerTest(SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, TestCase):
    """Test the ``BarcodeSetManager``"""

    def testFindByShortName(self):
        """Test finding by ``short_name``"""
        barcode_set = self.make_barcode_set()
        result = BarcodeSet.objects.find("3TS")
        self.assertEqual(list(result), [barcode_set])

    def testFindByName(self):
        """Test finding by ``name``"""
        barcode_set = self.make_barcode_set()
        result = BarcodeSet.objects.find("third")
        self.assertEqual(list(result), [barcode_set])

    def testFindByDescription(self):
        """Test finding by ``description``"""
        barcode_set = self.make_barcode_set()
        result = BarcodeSet.objects.find("third example")
        self.assertEqual(list(result), [barcode_set])


class BarcodeSetEntryTest(SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, TestCase):
    """Test the ``BarcodeSetEntry`` model"""

    # TODO: add test for validation for unique name and sequence in barcode set

    def testCreate(self):
        """Test creating ``BarcodeSetEntry`` objects"""
        self.assertEqual(BarcodeSetEntry.objects.count(), 1)
        self.barcode_set.entries.create(name="My name", sequence="ATATATAGCGCGC")
        self.assertEqual(BarcodeSetEntry.objects.count(), 2)

    def testUpdate(self):
        """Test updating ``BarcodeSetEntry`` objects"""
        self.barcode_set_entry.name = "yay"
        self.barcode_set_entry.save()

        other = BarcodeSetEntry.objects.get(pk=self.barcode_set_entry.pk)
        self.assertEqual(other.name, self.barcode_set_entry.name)

    def testDelete(self):
        """Test deleting``BarcodeSetEntry`` objects"""
        self.assertEqual(BarcodeSetEntry.objects.count(), 1)
        self.barcode_set_entry.delete()
        self.assertEqual(BarcodeSetEntry.objects.count(), 0)

    def testStr(self):
        """Test ``__str__()``"""
        self.assertEqual(str(self.barcode_set_entry), "First entry (AAAAAAAA)")

    def testGetAbsoluteUrl(self):
        """Test ``get_absolute_url()``"""
        self.assertEqual(
            self.barcode_set_entry.get_absolute_url(),
            reverse(
                "barcodes:barcodeset-detail",
                kwargs={
                    "project": self.project.sodar_uuid,
                    "barcodeset": self.barcode_set_entry.barcode_set.sodar_uuid,
                },
            )
            + "?barcode_set_entry=%s" % self.barcode_set_entry.sodar_uuid,
        )


class BarcodeSetEntryManagerTest(SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, TestCase):
    """Test the ``BarcodeSetEntryManager``"""

    def testFindByName(self):
        """Test finding by ``name``"""
        barcode_set = self.make_barcode_set()
        barcode_set_entry = self.make_barcode_set_entry(barcode_set)
        result = BarcodeSetEntry.objects.find("third")
        self.assertEqual(list(result), [barcode_set_entry])

    def testFindBySequence(self):
        """Test finding by ``sequence``"""
        barcode_set = self.make_barcode_set()
        barcode_set_entry = self.make_barcode_set_entry(barcode_set)
        result = BarcodeSetEntry.objects.find("GATTACA")
        self.assertEqual(list(result), [barcode_set_entry])
