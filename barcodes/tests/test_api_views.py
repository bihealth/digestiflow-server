# TODO: check timeline events

import json
from test_plus.test import APITestCase

from digestiflow.test_utils import SetupUserMixin, SetupProjectMixin, AuthenticatedRequestMixin
from ..models import BarcodeSet, BarcodeSetEntry
from ..tests import SetupBarcodeSetMixin


class BarcodeSetListCreateApiViewTest(
    SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, AuthenticatedRequestMixin, APITestCase
):
    """Tests for creation of barcode sets using REST API"""

    url_name = "api:barcodesets"

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
        response = self.runPost(self.root, data=self.barcode_set_api_post_data)
        self.response_201(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertIn("sodar_uuid", data)

    def testPostAccessDenied(self):
        """Test that creating machine via API is denied if role assignment is missing"""
        self.runPost(None, data=self.barcode_set_api_post_data)
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.runPost(user, data=self.barcode_set_api_post_data)
            self.response_403()

    def testPostAccessAllowed(self):
        """Test that creating machine via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPost(user, data=self.barcode_set_api_post_data)
            self.response_201(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertIn("sodar_uuid", data)
            BarcodeSet.objects.filter(sodar_uuid=data["sodar_uuid"]).delete()


class BarcodeSetUpdateApiViewTest(
    SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, AuthenticatedRequestMixin, APITestCase
):
    """Tests for detail view, update, delete of barcode sets using REST API"""

    url_name = "api:barcodesets"

    def testGet(self):
        """Test that querying API for the barcode set list works (with super user)"""
        response = self.runGet(self.root, barcodeset=self.barcode_set.sodar_uuid)
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["sodar_uuid"], str(self.barcode_set.sodar_uuid))

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        self.runGet(None, barcodeset=self.barcode_set.sodar_uuid)
        self.response_401()
        for user in (self.norole, self.unrelated_owner):
            self.runGet(user)
            self.response_403()

    def testGetAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user, barcodeset=self.barcode_set.sodar_uuid)
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["sodar_uuid"], str(self.barcode_set.sodar_uuid))

    def testUpdate(self):
        """Test that creating barcode set via API works (with super user)"""
        response = self.runPut(
            self.root, barcodeset=self.barcode_set.sodar_uuid, data=self.barcode_set_api_post_data
        )
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["short_name"], self.barcode_set_api_post_data["short_name"])

    def testUpdateAccessDenied(self):
        """Test that creating barcode set via API is denied if role assignment is missing"""
        self.runPut(
            None, barcodeset=self.barcode_set.sodar_uuid, data=self.barcode_set_api_post_data
        )
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.runPut(
                user, barcodeset=self.barcode_set.sodar_uuid, data=self.barcode_set_api_post_data
            )
            self.response_403()

    def testUpdateAccessAllowed(self):
        """Test that creating barcode set via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPut(
                user, barcodeset=self.barcode_set.sodar_uuid, data=self.barcode_set_api_post_data
            )
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["short_name"], self.barcode_set_api_post_data["short_name"])

    def testDelete(self):
        """Test that creating barcode set via API works (with super user)"""
        self.assertEqual(BarcodeSet.objects.count(), 1)
        response = self.runDelete(self.root, barcodeset=self.barcode_set.sodar_uuid)
        self.response_204(response)
        self.assertEqual(BarcodeSet.objects.count(), 0)

    def testDeleteAccessDenied(self):
        """Test that creating machine via API is denied if role assignment is missing"""
        self.assertEqual(BarcodeSet.objects.count(), 1)
        self.runDelete(None, barcodeset=self.barcode_set.sodar_uuid)
        self.assertEqual(BarcodeSet.objects.count(), 1)
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.assertEqual(BarcodeSet.objects.count(), 1)
            self.runDelete(user, barcodeset=self.barcode_set.sodar_uuid)
            self.assertEqual(BarcodeSet.objects.count(), 1)
            self.response_403()

    def testDeleteAccessAllowed(self):
        """Test that creating machine via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            BarcodeSet.objects.all().delete()
            barcode_set = self.make_barcode_set()
            self.assertEqual(BarcodeSet.objects.count(), 1)
            response = self.runDelete(user, barcodeset=barcode_set.sodar_uuid)
            self.response_204(response)
            self.assertEqual(BarcodeSet.objects.count(), 0)


class BarcodeSetEntryListCreateApiViewTest(
    SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, AuthenticatedRequestMixin, APITestCase
):
    """Tests for creation of barcode set entries using REST API"""

    url_name = "api:barcodesetentries"

    def testGet(self):
        """Test that querying API for the machine list works (with super user)"""
        response = self.runGet(self.root, barcodeset=self.barcode_set.sodar_uuid)
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(data), 1)

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        self.runGet(None, barcodeset=self.barcode_set.sodar_uuid)
        self.response_401()
        for user in (self.norole, self.unrelated_owner):
            self.runGet(user, barcodeset=self.barcode_set.sodar_uuid)
            self.response_403()

    def testGetAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user, barcodeset=self.barcode_set.sodar_uuid)
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(len(data), 1)

    def testPost(self):
        """Test that creating machine via API works (with super user)"""
        response = self.runPost(
            self.root,
            barcodeset=self.barcode_set.sodar_uuid,
            data=self.barcode_set_entry_api_post_data,
        )
        self.response_201(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertIn("sodar_uuid", data)

    def testPostAccessDenied(self):
        """Test that creating machine via API is denied if role assignment is missing"""
        self.runPost(
            None, barcodeset=self.barcode_set.sodar_uuid, data=self.barcode_set_entry_api_post_data
        )
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.runPost(
                user,
                barcodeset=self.barcode_set.sodar_uuid,
                data=self.barcode_set_entry_api_post_data,
            )
            self.response_403()

    def testPostAccessAllowed(self):
        """Test that creating machine via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPost(
                user,
                barcodeset=self.barcode_set.sodar_uuid,
                data=self.barcode_set_entry_api_post_data,
            )
            self.response_201(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertIn("sodar_uuid", data)
            BarcodeSetEntry.objects.filter(sodar_uuid=data["sodar_uuid"]).delete()


class BarcodeSetEntryUpdateDeleteApiViewTest(
    SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, AuthenticatedRequestMixin, APITestCase
):
    """Tests for update and delete action using REST API"""

    url_name = "api:barcodesetentries"

    def testGet(self):
        """Test that querying API for the barcode set list works (with super user)"""
        response = self.runGet(
            self.root,
            barcodeset=self.barcode_set.sodar_uuid,
            barcodesetentry=self.barcode_set_entry.sodar_uuid,
        )
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["sodar_uuid"], str(self.barcode_set_entry.sodar_uuid))

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        self.runGet(
            None,
            barcodeset=self.barcode_set.sodar_uuid,
            barcodesetentry=self.barcode_set_entry.sodar_uuid,
        )
        self.response_401()
        for user in (self.norole, self.unrelated_owner):
            self.runGet(
                user,
                barcodeset=self.barcode_set.sodar_uuid,
                barcodesetentry=self.barcode_set_entry.sodar_uuid,
            )
            self.response_403()

    def testGetAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(
                user,
                barcodeset=self.barcode_set.sodar_uuid,
                barcodesetentry=self.barcode_set_entry.sodar_uuid,
            )
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["sodar_uuid"], str(self.barcode_set_entry.sodar_uuid))

    def testUpdate(self):
        """Test that creating barcode set via API works (with super user)"""
        response = self.runPut(
            self.root,
            barcodeset=self.barcode_set.sodar_uuid,
            barcodesetentry=self.barcode_set_entry.sodar_uuid,
            data=self.barcode_set_entry_api_post_data,
        )
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["name"], self.barcode_set_entry_api_post_data["name"])

    def testUpdateAccessDenied(self):
        """Test that creating barcode set via API is denied if role assignment is missing"""
        self.runPut(
            None, barcodeset=self.barcode_set.sodar_uuid, data=self.barcode_set_entry_api_post_data
        )
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.runPut(
                user,
                barcodeset=self.barcode_set.sodar_uuid,
                barcodesetentry=self.barcode_set_entry.sodar_uuid,
                data=self.barcode_set_entry_api_post_data,
            )
            self.response_403()

    def testUpdateAccessAllowed(self):
        """Test that creating barcode set via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPut(
                user,
                barcodeset=self.barcode_set.sodar_uuid,
                barcodesetentry=self.barcode_set_entry.sodar_uuid,
                data=self.barcode_set_entry_api_post_data,
            )
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["name"], self.barcode_set_entry_api_post_data["name"])

    def testDelete(self):
        """Test that creating barcode set via API works (with super user)"""
        self.assertEqual(BarcodeSetEntry.objects.count(), 1)
        response = self.runDelete(
            self.root,
            barcodeset=self.barcode_set.sodar_uuid,
            barcodesetentry=self.barcode_set_entry.sodar_uuid,
        )
        self.response_204(response)
        self.assertEqual(BarcodeSetEntry.objects.count(), 0)

    def testDeleteAccessDenied(self):
        """Test that creating machine via API is denied if role assignment is missing"""
        self.assertEqual(BarcodeSetEntry.objects.count(), 1)
        self.runDelete(
            None,
            barcodeset=self.barcode_set.sodar_uuid,
            barcodesetentry=self.barcode_set_entry.sodar_uuid,
        )
        self.assertEqual(BarcodeSetEntry.objects.count(), 1)
        self.response_401()
        for user in (self.guest, self.norole, self.unrelated_owner):
            self.assertEqual(BarcodeSetEntry.objects.count(), 1)
            self.runDelete(
                user,
                barcodeset=self.barcode_set.sodar_uuid,
                barcodesetentry=self.barcode_set_entry.sodar_uuid,
            )
            self.assertEqual(BarcodeSetEntry.objects.count(), 1)
            self.response_403()

    def testDeleteAccessAllowed(self):
        """Test that creating machine via API is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            BarcodeSetEntry.objects.all().delete()
            barcode_set_entry = self.make_barcode_set_entry()
            self.assertEqual(BarcodeSetEntry.objects.count(), 1)
            response = self.runDelete(
                user,
                barcodeset=self.barcode_set.sodar_uuid,
                barcodesetentry=barcode_set_entry.sodar_uuid,
            )
            self.response_204(response)
            self.assertEqual(BarcodeSetEntry.objects.count(), 0)


class BarcodeSetEntryRetrieveApiViewTest(
    SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, AuthenticatedRequestMixin, APITestCase
):
    """Tests for retrieve action using REST API"""

    url_name = "api:barcodesetentries-retrieve"

    def testGet(self):
        """Test that querying API for the barcode set list works (with super user)"""
        response = self.runGet(self.root, barcodesetentry=self.barcode_set_entry.sodar_uuid)
        self.response_200(response)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["sodar_uuid"], str(self.barcode_set_entry.sodar_uuid))

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        self.runGet(None, barcodesetentry=self.barcode_set_entry.sodar_uuid)
        self.response_401()
        for user in (self.norole, self.unrelated_owner):
            self.runGet(user, barcodesetentry=self.barcode_set_entry.sodar_uuid)
            self.response_403()

    def testGetAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user, barcodesetentry=self.barcode_set_entry.sodar_uuid)
            self.response_200(response)
            data = json.loads(response.content.decode("utf-8"))
            self.assertEqual(data["sodar_uuid"], str(self.barcode_set_entry.sodar_uuid))
