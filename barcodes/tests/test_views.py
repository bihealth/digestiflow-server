# TODO: check timeline events

from django.shortcuts import reverse
from test_plus.test import TestCase

from digestiflow.test_utils import SetupUserMixin, SetupProjectMixin, AuthenticatedRequestMixin
from ..models import BarcodeSet
from ..tests import SetupBarcodeSetMixin


class BarcodeSetListViewTest(
    AuthenticatedRequestMixin, SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, TestCase
):
    """Test the ``BarcodeSetListView``"""

    def runGet(self, user, project=None):
        return super().runGet(
            user, "barcodes:barcodeset-list", project=(project or self.project).sodar_uuid
        )

    def testGet(self):
        """Test that rendering the barcode set list works (with super user)"""
        response = self.runGet(self.root)
        self.response_200(response)

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        for user in (self.norole, None, self.unrelated_owner):
            response = self.runGet(user)
            self.assertUnauthorizedRedirect(user, response)

    def testAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user)
            self.response_200(response)
            self.assertInContext("project")
            self.assertInContext("object_list")


class BarcodeSetDetailViewTest(
    AuthenticatedRequestMixin, SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, TestCase
):
    """Test the ``BarcodeSetDetailView``"""

    def runGet(self, user, project=None):
        return super().runGet(
            user,
            "barcodes:barcodeset-detail",
            project=(project or self.project).sodar_uuid,
            barcodeset=self.barcode_set.sodar_uuid,
        )

    def testGet(self):
        """Test that rendering the barcode set detail works (with super user)"""
        response = self.runGet(self.root)
        self.response_200(response)
        self.assertInContext("project")
        self.assertInContext("object")

    def testAccessAllowed(self):
        """Test that access is denied if role assignment is correct"""
        for user in (self.guest, self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user)
            self.response_200(response)

    def testGetAccessDenied(self):
        """Test that access is allowed if role assignment is missing"""
        for user in (self.norole, None):
            response = self.runGet(user)
            self.assertUnauthorizedRedirect(user, response)
        # Members of unrelated projects should not be able to see the object in their project...
        self.runGet(self.unrelated_owner, self.unrelated_project)
        self.response_404()


class BarcodeSetCreateViewTest(
    AuthenticatedRequestMixin, SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, TestCase
):
    """Test the ``BarcodeSetCreateView``"""

    url_name = "barcodes:barcodeset-create"

    def setUp(self):
        super().setUp()

    def runGet(self, user, project=None):
        return super().runGet(user, self.url_name, project=(project or self.project).sodar_uuid)

    def runPost(self, user, data, project=None):
        return super().runPost(
            user, self.url_name, project=(project or self.project).sodar_uuid, data=data
        )

    def testGet(self):
        """Test that rendering the barcode set create form works (with super user)"""
        response = self.runGet(self.root)
        self.response_200(response)
        self.assertInContext("project")
        self.assertInContext("form")

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        for user in (self.guest, self.norole, None):
            response = self.runGet(user)
            self.assertUnauthorizedRedirect(user, response)

    def testAccessAllowed(self):
        """Test that access is denied if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user)
            self.response_200(response)
            self.assertInContext("project")
            self.assertInContext("form")

    def testPost(self):
        """Test that the create view works (with super user)"""
        self.assertEqual(BarcodeSet.objects.count(), 1)
        response = self.runPost(self.root, self.barcode_set_form_post_data)
        self.assertRedirects(
            response,
            BarcodeSet.objects.order_by("-date_created").first().get_absolute_url(),
            fetch_redirect_response=False,
        )
        self.assertEqual(BarcodeSet.objects.count(), 2)

    def testPostAccessDenied(self):
        """Test that access is denied if necessary role assignment is missing"""
        for user in (self.norole, self.guest, None, self.unrelated_owner):
            self.assertEqual(BarcodeSet.objects.count(), 1)
            response = self.runPost(user, data=self.barcode_set_form_post_data)
            self.assertUnauthorizedRedirect(user, response)

    def testPostAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            BarcodeSet.objects.all().delete()
            response = self.runPost(user, data=self.barcode_set_form_post_data)
            self.assertEqual(BarcodeSet.objects.count(), 1)
            self.response_200(response)
            self.assertRedirects(
                response,
                BarcodeSet.objects.order_by("-date_created").first().get_absolute_url(),
                fetch_redirect_response=False,
            )


class BarcodeSetUpdateViewTest(
    AuthenticatedRequestMixin, SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, TestCase
):
    """Test the ``BarcodeSetUpdateView``"""

    url_name = "barcodes:barcodeset-update"

    def setUp(self):
        super().setUp()

    def runGet(self, user, project=None):
        return super().runGet(
            user,
            self.url_name,
            project=(project or self.project).sodar_uuid,
            barcodeset=self.barcode_set.sodar_uuid,
        )

    def runPost(self, user, data, project=None):
        return super().runPost(
            user,
            self.url_name,
            project=(project or self.project).sodar_uuid,
            barcodeset=self.barcode_set.sodar_uuid,
            data=data,
        )

    def testGet(self):
        """Test that rendering the machine update form works (with super user)"""
        response = self.runGet(self.root)
        self.response_200(response)
        self.assertInContext("project")
        self.assertInContext("object")
        self.assertInContext("form")

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        for user in (self.guest, self.norole, None):
            response = self.runGet(user)
            self.assertUnauthorizedRedirect(user, response)
        # Members of unrelated projects should not be able to see the object in their project...
        self.runGet(self.unrelated_owner, self.unrelated_project)
        self.response_404()

    def testAccessAllowed(self):
        """Test that access is denied if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user)
            self.response_200(response)
            self.assertInContext("project")
            self.assertInContext("object")
            self.assertInContext("form")

    def testPost(self):
        """Test that the update view works (with super user)"""
        self.assertEqual(BarcodeSet.objects.count(), 1)
        response = self.runPost(self.root, self.barcode_set_form_post_data)
        self.assertRedirects(
            response,
            BarcodeSet.objects.order_by("-date_created").first().get_absolute_url(),
            fetch_redirect_response=False,
        )
        self.assertEqual(BarcodeSet.objects.count(), 1)
        barcodeset = BarcodeSet.objects.first()
        self.assertEqual(barcodeset.name, self.barcode_set_form_post_data["name"])
        self.assertEqual(barcodeset.short_name, self.barcode_set_form_post_data["short_name"])

    def testPostAccessDenied(self):
        """Test that access is denied if necessary role assignment is missing"""
        for user in (self.norole, self.guest, None):
            self.assertEqual(BarcodeSet.objects.count(), 1)
            response = self.runPost(user, data=self.barcode_set_form_post_data)
            self.assertUnauthorizedRedirect(user, response)
        # Members of unrelated projects should not be able to see the object in their project...
        self.runPost(
            self.unrelated_owner,
            data=self.barcode_set_form_post_data,
            project=self.unrelated_project,
        )
        self.response_404()

    def testPostAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPost(user, data=self.barcode_set_form_post_data)
            self.assertEqual(BarcodeSet.objects.count(), 1)
            self.response_200(response)
            self.assertRedirects(
                response,
                BarcodeSet.objects.order_by("-date_created").first().get_absolute_url(),
                fetch_redirect_response=False,
            )


