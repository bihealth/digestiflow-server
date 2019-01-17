"""The views for the barcodes app."""

import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from projectroles.plugins import get_backend_api
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin

from digestiflow.utils import model_to_dict, ProjectPermissionMixin
from .forms import BarcodeSetForm
from .models import BarcodeSet, BarcodeSetEntry


class BarcodeSetListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display list of all BarcodeSet records"""

    template_name = "barcodes/barcodeset_list.html"
    permission_required = "barcodes.view_barcodeset"

    model = BarcodeSet

    def get_queryset(self):
        return super().get_queryset().filter(project__sodar_uuid=self.kwargs["project"])


class BarcodeSetDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display detail of BarcodeSet records"""

    template_name = "barcodes/barcodeset_detail.html"
    permission_required = "barcodes.view_barcodeset"

    model = BarcodeSet

    slug_url_kwarg = "barcodeset"
    slug_field = "sodar_uuid"


class BarcodeSetCreateView(
    SuccessMessageMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    CreateView,
):
    """Display list of all BarcodeSet records"""

    success_message = "Barcode set successfully created."
    template_name = "barcodes/barcodeset_create.html"
    permission_required = "barcodes.add_barcodeset"

    model = BarcodeSet
    form_class = BarcodeSetForm

    @transaction.atomic
    def form_valid(self, form):
        # Properly set the reference to the current project.
        form.instance.project = self._get_project(self.request, self.kwargs)
        # Save form, get ``self.object``, ready for creating barcode set entries.
        self.object = form.save()
        for entry in json.loads(form.cleaned_data["entries_json"]):
            BarcodeSetEntry.objects.create(
                barcode_set=self.object, name=entry["name"], sequence=entry["sequence"]
            )
        # Call into super class.
        result = super().form_valid(form)
        # Register event with timeline.
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self._get_project(self.request, self.kwargs),
                app_name="barcodes",
                user=self.request.user,
                event_name="barcodeset_create",
                description="create barcodeset {barcodeset}: {extra-barcodeset_dict}",
                status_type="OK",
                extra_data={
                    "barcodeset_dict": {
                        **model_to_dict(self.object),
                        "entries": [model_to_dict(entry) for entry in self.object.entries.all()],
                    }
                },
            )
            tl_event.add_object(obj=self.object, label="barcodeset", name=self.object.name)
        return result


class BarcodeSetUpdateView(
    SuccessMessageMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    """Updating of BarcodeSet records"""

    success_message = "Barcode set successfully updated."
    template_name = "barcodes/barcodeset_update.html"
    permission_required = "barcodes.change_barcodeset"

    model = BarcodeSet
    form_class = BarcodeSetForm

    slug_url_kwarg = "barcodeset"
    slug_field = "sodar_uuid"

    @transaction.atomic
    def form_valid(self, form):
        # Save form, get ``self.object``, ready for updating barcode set entries.
        self.object = form.save()
        try:
            self._update_entries(self.object, form)
        except ProtectedError as e:  # pragma: no cover
            messages.error(self.request, "Could not update barcode set entries: %s" % e)
            return self.form_invalid(form)
        # Call into super class.
        result = super().form_valid(form)
        # Register event with timeline.
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self._get_project(self.request, self.kwargs),
                app_name="barcodes",
                user=self.request.user,
                event_name="barcodeset_update",
                description="update barcodeset {barcodeset}: {extra-barcodeset_dict}",
                status_type="OK",
                extra_data={
                    "barcodeset_dict": {
                        **model_to_dict(self.object),
                        "entries": [model_to_dict(entry) for entry in self.object.entries.all()],
                    }
                },
            )
            tl_event.add_object(obj=self.object, label="barcodeset", name=self.object.name)
        return result

    def _update_entries(self, barcode_set, form):
        """Update barcode set entries of ``barcode_set`` record from JSON field.

        This method must be called within a transaction, of course.

        The algorithm for matching them is also mirrored in the JavaScript and both need to be kept in sync.
        """
        # Existing entries and to-be-updated values by UUID.
        existing = {str(entry.sodar_uuid): entry for entry in barcode_set.entries.all()}
        updated = json.loads(form.cleaned_data["entries_json"])
        updated_by_uuid = {entry.get("uuid"): entry for entry in updated if entry.get("uuid")}
        # Delete and update existing.
        for entry in existing.values():
            if str(entry.sodar_uuid) not in updated_by_uuid:
                # Delete records from existing set that we don't find in updated records.
                entry.delete()
            else:
                # Update existing record.
                the_updated = updated_by_uuid[str(entry.sodar_uuid)]
                entry.name = the_updated["name"]
                entry.sequence = the_updated["sequence"]
                entry.save()
        # Add new records.
        for entry in updated:
            if not entry.get("uuid") or entry.get("uuid") not in existing:
                BarcodeSetEntry.objects.create(
                    name=entry["name"], sequence=entry["sequence"], barcode_set=barcode_set
                )


class BarcodeSetDeleteView(
    SuccessMessageMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DeleteView,
):
    """Deletion of BarcodeSet records"""

    success_message = "Barcode set successfully deleted."
    template_name = "barcodes/barcodeset_confirm_delete.html"
    permission_required = "barcodes.delete_barcodeset"

    model = BarcodeSet

    slug_url_kwarg = "barcodeset"
    slug_field = "sodar_uuid"

    @transaction.atomic
    def delete(self, *args, **kwargs):
        # Delete barcode set record.
        for entry in self.get_object().entries.all():
            entry.delete()
        result = super().delete(*args, **kwargs)
        # Register event with timeline.
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self._get_project(self.request, self.kwargs),
                app_name="barcodes",
                user=self.request.user,
                event_name="barcodeset_delete",
                description="delete barcodeset {barcodeset}: {extra-barcodeset_dict}",
                status_type="OK",
                extra_data={
                    "barcodeset_dict": {
                        **model_to_dict(self.object),
                        "entries": [model_to_dict(entry) for entry in self.object.entries.all()],
                    }
                },
            )
            tl_event.add_object(obj=self.object, label="barcodeset", name=self.object.name)
        return result

    def get_success_url(self):
        return reverse(
            "barcodes:barcodeset-list",
            kwargs={"project": self._get_project(self.request, self.kwargs).sodar_uuid},
        )
