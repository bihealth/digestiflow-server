# TODO: check timeline events

from django.shortcuts import reverse
from test_plus.test import TestCase

from sequencers.models import INDEX_WORKFLOW_A, MACHINE_MODEL_HISEQ2000, SequencingMachine
from ..tests import (
    SetupUserMixin,
    SetupProjectMixin,
    SetupSequencingMachineMixin,
    AuthenticatedRequestMixin,
)


class SequencingMachineListViewTest(
    AuthenticatedRequestMixin,
    SetupSequencingMachineMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``SequencingMachineListView``"""

    def runGet(self, user, project=None):
        return super().runGet(
            user, "sequencers:sequencer-list", project=(project or self.project).sodar_uuid
        )

    def testGet(self):
        """Test that rendering the machine list works (with super user)"""
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


class SequencingMachineDetailViewTest(
    AuthenticatedRequestMixin,
    SetupSequencingMachineMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``SequencingMachineDetailView``"""

    def runGet(self, user, project=None):
        return super().runGet(
            user,
            "sequencers:sequencer-detail",
            project=(project or self.project).sodar_uuid,
            sequencer=self.hiseq2000.sodar_uuid,
        )

    def testGet(self):
        """Test that rendering the machine list works (with super user)"""
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


class SequencingMachineCreateViewTest(
    AuthenticatedRequestMixin,
    SetupSequencingMachineMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``SequencingMachineCreateView``"""

    url_name = "sequencers:sequencer-create"

    def setUp(self):
        super().setUp()
        self.form_data = {
            "vendor_id": "Hzzzzzzzz",
            "label": "Another test machine",
            "machine_model": MACHINE_MODEL_HISEQ2000,
            "slot_count": 2,
            "dual_index_workflow": INDEX_WORKFLOW_A,
        }

    def runGet(self, user, project=None):
        return super().runGet(user, self.url_name, project=(project or self.project).sodar_uuid)

    def runPost(self, user, data, project=None):
        return super().runPost(
            user, self.url_name, project=(project or self.project).sodar_uuid, data=data
        )

    def testGet(self):
        """Test that rendering the machine create form works (with super user)"""
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
        self.assertEqual(SequencingMachine.objects.count(), 1)
        response = self.runPost(self.root, self.form_data)
        self.assertRedirects(
            response,
            SequencingMachine.objects.order_by("-date_created").first().get_absolute_url(),
            fetch_redirect_response=False,
        )
        self.assertEqual(SequencingMachine.objects.count(), 2)

    def testPostAccessDenied(self):
        """Test that access is denied if necessary role assignment is missing"""
        for user in (self.norole, self.guest, None, self.unrelated_owner):
            self.assertEqual(SequencingMachine.objects.count(), 1)
            response = self.runPost(user, data=self.form_data)
            self.assertUnauthorizedRedirect(user, response)

    def testPostAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            SequencingMachine.objects.all().delete()
            response = self.runPost(user, data=self.form_data)
            self.assertEqual(SequencingMachine.objects.count(), 1)
            self.response_200(response)
            self.assertRedirects(
                response,
                SequencingMachine.objects.order_by("-date_created").first().get_absolute_url(),
                fetch_redirect_response=False,
            )


class SequencingMachineUpdateViewTest(
    AuthenticatedRequestMixin,
    SetupSequencingMachineMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``SequencingMachineUpdateView``"""

    url_name = "sequencers:sequencer-update"

    def setUp(self):
        super().setUp()
        self.form_data = {
            "vendor_id": "Haaaaaaaa",
            "label": "UPDATED",
            "machine_model": MACHINE_MODEL_HISEQ2000,
            "slot_count": 2,
            "dual_index_workflow": INDEX_WORKFLOW_A,
        }

    def runGet(self, user, project=None):
        return super().runGet(
            user,
            self.url_name,
            project=(project or self.project).sodar_uuid,
            sequencer=self.hiseq2000.sodar_uuid,
        )

    def runPost(self, user, data, project=None):
        return super().runPost(
            user,
            self.url_name,
            project=(project or self.project).sodar_uuid,
            sequencer=self.hiseq2000.sodar_uuid,
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
        self.assertEqual(SequencingMachine.objects.count(), 1)
        response = self.runPost(self.root, self.form_data)
        self.assertRedirects(
            response,
            SequencingMachine.objects.order_by("-date_created").first().get_absolute_url(),
            fetch_redirect_response=False,
        )
        self.assertEqual(SequencingMachine.objects.count(), 1)
        instrument = SequencingMachine.objects.first()
        self.assertEqual(instrument.vendor_id, self.form_data["vendor_id"])
        self.assertEqual(instrument.label, self.form_data["label"])

    def testPostAccessDenied(self):
        """Test that access is denied if necessary role assignment is missing"""
        for user in (self.norole, self.guest, None):
            self.assertEqual(SequencingMachine.objects.count(), 1)
            response = self.runPost(user, data=self.form_data)
            self.assertUnauthorizedRedirect(user, response)
        # Members of unrelated projects should not be able to see the object in their project...
        self.runPost(self.unrelated_owner, data=self.form_data, project=self.unrelated_project)
        self.response_404()

    def testPostAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runPost(user, data=self.form_data)
            self.assertEqual(SequencingMachine.objects.count(), 1)
            self.response_200(response)
            self.assertRedirects(
                response,
                SequencingMachine.objects.order_by("-date_created").first().get_absolute_url(),
                fetch_redirect_response=False,
            )


class SequencingMachineDeleteViewTest(
    AuthenticatedRequestMixin,
    SetupSequencingMachineMixin,
    SetupProjectMixin,
    SetupUserMixin,
    TestCase,
):
    """Test the ``SequencingMachineDeleteView``"""

    url_name = "sequencers:sequencer-delete"

    def setUp(self):
        super().setUp()

    def runGet(self, user, sequencer, project=None):
        return super().runGet(
            user,
            self.url_name,
            project=(project or self.project).sodar_uuid,
            sequencer=sequencer.sodar_uuid,
        )

    def runPost(self, user, sequencer, project=None):
        return super().runPost(
            user,
            self.url_name,
            project=(project or self.project).sodar_uuid,
            sequencer=sequencer.sodar_uuid,
        )

    def testGet(self):
        """Test that rendering the machine update form works (with super user)"""
        response = self.runGet(self.root, self.hiseq2000)
        self.response_200(response)
        self.assertInContext("project")
        self.assertInContext("object")

    def testGetAccessDenied(self):
        """Test that access is denied if role assignment is missing"""
        for user in (self.guest, self.norole, None):
            response = self.runGet(user, self.hiseq2000)
            self.assertUnauthorizedRedirect(user, response)
        # Members of unrelated projects should not be able to see the object in their project...
        self.runGet(self.unrelated_owner, sequencer=self.hiseq2000, project=self.unrelated_project)
        self.response_404()

    def testAccessAllowed(self):
        """Test that access is denied if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            response = self.runGet(user, self.hiseq2000)
            self.response_200(response)
            self.assertInContext("project")
            self.assertInContext("object")

    def testPost(self):
        """Test that the delete view works (with super user)"""
        self.assertEqual(SequencingMachine.objects.count(), 1)
        response = self.runPost(self.root, SequencingMachine.objects.first())
        self.assertEqual(SequencingMachine.objects.count(), 0)
        self.response_200(response)
        self.assertRedirects(
            response,
            reverse("sequencers:sequencer-list", kwargs={"project": self.project.sodar_uuid}),
            fetch_redirect_response=False,
        )

    def testPostAccessDenied(self):
        """Test that access is denied if necessary role assignment is missing"""
        for user in (self.norole, self.guest, None):
            SequencingMachine.objects.all().delete()
            self.make_machine()
            self.assertEqual(SequencingMachine.objects.count(), 1)
            response = self.runPost(user, SequencingMachine.objects.first())
            self.assertEqual(SequencingMachine.objects.count(), 1)
            self.assertUnauthorizedRedirect(user, response)
        # Members of unrelated projects should not be able to see the object in their project...
        SequencingMachine.objects.all().delete()
        self.make_machine()
        self.assertEqual(SequencingMachine.objects.count(), 1)
        response = self.runPost(
            self.unrelated_owner,
            sequencer=SequencingMachine.objects.first(),
            project=self.unrelated_project,
        )
        self.assertEqual(SequencingMachine.objects.count(), 1)
        self.response_404()

    def testPostAccessAllowed(self):
        """Test that access is allowed if role assignment is correct"""
        for user in (self.contributor, self.delegate, self.owner, self.root):
            SequencingMachine.objects.all().delete()
            self.make_machine()
            self.assertEqual(SequencingMachine.objects.count(), 1)
            response = self.runPost(user, SequencingMachine.objects.first())
            self.assertEqual(SequencingMachine.objects.count(), 0)
            self.response_200(response)
            self.assertRedirects(
                response,
                reverse("sequencers:sequencer-list", kwargs={"project": self.project.sodar_uuid}),
                fetch_redirect_response=False,
            )
