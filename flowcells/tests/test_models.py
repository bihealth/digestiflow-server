import datetime

from test_plus.test import TestCase
from django.shortcuts import reverse

from barcodes.tests import SetupBarcodeSetMixin
from digestiflow.test_utils import SetupUserMixin, SetupProjectMixin
from sequencers.tests import SetupSequencingMachineMixin
from ..models import (
    pretty_range,
    prefix_match,
    FlowCell,
)  # FlowCellTag, Library, LaneIndexHistogram, Message, KnownIndexContamination
from ..tests import SetupFlowCellMixin


class HelperFunctionsTest(TestCase):
    """Tests for the helper functions."""

    def testPrettyRange(self):
        """Test for ``pretty_range()```"""
        self.assertEqual(pretty_range([1, 2, 3, 5, 7, 8, 9]), "1-3,5,7-9")

    def testPrefixMatchTrue(self):
        """Test for ``prefix_match()``` with valid cases"""
        self.assertTrue(prefix_match("12345", ["1234"]))
        self.assertTrue(prefix_match("12345", ["12345"]))
        self.assertTrue(prefix_match("12345", ["123456"]))

    def testPrefixMatchFalse(self):
        """Test for ``prefix_match()``` with invalid cases"""
        self.assertFalse(prefix_match("x12345", ["1234"]))
        self.assertFalse(prefix_match("x12345", ["12345"]))
        self.assertFalse(prefix_match("x12345", ["123456"]))


class FlowCellTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``FlowCell`` model"""

    def testCreate(self):
        """Test creating ``FlowCell`` objects"""
        self.assertEqual(FlowCell.objects.count(), 1)
        FlowCell.objects.create(
            project=self.project,
            run_date=datetime.date.today(),
            sequencing_machine=self.hiseq2000,
            run_number=42,
            slot="A",
            vendor_id="Hveryverynew",
            label="a_new_flow_cell",
            description="A new flow cell",
        )
        self.assertEqual(FlowCell.objects.count(), 2)

    def testUpdate(self):
        """Test updating ``FlowCell`` objects"""
        self.flow_cell.vendor_id = "ASDF"
        self.flow_cell.save()

        other = FlowCell.objects.get(pk=self.flow_cell.pk)
        self.assertEqual(other.vendor_id, self.flow_cell.vendor_id)

    def testDelete(self):
        """Test deleting``FlowCell`` objects"""
        self.assertEqual(FlowCell.objects.count(), 1)
        self.flow_cell.delete()
        self.assertEqual(FlowCell.objects.count(), 0)

    def testStr(self):
        """Test ``__str__()``"""
        self.assertEqual(
            str(self.flow_cell), "FlowCell 190118_Hxxxxxxxx_0001_A_Hasdfghijkl_my_flow_cell"
        )

    def testGetAbsoluteUrl(self):
        """Test ``get_absolute_url()``"""
        self.assertEqual(
            self.flow_cell.get_absolute_url(),
            reverse(
                "flowcells:flowcell-detail",
                kwargs={"project": self.project.sodar_uuid, "flowcell": self.flow_cell.sodar_uuid},
            ),
        )

    def testIsPaired(self):
        """Test ``@property def is_paired()``"""
        self.assertTrue(self.flow_cell.is_paired)

    def testGetPlannedReadsTuples(self):
        """Test ``get_planned_reads_tuples()``"""
        self.assertEqual(
            self.flow_cell.get_planned_reads_tuples(), ((150, "T"), (10, "B"), (150, "T"))
        )

    def testGetSentMessages(self):
        """Test ``get_sent_messages()``"""
        self.assertEqual(list(self.flow_cell.get_sent_messages()), [self.sent_message])

    def testName(self):
        """Test ``@property def name()``"""
        self.assertEqual(self.flow_cell.name, self.flow_cell.vendor_id)

    def testGetFullName(self):
        """Test ``get_full_name()``"""
        self.assertEqual(
            self.flow_cell.get_full_name(), "190118_Hxxxxxxxx_0001_A_Hasdfghijkl_my_flow_cell"
        )

    def testHasSheetForLane(self):
        """Test ``has_sheet_for_lane()``"""
        for i in range(1, 5):
            self.assertTrue(self.flow_cell.has_sheet_for_lane(i))
        for i in range(5, 9):
            self.assertFalse(self.flow_cell.has_sheet_for_lane(i))

    def testGetKnownContaminations(self):
        """Test ``get_known_contaminations()``"""
        result = self.flow_cell.get_known_contaminations()
        self.assertEqual(len(result), 8)
        self.assertIn("AAAAAAAA", result)
        self.assertIn("AAAAAAAAAA", result)

    def testGetIndexErrors(self):
        """Test ``get_index_errors()``"""
        expected = [
            (1, 1, "ACGTACGTAG"),
            (2, 1, "ACGTACGTAG"),
            (3, 1, "ACGTACGTAG"),
            (4, 1, "ACGTACGTAG"),
        ]
        self.assertEqual(list(sorted(self.flow_cell.get_index_errors().keys())), expected)

    def testGetIndexErrorsEmptySheet(self):
        """Test if sheet is empty"""
        flow_cell = self.make_flow_cell()
        self.assertEqual(flow_cell.get_index_errors(), {})
        # Also check the branch with caching
        self.assertEqual(flow_cell.get_index_errors(), {})

    def testGetReverseIndexErrors(self):
        """Test ``get_reverse_index_errors()``"""
        result = self.flow_cell.get_reverse_index_errors()
        self.assertTrue(len(result), 1)
        self.assertIn(str(self.library.sodar_uuid), result)

    def testGetReverseIndexErrorsEmptySheet(self):
        """Test if sheet is empty"""
        flow_cell = self.make_flow_cell()
        self.assertEqual(flow_cell.get_reverse_index_errors(), {})
        # Also check the branch with caching
        self.assertEqual(flow_cell.get_reverse_index_errors(), {})

    def testGetSampleSheetErrors(self):
        """Test ``get_sample_sheet_errors()`` with duplicate name"""
        library_dup = self.flow_cell.libraries.create(
            name="ONE",
            barcode=self.barcode_set_entry,
            barcode2=self.barcode_set_entry,
            lane_numbers=[1, 2, 3, 4],
        )
        result = self.flow_cell.get_sample_sheet_errors()
        self.assertIn("name", result[str(self.library.sodar_uuid)])
        self.assertIn("barcode", result[str(self.library.sodar_uuid)])
        self.assertIn("barcode2", result[str(self.library.sodar_uuid)])
        self.assertIn("name", result[str(library_dup.sodar_uuid)])
        self.assertIn("barcode", result[str(library_dup.sodar_uuid)])
        self.assertIn("barcode2", result[str(library_dup.sodar_uuid)])

    def testGetSampleSheetErrorsEmptySheet(self):
        """Test if sheet is empty"""
        flow_cell = self.make_flow_cell()
        self.assertEqual(flow_cell.get_sample_sheet_errors(), {})
        # Also check the branch with caching
        self.assertEqual(flow_cell.get_sample_sheet_errors(), {})

    def testIsUserWatching(self):
        """Test ``is_user_watching()``"""
        self.assertTrue(self.flow_cell.is_user_watching(self.user))


class FlowCellManagerTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``FlowCellManager``"""

    def testFindByVendorId(self):
        """Test finding by ``vendor_id``"""
        result = FlowCell.objects.find("hasdfghijkl")
        self.assertEqual(list(result), [self.flow_cell])

    def testFindByLabel(self):
        """Test finding by ``label``"""
        result = FlowCell.objects.find("my_flow_cell")
        self.assertEqual(list(result), [self.flow_cell])

    def testFindByManualLabel(self):
        """Test finding by ``manual_label``"""
        result = FlowCell.objects.find("myflowcell")
        self.assertEqual(list(result), [self.flow_cell])

    def testFindByDescription(self):
        """Test finding by ``manual_label``"""
        result = FlowCell.objects.find("first")
        self.assertEqual(list(result), [self.flow_cell])


