"""The views for the flowcells app."""

import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from projectroles.plugins import get_backend_api
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin

from barcodes.models import BarcodeSetEntry
from digestiflow.utils import model_to_dict
from .forms import FlowCellForm
from .models import FlowCell


class FlowCellListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display list of all FlowCell records"""

    template_name = "flowcells/flowcell_list.html"
    permission_required = "flowcells.view_data"

    model = FlowCell

    def get_queryset(self):
        return super().get_queryset().filter(project__sodar_uuid=self.kwargs["project"])


class FlowCellDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display detail of FlowCell records"""

    template_name = "flowcells/flowcell_detail.html"
    permission_required = "flowcells.view_data"

    model = FlowCell

    slug_url_kwarg = "flowcell"
    slug_field = "sodar_uuid"


class FlowCellRecreateLibrariesMixin:
    """Mixin with functionality to recreate the libraries"""

    def _update_libraries(self, flowcell, form):
        """Update libraries of ``flowcell`` record from JSON field.

        This method must be called within a transaction, of course.

        For now, we just recreate the library entries.
        """
        flowcell.libraries.all().delete()

        project_barcodes = BarcodeSetEntry.objects.filter(
            barcode_set__project=self._get_project(self.request, self.kwargs)
        )
        for info in json.loads(form.cleaned_data["libraries_json"]):
            if info["barcode"]:
                barcode = project_barcodes.get(sodar_uuid=info["barcode"])
            else:
                barcode = None
            if info["barcode2"]:
                barcode2 = project_barcodes.get(sodar_uuid=info["barcode2"])
            else:
                barcode2 = None
            flowcell.libraries.create(
                name=info["name"],
                reference=info["reference"],
                barcode=barcode,
                barcode_seq=info["barcode_seq"],
                barcode2=barcode2,
                barcode_seq2=info["barcode_seq2"],
                lane_numbers=info["lane_numbers"],
            )


class FlowCellCreateView(
    FlowCellRecreateLibrariesMixin,
    SuccessMessageMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    CreateView,
):
    """Display list of all FlowCell records"""

    success_message = "Flow cell successfully created."
    template_name = "flowcells/flowcell_create.html"
    permission_required = "flowcells.modify_data"

    model = FlowCell
    form_class = FlowCellForm

    @transaction.atomic
    def form_valid(self, form):
        """Automatically set the project property."""
        # Create the sequencing machine.
        form.instance.project = self._get_project(self.request, self.kwargs)
        result = super().form_valid(form)
        try:
            self._update_libraries(self.object, form)
        except Exception as e:
            messages.error(self.request, "Could not create libraries: %s" % e)
            return self.form_invalid(form)
        # Register event with timeline.
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self._get_project(self.request, self.kwargs),
                app_name="flowcells",
                user=self.request.user,
                event_name="flowcell_create",
                description="create flowcell {flowcell}: {extra-flowcell_dict}",
                status_type="OK",
                extra_data={"flowcell_dict": model_to_dict(self.object)},
            )
            tl_event.add_object(obj=self.object, label="flowcell", name=self.object.get_full_name())
        return result


class FlowCellUpdateView(
    FlowCellRecreateLibrariesMixin,
    SuccessMessageMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    """Updating of FlowCell records"""

    success_message = "Flow cell successfully updated."
    template_name = "flowcells/flowcell_update.html"
    permission_required = "flowcells.modify_data"

    model = FlowCell
    form_class = FlowCellForm

    slug_url_kwarg = "flowcell"
    slug_field = "sodar_uuid"

    @transaction.atomic
    def form_valid(self, form):
        # Save form, get ``self.object``, ready for updating libraries.
        self.object = form.save()
        try:
            self._update_libraries(self.object, form)
        except Exception as e:
            messages.error(self.request, "Could not update libraries entries: %s" % e)
            return self.form_invalid(form)
        # Call into super class.
        result = super().form_valid(form)
        # Register event with timeline.
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self._get_project(self.request, self.kwargs),
                app_name="flowcells",
                user=self.request.user,
                event_name="flowcell_update",
                description="update flowcell {flowcell}: {extra-flowcell_dict}",
                status_type="OK",
                extra_data={"flowcell_dict": model_to_dict(self.object)},
            )
            tl_event.add_object(obj=self.object, label="flowcell", name=self.object.get_full_name())
        return result


class FlowCellDeleteView(
    SuccessMessageMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DeleteView,
):
    """Deletion of FlowCell records"""

    success_message = "Flow cell successfully deleted."
    template_name = "flowcells/flowcell_confirm_delete.html"
    permission_required = "flowcells.modify_data"

    model = FlowCell

    slug_url_kwarg = "flowcell"
    slug_field = "sodar_uuid"

    @transaction.atomic
    def delete(self, *args, **kwargs):
        # Delete sequencing machine record.
        result = super().delete(*args, **kwargs)
        # Register event with timeline.
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self._get_project(self.request, self.kwargs),
                app_name="flowcells",
                user=self.request.user,
                event_name="flowcell_delete",
                description="delete flowcell {flowcell}: {extra-flowcell_dict}",
                status_type="OK",
                extra_data={"flowcell_dict": model_to_dict(self.object)},
            )
            tl_event.add_object(obj=self.object, label="flowcell", name=self.object.get_full_name())
        return result

    def get_success_url(self):
        return reverse(
            "flowcells:flowcell-list",
            kwargs={"project": self._get_project(self.request, self.kwargs).sodar_uuid},
        )
