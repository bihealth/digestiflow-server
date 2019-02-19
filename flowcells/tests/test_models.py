import datetime

from django.core import mail
from django.shortcuts import reverse
from projectroles.models import PROJECT_TAG_STARRED
from test_plus.test import TestCase

from barcodes.tests import SetupBarcodeSetMixin
from digestiflow.test_utils import SetupUserMixin, SetupProjectMixin
from sequencers.tests import SetupSequencingMachineMixin
from ..models import (
    pretty_range,
    prefix_match,
    FlowCell,
    FlowCellTag,
    flow_cell_updated,
    flow_cell_created,
    KnownIndexContamination,
    Library,
    Message,
    message_created,
    FLOWCELL_TAG_WATCHING,
    STATUS_COMPLETE,
)
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
            run_date=datetime.date(2019, 1, 18),
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
        self.assertEqual(len(result), 11)
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
        self.assertEquals(self.flow_cell.get_index_errors(), {})
        self.flow_cell.update_error_caches().save()
        self.flow_cell = FlowCell.objects.get(pk=self.flow_cell.pk)
        self.assertEqual(list(sorted(self.flow_cell.get_index_errors().keys())), expected)

    def testGetIndexErrorsEmptySheet(self):
        """Test if sheet is empty"""
        flow_cell = self.make_flow_cell()
        self.assertEquals(flow_cell.get_index_errors(), {})
        flow_cell.update_error_caches().save()
        flow_cell = FlowCell.objects.get(pk=flow_cell.pk)
        self.assertEqual(flow_cell.get_index_errors(), {})

    def testGetReverseIndexErrors(self):
        """Test ``get_reverse_index_errors()``"""
        result = self.flow_cell.get_reverse_index_errors()
        self.assertEquals(result, {})
        self.flow_cell.update_error_caches().save()
        self.flow_cell = FlowCell.objects.get(pk=self.flow_cell.pk)
        result = self.flow_cell.get_reverse_index_errors()
        self.assertEquals(len(result), 1)
        self.assertIn(str(self.library.sodar_uuid), result)

    def testGetReverseIndexErrorsEmptySheet(self):
        """Test if sheet is empty"""
        flow_cell = self.make_flow_cell()
        self.assertEqual(flow_cell.get_reverse_index_errors(), {})
        flow_cell.update_error_caches().save()
        flow_cell = FlowCell.objects.get(pk=flow_cell.pk)
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
        self.assertEquals(result, {})
        self.flow_cell.update_error_caches().save()
        self.flow_cell = FlowCell.objects.get(pk=self.flow_cell.pk)
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
        flow_cell.update_error_caches().save()
        flow_cell = FlowCell.objects.get(pk=flow_cell.pk)
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


class FlowCellTagTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``FlowCellTag`` model"""

    def testCreate(self):
        """Test creating ``FlowCellTag`` objects"""
        self.assertEqual(FlowCellTag.objects.count(), 1)
        self.flow_cell.tags.create(user=self.user, name="hearting")
        self.assertEqual(FlowCellTag.objects.count(), 2)

    def testUpdate(self):
        """Test updating ``FlowCellTag`` objects"""
        self.tag_user_watches_flow_cell.name = "yay"
        self.tag_user_watches_flow_cell.save()

        other = FlowCellTag.objects.get(pk=self.tag_user_watches_flow_cell.pk)
        self.assertEqual(other.name, self.tag_user_watches_flow_cell.name)

    def testDelete(self):
        """Test deleting ``FlowCellTag`` objects"""
        self.assertEqual(FlowCellTag.objects.count(), 1)
        self.tag_user_watches_flow_cell.delete()
        self.assertEqual(FlowCellTag.objects.count(), 0)

    def testStr(self):
        """Test ``__str__()``"""
        self.assertEqual(str(self.tag_user_watches_flow_cell), "Hasdfghijkl: author: WATCHING")


class FlowCellCreatedTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Tests for ``flow_cell_created()```."""

    def testProjectStargazersNotified(self):
        """Test that those having the project starred are emailed and subscribed"""
        # setup
        self.project.tags.create(user=self.user, name=PROJECT_TAG_STARRED)
        flow_cell2 = self.make_flow_cell()
        self.assertEqual(flow_cell2.tags.count(), 0)
        # test code
        flow_cell_created(flow_cell2)
        # check created objects
        self.assertEqual(flow_cell2.tags.count(), 1)
        tag = list(flow_cell2.tags.all())[0]
        self.assertEqual(tag.user, self.user)
        self.assertEqual(tag.name, FLOWCELL_TAG_WATCHING)
        # check email
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["author@example.com"])
        self.assertEqual(mail.outbox[0].subject, "[Digestiflow] Flow Cell Created: Hasdfasdf")
        self.assertIn("Hasdfasdf", mail.outbox[0].body)

    def testDemuxOperatorNotified(self):
        """Test that the flow cell demultiplexer is notified"""
        # setup
        flow_cell2 = self.make_flow_cell(demux_operator=self.user)
        self.assertEqual(flow_cell2.tags.count(), 0)
        # test code
        flow_cell_created(flow_cell2)
        # check created objects
        self.assertEqual(flow_cell2.tags.count(), 1)
        tag = list(flow_cell2.tags.all())[0]
        self.assertEqual(tag.user, self.user)
        self.assertEqual(tag.name, FLOWCELL_TAG_WATCHING)
        # check email
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["author@example.com"])
        self.assertEqual(mail.outbox[0].subject, "[Digestiflow] Flow Cell Created: Hasdfasdf")
        self.assertIn("Hasdfasdf", mail.outbox[0].body)


class FlowCellUpdatedTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Tests for ``flow_cell_updated()```."""

    def testWatchersNotifiedOnStateChange(self):
        """Test that the flow cell watchers are notified"""
        self.flow_cell.status_conversion = STATUS_COMPLETE
        original = FlowCell.objects.get(pk=self.flow_cell.pk)
        flow_cell_updated(original, self.flow_cell)
        # check email
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["author@example.com"])
        self.assertEqual(
            mail.outbox[0].subject, "[Digestiflow] Flow Cell State Changed: Hasdfghijkl"
        )
        self.assertIn("Hasdfghijkl", mail.outbox[0].body)

    def testDemuxOperatorNotifiedOnStateChange(self):
        """Test that the flow demux operator are notified"""
        self.flow_cell.status_conversion = STATUS_COMPLETE
        original = FlowCell.objects.get(pk=self.flow_cell.pk)
        self.tag_user_watches_flow_cell.delete()
        self.flow_cell.demux_operator = self.make_user(username="foo")
        flow_cell_updated(original, self.flow_cell)
        # check email
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["foo@example.com"])
        self.assertEqual(
            mail.outbox[0].subject, "[Digestiflow] Flow Cell State Changed: Hasdfghijkl"
        )
        self.assertIn("Hasdfghijkl", mail.outbox[0].body)

    def testNobodyNofiedOnStateNochange(self):
        """Test that the flow cell watchers are notified"""
        flow_cell_updated(self.flow_cell, self.flow_cell)
        self.assertEqual(len(mail.outbox), 0)


class LibraryTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``Library`` model"""

    def testCreate(self):
        """Test creating ``Library`` objects"""
        self.assertEqual(Library.objects.count(), 1)
        self.flow_cell.libraries.create(
            name="The_Name", barcode_seq="ATATATAGCGCGC", lane_numbers=[1, 2]
        )
        self.assertEqual(Library.objects.count(), 2)

    def testUpdate(self):
        """Test updating ``Library`` objects"""
        self.library.name = "yay"
        self.library.save()

        other = Library.objects.get(pk=self.library.pk)
        self.assertEqual(other.name, self.library.name)

    def testDelete(self):
        """Test deleting``Library`` objects"""
        self.assertEqual(Library.objects.count(), 1)
        self.library.delete()
        self.assertEqual(Library.objects.count(), 0)

    def testStr(self):
        """Test ``__str__()``"""
        self.assertEqual(
            str(self.library),
            "Library ONE on lane(s) [1, 2, 3, 4] for FlowCell 190118_Hxxxxxxxx_0001_A_Hasdfghijkl_my_flow_cell",
        )

    def testGetAbsoluteUrl(self):
        """Test ``get_absolute_url()``"""
        self.assertEqual(
            self.library.get_absolute_url(),
            reverse(
                "flowcells:flowcell-detail",
                kwargs={
                    "project": self.project.sodar_uuid,
                    "flowcell": self.library.flow_cell.sodar_uuid,
                },
            )
            + "?library=%s" % self.library.sodar_uuid,
        )


class LibraryManagerTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``LibraryManagerTest``"""

    def testFindByName(self):
        """Test finding by ``name``"""
        flow_cell = self.make_flow_cell()
        library = self.make_library(flow_cell)
        result = Library.objects.find("three")
        self.assertEqual(list(result), [library])

    def testFindByBarcodeSeq(self):
        """Test finding by ``barcode_seq``"""
        flow_cell = self.make_flow_cell()
        library = self.make_library(flow_cell)
        result = Library.objects.find("atatat")
        self.assertEqual(list(result), [library])

    def testFindByBarcodeSeq2(self):
        """Test finding by ``barcode_seq2``"""
        flow_cell = self.make_flow_cell()
        library = self.make_library(flow_cell)
        result = Library.objects.find("gcgcgcgc")
        self.assertEqual(list(result), [library])


class MessageTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``Message`` model"""

    def testCreate(self):
        """Test creating ``Message`` objects"""
        self.assertEqual(Message.objects.count(), 2)
        self.flow_cell.messages.create(subject="my subject", body="my body", author=self.user)
        self.assertEqual(Message.objects.count(), 3)

    def testUpdate(self):
        """Test updating ``Message`` objects"""
        self.sent_message.subject = "yay"
        self.sent_message.save()

        other = Message.objects.get(pk=self.sent_message.pk)
        self.assertEqual(other.subject, self.sent_message.subject)

    def testDelete(self):
        """Test deleting``Message`` objects"""
        self.assertEqual(Message.objects.count(), 2)
        self.sent_message.delete()
        self.assertEqual(Message.objects.count(), 1)

    def testStr(self):
        """Test ``__str__()``"""
        self.assertTrue(str(self.sent_message).endswith("] the message subject"))

    def testGetAbsoluteUrl(self):
        """Test ``get_absolute_url()``"""
        self.assertEqual(
            self.sent_message.get_absolute_url(),
            reverse(
                "flowcells:flowcell-detail",
                kwargs={
                    "project": self.project.sodar_uuid,
                    "flowcell": self.sent_message.flow_cell.sodar_uuid,
                },
            )
            + "#message-%s" % self.sent_message.sodar_uuid,
        )


class MessageCreatedTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test ``message_created()``"""

    def testWatchersNotifiedOnNewMessage(self):
        """Test that the flow cell watchers are notified"""
        self.sent_message.author = self.make_user(username="foo")
        self.sent_message.save()
        message_created(self.sent_message)
        # check email
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["author@example.com"])
        self.assertEqual(
            mail.outbox[0].subject, "[Digestiflow] New Message for Flow Cell: Hasdfghijkl"
        )
        self.assertIn("Hasdfghijkl", mail.outbox[0].body)

    def testDemuxOperatorNotifiedOnNewMessage(self):
        """Test that the flow demux operator are notified"""
        self.flow_cell.demux_operator = self.make_user(username="foo")
        self.flow_cell.save()
        self.tag_user_watches_flow_cell.delete()
        message_created(self.sent_message)
        # check email
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["foo@example.com"])
        self.assertEqual(
            mail.outbox[0].subject, "[Digestiflow] New Message for Flow Cell: Hasdfghijkl"
        )
        self.assertIn("Hasdfghijkl", mail.outbox[0].body)


class MessageManagerTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``MessageManagerTest``"""

    def testFindBySubject(self):
        """Test finding by ``subject``"""
        flow_cell = self.make_flow_cell()
        message = self.make_message(flow_cell)
        result = Message.objects.find("third subject")
        self.assertEqual(list(result), [message])

    def testFindByBody(self):
        """Test finding by ``body``"""
        flow_cell = self.make_flow_cell()
        message = self.make_message(flow_cell)
        result = Message.objects.find("third body")
        self.assertEqual(list(result), [message])


class KnownIndexContaminationTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``KnownIndexContamination`` model"""

    def testFactoryDefaultsFromMigrations(self):
        """Test Presence of index contaminations inserted by migration"""
        self.assertEqual(KnownIndexContamination.objects.count(), 7)

    def testCreate(self):
        """Test creating ``KnownIndexContamination`` objects"""
        self.assertEqual(KnownIndexContamination.objects.count(), 7)
        KnownIndexContamination.objects.create(
            title="Yet another title", description="Yet another description", sequence="TCTCTCTCTC"
        )
        self.assertEqual(KnownIndexContamination.objects.count(), 8)

    def testUpdate(self):
        """Test updating ``KnownIndexContamination`` objects"""
        self.known_index_contamination.title = "yay"
        self.known_index_contamination.save()

        other = KnownIndexContamination.objects.get(pk=self.known_index_contamination.pk)
        self.assertEqual(other.title, self.known_index_contamination.title)

    def testDelete(self):
        """Test deleting ``KnownIndexContamination`` objects"""
        self.assertEqual(KnownIndexContamination.objects.count(), 7)
        self.known_index_contamination.delete()
        self.assertEqual(KnownIndexContamination.objects.count(), 6)

    def testStr(self):
        """Test ``__str__()``"""
        self.assertEqual(str(self.known_index_contamination), "CGATCGATCGAT: Some Contamination")