# class BarcodeSetEntryTest(SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, TestCase):
#     """Test the ``BarcodeSetEntry`` model"""
#
#     # TODO: add validation for unique name and sequence in barcode set
#
#     def testCreate(self):
#         """Test creating ``BarcodeSetEntry`` objects"""
#         self.assertEqual(BarcodeSetEntry.objects.count(), 1)
#         self.barcode_set.entries.create(name="My name", sequence="ATATATAGCGCGC")
#         self.assertEqual(BarcodeSetEntry.objects.count(), 2)
#
#     def testUpdate(self):
#         """Test updating ``BarcodeSetEntry`` objects"""
#         self.barcode_set_entry.name = "yay"
#         self.barcode_set_entry.save()
#
#         other = BarcodeSetEntry.objects.get(pk=self.barcode_set_entry.pk)
#         self.assertEqual(other.name, self.barcode_set_entry.name)
#
#     def testDelete(self):
#         """Test deleting``BarcodeSetEntry`` objects"""
#         self.assertEqual(BarcodeSetEntry.objects.count(), 1)
#         self.barcode_set_entry.delete()
#         self.assertEqual(BarcodeSetEntry.objects.count(), 0)
#
#     def testStr(self):
#         """Test ``__str__()``"""
#         self.assertEqual(str(self.barcode_set_entry), "First entry (AAAAAAAA)")
#
#     def testGetAbsoluteUrl(self):
#         """Test ``get_absolute_url()``"""
#         self.assertEqual(
#             self.barcode_set_entry.get_absolute_url(),
#             reverse(
#                 "flowcells:flowcell-detail",
#                 kwargs={
#                     "project": self.project.sodar_uuid,
#                     "barcodeset": self.barcode_set_entry.barcode_set.sodar_uuid,
#                 },
#             )
#             + "?barcode_set_entry=%s" % self.barcode_set_entry.sodar_uuid,
#         )
#
#
# class BarcodeSetEntryManagerTest(SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, TestCase):
#     """Test the ``BarcodeSetEntryManager``"""
#
#     def testFindByName(self):
#         """Test finding by ``name``"""
#         barcode_set = self.make_barcode_set()
#         barcode_set_entry = self.make_barcode_set_entry(barcode_set)
#         result = BarcodeSetEntry.objects.find("third")
#         self.assertEqual(list(result), [barcode_set_entry])
#
#     def testFindBySequence(self):
#         """Test finding by ``sequence``"""
#         barcode_set = self.make_barcode_set()
#         barcode_set_entry = self.make_barcode_set_entry(barcode_set)
#         result = BarcodeSetEntry.objects.find("GATTACA")
#         self.assertEqual(list(result), [barcode_set_entry])
