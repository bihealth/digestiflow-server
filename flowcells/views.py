"""The views for the flowcells app."""

import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import reverse, redirect
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from projectroles.plugins import get_backend_api
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin

from barcodes.models import BarcodeSetEntry
from digestiflow.utils import model_to_dict
from .forms import FlowCellForm, MessageForm
from .models import FlowCell, Message, MSG_STATE_DRAFT, MSG_STATE_SENT


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

    @transaction.atomic()
    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        flowcell = result["object"]
        messages = flowcell.messages.filter(author=self.request.user, state=MSG_STATE_DRAFT)
        try:
            instance = messages.first()
        except Message.DoesNotExit:
            instance = Message()
        result["message_form"] = MessageForm(instance=instance)
        return result


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


class MessageCreateView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    CreateView,
):
    """Creation of messages."""

    template_name = "flowcells/flowcell_detail.html"
    permission_required = "flowcells.modify_data"

    model = Message
    form_class = MessageForm

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        # Enable directly going to the messages.
        result["message_mode"] = True
        # Get flow cell to display as the main "single" object.
        project = self._get_project(self.request, self.kwargs)
        flow_cell = project.flowcell_set.get(sodar_uuid=self.kwargs["flowcell"])
        result["object"] = flow_cell
        # Setup the model form, push draft message into it, if any.
        messages = flow_cell.messages.filter(author=self.request.user, state=MSG_STATE_DRAFT)
        try:
            instance = messages.first()
        except Message.DoesNotExit:
            instance = Message()
        result["message_form"] = MessageForm(instance=instance)
        return result

    @transaction.atomic
    def form_valid(self, form):
        # Automatically set the instance attributes for user and flow_cell.
        form.instance.author = self.request.user
        project = self._get_project(self.request, self.kwargs)
        flow_cell = project.flowcell_set.get(sodar_uuid=self.kwargs["flowcell"])
        form.instance.flow_cell = flow_cell

        # Prevent "create" when there already is a draft.
        if flow_cell.messages.filter(author=self.request.user, state=MSG_STATE_DRAFT):
            form.add_error(None, "Cannot create message if draft already exists")
            return self.form_invalid(form)

        # Handle submission with "discard"
        if form.cleaned_data["submit"] == "discard":
            message.success(self.request, "Your message draft has been discarded")
            return redirect(form.instance.flow_cell.get_absolute_url())

        # Handle submission with "save" or "send"
        if form.cleaned_data["submit"] == "save":
            form.instance.state = MSG_STATE_DRAFT
            messages.success(self.request, "Your message has been saved as a draft.")
            return super().form_valid(form)
        else:  # form.cleaned_data["submit"] == "send"
            form.instance.state = MSG_STATE_SENT
            form.save()
            messages.success(self.request, "Your message has been successfully sent.")
            return redirect(flow_cell.get_absolute_url() + "#message-%s" % form.instance.sodar_uuid)


class MessageUpdateView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    """Updating of Message records"""

    template_name = "flowcells/flowcell_update.html"
    permission_required = "flowcells.modify_data"

    model = Message
    form_class = MessageForm

    slug_url_kwarg = "message"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        # Enable directly going to the messages.
        result["message_mode"] = True
        # Get flow cell to display as the main "single" object.
        project = self._get_project(self.request, self.kwargs)
        flow_cell = project.flowcell_set.get(sodar_uuid=self.kwargs["flowcell"])
        result["object"] = flow_cell
        # Setup the model form, push draft message into it, if any.
        instance = flow_cell.messages.get(sodar_uuid=self.kwargs["message"])
        result["message_form"] = MessageForm(instance=instance)
        return result

    @transaction.atomic
    def form_valid(self, form):
        # Handle submission with "discard"
        if form.cleaned_data["submit"] == "discard":
            form.instance.delete()
            messages.success(self.request, "Your message draft has been discarded")
            return redirect(form.instance.flow_cell.get_absolute_url())

        # Handle submission with "save" or "send"
        if form.cleaned_data["submit"] == "save":
            form.instance.state = MSG_STATE_DRAFT
            messages.success(self.request, "Your message has been saved as a draft.")
            return super().form_valid(form)
        else:  # form.cleaned_data["submit"] == "send"
            form.instance.state = MSG_STATE_SENT
            form.instance.save()
            messages.success(self.request, "Your message has been successfully sent.")
            flow_cell = form.instance.flow_cell
            return redirect(flow_cell.get_absolute_url() + "#message-%s" % form.instance.sodar_uuid)


class MessageDeleteView(
    SuccessMessageMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DeleteView,
):
    """Deletion of Message records"""

    success_message = "Message has been successfully deleted."
    template_name = "flowcells/message_confirm_delete.html"
    permission_required = "flowcells.modify_data"

    model = Message

    slug_url_kwarg = "message"
    slug_field = "sodar_uuid"

    def get_queryset(self):
        flow_cell = FlowCell.objects.get(
            project__sodar_uuid=self.kwargs["project"], sodar_uuid=self.kwargs["flowcell"]
        )
        return flow_cell.messages

    def get_success_url(self):
        flow_cell = FlowCell.objects.get(
            project__sodar_uuid=self.kwargs["project"], sodar_uuid=self.kwargs["flowcell"]
        )
        return flow_cell.get_absolute_url() + "#message-top"
