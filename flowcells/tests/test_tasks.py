# import datetime

# from django.shortcuts import reverse
from test_plus.test import TestCase

from barcodes.tests import SetupBarcodeSetMixin
from digestiflow.test_utils import SetupUserMixin, SetupProjectMixin
from sequencers.tests import SetupSequencingMachineMixin

from ..models import FlowCell, FLOWCELL_ERROR_CACHE_VERSION
from ..tasks import flowcell_update_error_caches, flowcell_update_outdated_error_caches
from ..tests import SetupFlowCellMixin


class FlowCellUpdateErrorCachesTaskTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``flowcell_update_error_caches()`` function."""

    def testUpdateErrorCachesTask(self):
        # Create duplicate library
        self.flow_cell.libraries.create(
            name="ONE",
            barcode=self.barcode_set_entry,
            barcode2=self.barcode_set_entry,
            lane_numbers=[1, 2, 3, 4],
        )
        # Clear caches
        self.flow_cell.cache_index_errors = None
        self.flow_cell.cache_reverse_index_errors = None
        self.flow_cell.cache_sample_sheet_errors = None
        self.flow_cell.error_caches_version = None
        self.flow_cell.save()

        # Execute the update task.
        flowcell_update_error_caches(self.flow_cell.pk)

        # Load flow cell from database
        flow_cell = FlowCell.objects.get(pk=self.flow_cell.pk)
        self.assertEquals(len(flow_cell.cache_index_errors), 4)
        self.assertEquals(len(flow_cell.cache_reverse_index_errors), 2)
        self.assertEquals(len(flow_cell.cache_sample_sheet_errors), 2)
        self.assertEquals(flow_cell.error_caches_version, FLOWCELL_ERROR_CACHE_VERSION)


class FlowCellUpdateOutdatedErrorCachesTaskTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``flowcell_update_outdated_error_caches()`` function."""

    def testUpdateOutdatedErrorCachesTask(self):
        # Create duplicate library
        self.flow_cell.libraries.create(
            name="ONE",
            barcode=self.barcode_set_entry,
            barcode2=self.barcode_set_entry,
            lane_numbers=[1, 2, 3, 4],
        )
        # Clear caches
        self.flow_cell.cache_index_errors = None
        self.flow_cell.cache_reverse_index_errors = None
        self.flow_cell.cache_sample_sheet_errors = None
        self.flow_cell.error_caches_version = None
        self.flow_cell.save()

        # Execute the update task.
        tasks = flowcell_update_outdated_error_caches()
        for task in tasks:
            task.wait()

        # Load flow cell from database
        flow_cell = FlowCell.objects.get(pk=self.flow_cell.pk)
        self.assertEquals(len(flow_cell.cache_index_errors), 4)
        self.assertEquals(len(flow_cell.cache_reverse_index_errors), 2)
        self.assertEquals(len(flow_cell.cache_sample_sheet_errors), 2)
        self.assertEquals(flow_cell.error_caches_version, FLOWCELL_ERROR_CACHE_VERSION)