class BarcodeSetDeleteViewTest(
    AuthenticatedRequestMixin, SetupBarcodeSetMixin, SetupProjectMixin, SetupUserMixin, TestCase
):
    """Test the ``BarcodeSetDeleteView``"""

    url_name = "barcodes:barcodeset-delete"

    def setUp(self):
        super().setUp()

    def runGet(self, user, barcodeset, project=None):
        return super().runGet(
            user,
            self.url_name,
            project=(project or self.project).sodar_uuid,
            barcodeset=barcodeset.sodar_uuid,
        )

    def runPost(self, user, barcodeset, project=None):
        return super().runPost(
            user,
            self.url_name,
            project=(project or self.project).sodar_uuid,
            barcodeset=barcodeset.sodar_uuid,
        )

    def testGet(self):
        """Test that rendering the machine update form works (with super user)"""
        response = self.runGet(self.root, self.barcode_set)
        self.response_200(response)
        self.assertInContext("project")
        self.assertInContext("object")

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        for user in (self.guest, self.norole, None):
            response = self.runGet(user, self.barcode_set)
            self.assertUnauthorizedRedirect(user, response)
        # Members of unrelated projects should not be able to see the object in their project...
        self.runGet(
            self.unrelated_owner, barcodeset=self.barcode_set, project=self.unrelated_project
        )
        self.response_404()

    def testAccessAllowed(self):
        """Test that access is denied if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user, self.barcode_set)
            self.response_200(response)
            self.assertInContext("project")
            self.assertInContext("object")

    def testPost(self):
        """Test that the delete view works (with super user)"""
        self.assertEqual(BarcodeSet.objects.count(), 1)
        response = self.runPost(self.root, BarcodeSet.objects.first())
        self.assertEqual(BarcodeSet.objects.count(), 0)
        self.response_200(response)
        self.assertRedirects(
            response,
            reverse("barcodes:barcodeset-list", kwargs={"project": self.project.sodar_uuid}),
            fetch_redirect_response=False,
        )

    def testPostAccessDenied(self):
        """Test that access is denied if necessary role assignment is missing"""
        for user in (self.norole, self.guest, None):
            BarcodeSet.objects.all().delete()
            self.make_barcode_set()
            self.assertEqual(BarcodeSet.objects.count(), 1)
            response = self.runPost(user, BarcodeSet.objects.first())
            self.assertEqual(BarcodeSet.objects.count(), 1)
            self.assertUnauthorizedRedirect(user, response)
        # Members of unrelated projects should not be able to see the object in their project...
        BarcodeSet.objects.all().delete()
        self.make_barcode_set()
        self.assertEqual(BarcodeSet.objects.count(), 1)
        response = self.runPost(
            self.unrelated_owner,
            barcodeset=BarcodeSet.objects.first(),
            project=self.unrelated_project,
        )
        self.assertEqual(BarcodeSet.objects.count(), 1)
        self.response_404(response)

    def testPostAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            BarcodeSet.objects.all().delete()
            self.make_barcode_set()
            self.assertEqual(BarcodeSet.objects.count(), 1)
            response = self.runPost(user, BarcodeSet.objects.first())
            self.assertEqual(BarcodeSet.objects.count(), 0)
            self.response_200(response)
            self.assertRedirects(
                response,
                reverse("barcodes:barcodeset-list", kwargs={"project": self.project.sodar_uuid}),
                fetch_redirect_response=False,
            )
