# TODO: check timeline events

import json
from test_plus.test import APITestCase

from digestiflow.test_utils import SetupUserMixin, SetupProjectMixin, AuthenticatedRequestMixin
from ..models import SequencingMachine
from ..tests import SetupSequencingMachineMixin


class SequencingMachineListCreateApiViewTest(
    SetupSequencingMachineMixin,
    SetupProjectMixin,
    SetupUserMixin,
    AuthenticatedRequestMixin,
    APITestCase,
):
    """Tests for creation of sequencing machines using REST API"""

    url_name = "api:sequencers"

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
        response = self.runPost(self.root, data=self.post_data)
        self.response_201(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertIn("sodar_uuid", data)

    def testPostAccessDenied(self):
        """Test that creating machine via API is denied if role assignment is missing"""
        self.runPost(None, data=self.post_data)
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.runPost(user, data=self.post_data)
            self.response_403()

    def testPostAccessAllowed(self):
        """Test that creating machine via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPost(user, data=self.post_data)
            self.response_201(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertIn("sodar_uuid", data)
            SequencingMachine.objects.filter(sodar_uuid=data["sodar_uuid"]).delete()


class SequencingMachineUpdateApiViewTest(
    SetupSequencingMachineMixin,
    SetupProjectMixin,
    SetupUserMixin,
    AuthenticatedRequestMixin,
    APITestCase,
):
    """Tests for detail view, update, delete of sequencing machines using REST API"""

    url_name = "api:sequencers"

    def testGet(self):
        """Test that querying API for the machine list works (with super user)"""
        response = self.runGet(self.root, sequencer=self.hiseq2000.sodar_uuid)
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["sodar_uuid"], str(self.hiseq2000.sodar_uuid))

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        self.runGet(None, sequencer=self.hiseq2000.sodar_uuid)
        self.response_401()
        for user in (self.norole, self.unrelated_owner):
            self.runGet(user, sequencer=self.hiseq2000.sodar_uuid)
            self.response_403()

    def testGetAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user, sequencer=self.hiseq2000.sodar_uuid)
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["sodar_uuid"], str(self.hiseq2000.sodar_uuid))

    def testUpdate(self):
        """Test that creating machine via API works (with super user)"""
        response = self.runPut(self.root, sequencer=self.hiseq2000.sodar_uuid, data=self.post_data)
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["vendor_id"], self.post_data["vendor_id"])

    def testUpdateAccessDenied(self):
        """Test that creating machine via API is denied if role assignment is missing"""
        self.runPut(None, sequencer=self.hiseq2000.sodar_uuid, data=self.post_data)
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.runPut(user, sequencer=self.hiseq2000.sodar_uuid, data=self.post_data)
            self.response_403()

    def testUpdateAccessAllowed(self):
        """Test that creating machine via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPut(user, sequencer=self.hiseq2000.sodar_uuid, data=self.post_data)
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["vendor_id"], self.post_data["vendor_id"])

    def testDelete(self):
        """Test that creating machine via API works (with super user)"""
        self.assertEqual(SequencingMachine.objects.count(), 1)
        response = self.runDelete(self.root, sequencer=self.hiseq2000.sodar_uuid)
        self.response_204(response)
        self.assertEqual(SequencingMachine.objects.count(), 0)

    def testDeleteAccessDenied(self):
        """Test that creating machine via API is denied if role assignment is missing"""
        self.assertEqual(SequencingMachine.objects.count(), 1)
        self.runDelete(None, sequencer=self.hiseq2000.sodar_uuid)
        self.assertEqual(SequencingMachine.objects.count(), 1)
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.assertEqual(SequencingMachine.objects.count(), 1)
            self.runDelete(user, sequencer=self.hiseq2000.sodar_uuid)
            self.assertEqual(SequencingMachine.objects.count(), 1)
            self.response_403()

    def testDeleteAccessAllowed(self):
        """Test that creating machine via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            SequencingMachine.objects.all().delete()
            machine = self.make_machine()
            self.assertEqual(SequencingMachine.objects.count(), 1)
            response = self.runDelete(user, sequencer=machine.sodar_uuid)
            self.response_204(response)
            self.assertEqual(SequencingMachine.objects.count(), 0)


class SequencingMachineByVendorIdApiViewTest(
    SetupSequencingMachineMixin,
    SetupProjectMixin,
    SetupUserMixin,
    AuthenticatedRequestMixin,
    APITestCase,
):
    """Test that resolving sequencing machine by vendor ID works"""

    url_name = "api:sequencers"

    def testGet(self):
        """Test that querying API for the machine list works (with super user)"""
        response = self.runGet(self.root, sequencer=self.hiseq2000.vendor_id)
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["sodar_uuid"], str(self.hiseq2000.sodar_uuid))

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        self.runGet(None, sequencer=self.hiseq2000.vendor_id)
        self.response_401()
        for user in (self.norole, self.unrelated_owner):
            self.runGet(user)
            self.response_403()

    def testGetAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user, sequencer=self.hiseq2000.vendor_id)
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["sodar_uuid"], str(self.hiseq2000.sodar_uuid))
