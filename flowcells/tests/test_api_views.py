# TODO: check timeline events

import json
from test_plus.test import APITestCase

from barcodes.tests import SetupBarcodeSetMixin
from digestiflow.test_utils import SetupUserMixin, SetupProjectMixin, AuthenticatedRequestMixin
from sequencers.tests import SetupSequencingMachineMixin
from ..models import FlowCell, LaneIndexHistogram, Message
from ..tests import SetupFlowCellMixin


class FlowCellListCreateApiViewTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    AuthenticatedRequestMixin,
    APITestCase,
):
    """Tests for creation of barcode sets using REST API"""

    url_name = "api:flowcells"

    def testGet(self):
        """Test that querying API for the machine list works (with super user)"""
        response = self.runGet(self.root)
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(data), 1)

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        self.runGet(None)
        self.response_401()
        for user in (self.norole, self.unrelated_owner):
            self.runGet(user)
            self.response_403()

    def testGetAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user)
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(len(data), 1)

    def testPost(self):
        """Test that creating machine via API works (with super user)"""
        response = self.runPost(self.root, data=self.flow_cell_api_post_data)
        self.response_201(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertIn("sodar_uuid", data)

    def testPostAccessDenied(self):
        """Test that creating flow cell via API is denied if role assignment is missing"""
        self.runPost(None, data=self.flow_cell_api_post_data)
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.runPost(user, data=self.flow_cell_api_post_data)
            self.response_403()

    def testPostAccessAllowed(self):
        """Test that creating flow cell via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPost(user, data=self.flow_cell_api_post_data)
            self.response_201(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertIn("sodar_uuid", data)
            FlowCell.objects.filter(sodar_uuid=data["sodar_uuid"]).delete()


class FlowCellUpdateApiViewTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    AuthenticatedRequestMixin,
    APITestCase,
):
    """Tests for detail view, update, delete of barcode sets using REST API"""

    url_name = "api:flowcells"

    def testGet(self):
        """Test that querying API for the barcode set list works (with super user)"""
        response = self.runGet(self.root, flowcell=self.flow_cell.sodar_uuid)
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["sodar_uuid"], str(self.flow_cell.sodar_uuid))

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        self.runGet(None, flowcell=self.flow_cell.sodar_uuid)
        self.response_401()
        for user in (self.norole, self.unrelated_owner):
            self.runGet(user)
            self.response_403()

    def testGetAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user, flowcell=self.flow_cell.sodar_uuid)
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["sodar_uuid"], str(self.flow_cell.sodar_uuid))

    def testUpdate(self):
        """Test that creating flow cell set via API works (with super user)"""
        response = self.runPut(
            self.root, flowcell=self.flow_cell.sodar_uuid, data=self.flow_cell_api_post_data
        )
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["label"], self.flow_cell_api_post_data["label"])

    def testUpdateAccessDenied(self):
        """Test that creating flow cell set via API is denied if role assignment is missing"""
        self.runPut(None, flowcell=self.flow_cell.sodar_uuid, data=self.flow_cell_api_post_data)
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.runPut(user, flowcell=self.flow_cell.sodar_uuid, data=self.flow_cell_api_post_data)
            self.response_403()

    def testUpdateAccessAllowed(self):
        """Test that creating flow cell set via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPut(
                user, flowcell=self.flow_cell.sodar_uuid, data=self.flow_cell_api_post_data
            )
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["label"], self.flow_cell_api_post_data["label"])

    def testDelete(self):
        """Test that creating flow cell set via API works (with super user)"""
        self.assertEqual(FlowCell.objects.count(), 1)
        response = self.runDelete(self.root, flowcell=self.flow_cell.sodar_uuid)
        self.response_204(response)
        self.assertEqual(FlowCell.objects.count(), 0)

    def testDeleteAccessDenied(self):
        """Test that creating flow cell via API is denied if role assignment is missing"""
        self.assertEqual(FlowCell.objects.count(), 1)
        self.runDelete(None, flowcell=self.flow_cell.sodar_uuid)
        self.assertEqual(FlowCell.objects.count(), 1)
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.assertEqual(FlowCell.objects.count(), 1)
            self.runDelete(user, flowcell=self.flow_cell.sodar_uuid)
            self.assertEqual(FlowCell.objects.count(), 1)
            self.response_403()

    def testDeleteAccessAllowed(self):
        """Test that creating flow cell via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            FlowCell.objects.all().delete()
            flow_cell = self.make_flow_cell()
            self.assertEqual(FlowCell.objects.count(), 1)
            response = self.runDelete(user, flowcell=flow_cell.sodar_uuid)
            self.response_204(response)
            self.assertEqual(FlowCell.objects.count(), 0)


class FlowCellResolveApiViewTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    AuthenticatedRequestMixin,
    APITestCase,
):
    """Tests for resolving a flow cell by instrument name, run no, and flowcell name"""

    url_name = "api:flowcells-resolve"

    def testGet(self):
        """Test that resolving flow cell works (as super user)"""
        response = self.runGet(
            self.root,
            instrument_id=self.hiseq2000.vendor_id,
            run_no=self.flow_cell.run_number,
            flowcell_id=self.flow_cell.vendor_id,
        )
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["sodar_uuid"], str(self.flow_cell.sodar_uuid))

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        self.runGet(
            None,
            instrument_id=self.flow_cell.sequencing_machine.vendor_id,
            run_no=self.flow_cell.run_number,
            flowcell_id=self.flow_cell.vendor_id,
        )
        self.response_401()
        for user in (self.norole, self.unrelated_owner):
            self.runGet(
                user,
                instrument_id=self.flow_cell.sequencing_machine.vendor_id,
                run_no=self.flow_cell.run_number,
                flowcell_id=self.flow_cell.vendor_id,
            )
            self.response_403()

    def testGetAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(
                user,
                instrument_id=self.flow_cell.sequencing_machine.vendor_id,
                run_no=self.flow_cell.run_number,
                flowcell_id=self.flow_cell.vendor_id,
            )
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["sodar_uuid"], str(self.flow_cell.sodar_uuid))


class LaneIndexHistogramListCreateApiViewTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    AuthenticatedRequestMixin,
    APITestCase,
):
    """Tests for creation of lane index histogram entries using REST API"""

    url_name = "api:indexhistos"

    def testGet(self):
        """Test that querying API for the lane index histograms works (with super user)"""
        response = self.runGet(self.root, flowcell=self.flow_cell.sodar_uuid)
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(data), 4)

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        self.runGet(None, flowcell=self.flow_cell.sodar_uuid)
        self.response_401()
        for user in (self.norole, self.unrelated_owner):
            self.runGet(user, flowcell=self.flow_cell.sodar_uuid)
            self.response_403()

    def testGetAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user, flowcell=self.flow_cell.sodar_uuid)
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(len(data), 4)

    def testPost(self):
        """Test that creating lane index histograms via API works (with super user)"""
        response = self.runPost(
            self.root, flowcell=self.flow_cell.sodar_uuid, data=self.lane_index_histo_api_post_data
        )
        self.response_201(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertIn("sodar_uuid", data)

    def testPostAccessDenied(self):
        """Test that creating lane index histograms via API is denied if role assignment is missing"""
        self.runPost(
            None, flowcell=self.flow_cell.sodar_uuid, data=self.lane_index_histo_api_post_data
        )
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.runPost(
                user, flowcell=self.flow_cell.sodar_uuid, data=self.lane_index_histo_api_post_data
            )
            self.response_403()

    def testPostAccessAllowed(self):
        """Test that creating lane index histograms via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPost(
                user, flowcell=self.flow_cell.sodar_uuid, data=self.lane_index_histo_api_post_data
            )
            self.response_201(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertIn("sodar_uuid", data)
            LaneIndexHistogram.objects.filter(sodar_uuid=data["sodar_uuid"]).delete()


class LaneIndexHistogramUpdateDeleteApiViewTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    AuthenticatedRequestMixin,
    APITestCase,
):
    """Tests for update and delete action using REST API"""

    url_name = "api:indexhistos"

    def testGet(self):
        """Test that querying API for the index histograms works (with super user)"""
        response = self.runGet(
            self.root,
            flowcell=self.flow_cell.sodar_uuid,
            indexhistogram=self.histograms[0].sodar_uuid,
        )
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["sodar_uuid"], str(self.histograms[0].sodar_uuid))

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        self.runGet(
            None, flowcell=self.flow_cell.sodar_uuid, indexhistogram=self.histograms[0].sodar_uuid
        )
        self.response_401()
        for user in (self.norole, self.unrelated_owner):
            self.runGet(
                user,
                flowcell=self.flow_cell.sodar_uuid,
                indexhistogram=self.histograms[0].sodar_uuid,
            )
            self.response_403()

    def testGetAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(
                user,
                flowcell=self.flow_cell.sodar_uuid,
                indexhistogram=self.histograms[0].sodar_uuid,
            )
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["sodar_uuid"], str(self.histograms[0].sodar_uuid))

    def testUpdate(self):
        """Test that creating index histograms via API works (with super user)"""
        response = self.runPut(
            self.root,
            flowcell=self.flow_cell.sodar_uuid,
            indexhistogram=self.histograms[0].sodar_uuid,
            data=self.lane_index_histo_api_post_data,
        )
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["sample_size"], self.lane_index_histo_api_post_data["sample_size"])

    def testUpdateAccessDenied(self):
        """Test that creating index histograms via API is denied if role assignment is missing"""
        self.runPut(
            None,
            flowcell=self.flow_cell.sodar_uuid,
            indexhistogram=self.histograms[0].sodar_uuid,
            data=self.lane_index_histo_api_post_data,
        )
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.runPut(
                user,
                flowcell=self.flow_cell.sodar_uuid,
                indexhistogram=self.histograms[0].sodar_uuid,
                data=self.lane_index_histo_api_post_data,
            )
            self.response_403()

    def testUpdateAccessAllowed(self):
        """Test that creating index histograms via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPut(
                user,
                flowcell=self.flow_cell.sodar_uuid,
                indexhistogram=self.histograms[0].sodar_uuid,
                data=self.lane_index_histo_api_post_data,
            )
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(
                data["sample_size"], self.lane_index_histo_api_post_data["sample_size"]
            )

    def testDelete(self):
        """Test that creating index histograms via API works (with super user)"""
        self.assertEqual(LaneIndexHistogram.objects.count(), 4)
        response = self.runDelete(
            self.root,
            flowcell=self.flow_cell.sodar_uuid,
            indexhistogram=self.histograms[0].sodar_uuid,
        )
        self.response_204(response)
        self.assertEqual(LaneIndexHistogram.objects.count(), 3)

    def testDeleteAccessDenied(self):
        """Test that creating index histograms via API is denied if role assignment is missing"""
        self.assertEqual(LaneIndexHistogram.objects.count(), 4)
        self.runDelete(
            None, flowcell=self.flow_cell.sodar_uuid, indexhistogram=self.histograms[0].sodar_uuid
        )
        self.assertEqual(LaneIndexHistogram.objects.count(), 4)
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.assertEqual(LaneIndexHistogram.objects.count(), 4)
            self.runDelete(
                user,
                flowcell=self.flow_cell.sodar_uuid,
                indexhistogram=self.histograms[0].sodar_uuid,
            )
            self.assertEqual(LaneIndexHistogram.objects.count(), 4)
            self.response_403()

    def testDeleteAccessAllowed(self):
        """Test that creating index histograms via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            LaneIndexHistogram.objects.all().delete()
            index_histogram = self.make_index_histogram()
            self.assertEqual(LaneIndexHistogram.objects.count(), 1)
            response = self.runDelete(
                user, flowcell=self.flow_cell.sodar_uuid, indexhistogram=index_histogram.sodar_uuid
            )
            self.response_204(response)
            self.assertEqual(LaneIndexHistogram.objects.count(), 0)


class MessageListCreateApiViewTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    AuthenticatedRequestMixin,
    APITestCase,
):
    """Tests for creation of messages using REST API"""

    url_name = "api:messages"

    def testGet(self):
        """Test that querying API for the messages works (with super user)"""
        response = self.runGet(self.root, flowcell=self.flow_cell.sodar_uuid)
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(data), 2)

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        self.runGet(None, flowcell=self.flow_cell.sodar_uuid)
        self.response_401()
        for user in (self.norole, self.unrelated_owner):
            self.runGet(user, flowcell=self.flow_cell.sodar_uuid)
            self.response_403()

    def testGetAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user, flowcell=self.flow_cell.sodar_uuid)
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(len(data), 2)

    def testPost(self):
        """Test that creating messages via API works (with super user)"""
        response = self.runPost(
            self.root, flowcell=self.flow_cell.sodar_uuid, data=self.sent_message_api_post_data
        )
        self.response_201(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertIn("sodar_uuid", data)

    def testPostAccessDenied(self):
        """Test that creating messages via API is denied if role assignment is missing"""
        self.runPost(None, flowcell=self.flow_cell.sodar_uuid, data=self.sent_message_api_post_data)
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.runPost(
                user, flowcell=self.flow_cell.sodar_uuid, data=self.sent_message_api_post_data
            )
            self.response_403()

    def testPostAccessAllowed(self):
        """Test that creating messages via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPost(
                user, flowcell=self.flow_cell.sodar_uuid, data=self.sent_message_api_post_data
            )
            self.response_201(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertIn("sodar_uuid", data)
            Message.objects.filter(sodar_uuid=data["sodar_uuid"]).delete()


class MessageUpdateDeleteApiViewTest(
    SetupFlowCellMixin,
    SetupSequencingMachineMixin,
    SetupBarcodeSetMixin,
    SetupProjectMixin,
    SetupUserMixin,
    AuthenticatedRequestMixin,
    APITestCase,
):
    """Tests for update and delete action using REST API"""

    url_name = "api:messages"

    def testGet(self):
        """Test that querying API for messages works (with super user)"""
        response = self.runGet(
            self.root, flowcell=self.flow_cell.sodar_uuid, message=self.sent_message.sodar_uuid
        )
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["sodar_uuid"], str(self.sent_message.sodar_uuid))

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        self.runGet(None, flowcell=self.flow_cell.sodar_uuid, message=self.sent_message.sodar_uuid)
        self.response_401()
        for user in (self.norole, self.unrelated_owner):
            self.runGet(
                user, flowcell=self.flow_cell.sodar_uuid, message=self.sent_message.sodar_uuid
            )
            self.response_403()

    def testGetAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(
                user, flowcell=self.flow_cell.sodar_uuid, message=self.sent_message.sodar_uuid
            )
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["sodar_uuid"], str(self.sent_message.sodar_uuid))

    def testUpdate(self):
        """Test that updating messages via API works (with super user)"""
        response = self.runPut(
            self.root,
            flowcell=self.flow_cell.sodar_uuid,
            message=self.sent_message.sodar_uuid,
            data=self.sent_message_api_post_data,
        )
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["subject"], self.sent_message_api_post_data["subject"])

    def testUpdateAccessDenied(self):
        """Test that updating messages via API is denied if role assignment is missing"""
        self.runPut(
            None,
            flowcell=self.flow_cell.sodar_uuid,
            message=self.sent_message.sodar_uuid,
            data=self.sent_message_api_post_data,
        )
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.runPut(
                user,
                flowcell=self.flow_cell.sodar_uuid,
                message=self.sent_message.sodar_uuid,
                data=self.sent_message_api_post_data,
            )
            self.response_403()

    def testUpdateAccessAllowed(self):
        """Test that updating messages via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPut(
                user,
                flowcell=self.flow_cell.sodar_uuid,
                message=self.sent_message.sodar_uuid,
                data=self.sent_message_api_post_data,
            )
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["subject"], self.sent_message_api_post_data["subject"])

    def testDelete(self):
        """Test that deleting messages via API works (with super user)"""
        self.assertEqual(Message.objects.count(), 2)
        response = self.runDelete(
            self.root, flowcell=self.flow_cell.sodar_uuid, message=self.sent_message.sodar_uuid
        )
        self.response_204(response)
        self.assertEqual(Message.objects.count(), 1)

    def testDeleteAccessDenied(self):
        """Test that deleting messages via API is denied if role assignment is missing"""
        self.assertEqual(Message.objects.count(), 2)
        self.runDelete(
            None, flowcell=self.flow_cell.sodar_uuid, message=self.sent_message.sodar_uuid
        )
        self.assertEqual(Message.objects.count(), 2)
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.assertEqual(Message.objects.count(), 2)
            self.runDelete(
                user, flowcell=self.flow_cell.sodar_uuid, message=self.sent_message.sodar_uuid
            )
            self.assertEqual(Message.objects.count(), 2)
            self.response_403()

    def testDeleteAccessAllowed(self):
        """Test that deleting messages via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            Message.objects.all().delete()
            message = self.make_message()
            self.assertEqual(Message.objects.count(), 1)
            response = self.runDelete(
                user, flowcell=self.flow_cell.sodar_uuid, message=message.sodar_uuid
            )
            self.response_204(response)
            self.assertEqual(Message.objects.count(), 0)
