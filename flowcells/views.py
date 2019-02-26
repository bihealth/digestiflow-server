"""The views for the flowcells app."""

import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import reverse, redirect, render
from django.template.defaultfilters import pluralize
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from filesfolders.models import File, Folder
from projectroles.plugins import get_backend_api
from projectroles.utils import build_secret
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin

from barcodes.models import BarcodeSetEntry
from digestiflow.utils import model_to_dict
from .forms import (
    FlowCellForm,
    MessageForm,
    FlowCellUpdateStatusForm,
    FlowCellSuppressWarningForm,
    FlowCellToggleWatchingForm,
    LibrarySuppressWarningForm,
)
from .models import (
    FlowCell,
    Message,
    MSG_STATE_DRAFT,
    MSG_STATE_SENT,
    pretty_range,
    Library,
    FLOWCELL_TAG_WATCHING,
    message_created,
    flow_cell_created,
    flow_cell_updated,
)
from .tasks import flowcell_update_error_caches


# TODO: need to provide query set by project?!


class FlowCellListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display list of all FlowCell records"""

    template_name = "flowcells/flowcell_list.html"
    permission_required = "flowcells.view_flowcell"

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
    permission_required = "flowcells.view_flowcell"

    model = FlowCell

    slug_url_kwarg = "flowcell"
    slug_field = "sodar_uuid"

    def render_to_response(self, *args, **kwargs):
        context = self.get_context_data()
        if context["object"].is_error_cache_update_pending():
            messages.info(
                self.request,
                "Error information is outdated but will be refreshed shortly. Try reloading from time to time "
                "until this message disappears.",
            )
            flowcell_update_error_caches.delay(context["object"].pk)
        return super().render_to_response(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        flowcell = result["object"]
        messages = flowcell.messages.filter(author=self.request.user, state=MSG_STATE_DRAFT)
        try:
            instance = messages.first()
        except Message.DoesNotExit:
            instance = Message()
        result["message_form"] = MessageForm(instance=instance)
        result["csv_v1"] = self._build_v1_csv(flowcell)
        result["csv_v2"] = self._build_v2_csv(flowcell)
        result["flowcell_libraries"] = self._get_libraries(flowcell)
        return result

    def _get_libraries(self, flowcell):
        if not hasattr(self, "_flowcell_libraries"):
            self._flowcell_libraries = {}
        if flowcell.sodar_uuid not in self._flowcell_libraries:
            self._flowcell_libraries[flowcell.sodar_uuid] = list(flowcell.libraries.all())
        return self._flowcell_libraries[flowcell.sodar_uuid]

    def _build_v1_csv(self, flowcell):
        rows = [
            [
                "FCID",
                "Lane",
                "SampleID",
                "SampleRef",
                "Index",
                "Description",
                "Control",
                "Recipe",
                "Operator",
                "SampleProject",
            ]
        ]
        recipe = "PE_Indexing" if flowcell.is_paired else "SE_indexing"
        for lib in self._get_libraries(flowcell):
            if lib.get_barcode_seq2():
                barcode = "{}-{}".format(lib.get_barcode_seq(), lib.get_barcode_seq2())
            else:
                barcode = lib.get_barcode_seq()
            for lane_no in sorted(lib.lane_numbers):
                rows.append(
                    [
                        flowcell.vendor_id,
                        lane_no,
                        lib.name,
                        lib.reference,
                        barcode,
                        "",
                        "N",  # not PhiX
                        recipe,
                        flowcell.operator,
                        "Project",
                    ]
                )
        return "\n".join("\t".join(map(str, row)) for row in rows)

    def _build_v2_csv(self, flowcell):
        date = flowcell.run_date.strftime("%y/%m/%d")
        rows = [
            ["[Header]"],
            ["IEMFileVersion", "4"],
            ["Investigator Name", flowcell.operator],
            ["Experiment Name", "Project"],
            ["Date", date],
            ["Workflow", "GenerateFASTQ"],
            ["Applications", "FASTQ Only"],
            ["Assay", "TruSeq HT"],
            ["Description", ""],
            [],
            ["[Reads]"],
        ]
        for tup in flowcell.get_planned_reads_tuples():
            if tup[1] == "T":
                rows.append([str(tup[0])])
        rows += [
            [],
            ["[Data]"],
            [
                "Lane",
                "Sample_ID",
                "Sample_Name",
                "Sample_Plate",
                "Sample_Well",
                "i7_Index_ID",
                "index",
                "Sample_Project",
                "Description",
            ],
        ]
        for lib in self._get_libraries(flowcell):
            for lane_no in sorted(lib.lane_numbers):
                rows.append(
                    [
                        lane_no,
                        lib.name,
                        "",
                        "",
                        "",
                        lib.barcode.name if lib.barcode else "",
                        lib.barcode.sequence if lib.barcode else "",
                        "Project",
                        "",
                    ]
                )
        return "\n".join(",".join(map(str, row)) for row in rows) + "\n"  # noqa


class FlowCellRecreateLibrariesMixin:
    """Mixin with functionality to recreate the libraries"""

    @transaction.atomic()
    def _update_libraries(self, flowcell, form):
        """Update libraries of ``flowcell`` record from JSON field.

        This method must be called within a transaction, of course.

        For now, we just recreate the library entries.
        """
        flowcell.libraries.all().delete()

        project_barcodes = BarcodeSetEntry.objects.filter(
            barcode_set__project=self.get_project(self.request, self.kwargs)
        )
        print(json.loads(form.cleaned_data["libraries_json"]))
        for rank, info in enumerate(json.loads(form.cleaned_data["libraries_json"])):
            if info["barcode"]:
                barcode = project_barcodes.get(sodar_uuid=info["barcode"])
            else:
                barcode = None
            if info["barcode2"]:
                barcode2 = project_barcodes.get(sodar_uuid=info["barcode2"])
            else:
                barcode2 = None
            flowcell.libraries.create(
                rank=rank,
                name=info["name"],
                project_id=info["project_id"],
                reference=info["reference"],
                barcode=barcode,
                barcode_seq=info["barcode_seq"],
                barcode2=barcode2,
                barcode_seq2=info["barcode_seq2"],
                lane_numbers=info["lane_numbers"],
                demux_reads=info["demux_reads"],
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
    permission_required = "flowcells.add_flowcell"

    model = FlowCell
    form_class = FlowCellForm

    @transaction.atomic
    def form_valid(self, form):
        """Automatically set the project property."""
        # Create the sequencing machine.
        form.instance.project = self.get_project(self.request, self.kwargs)
        result = super().form_valid(form)
        try:
            self._update_libraries(self.object, form)
        except Exception as e:
            messages.error(self.request, "Could not create libraries: %s" % e)
            return self.form_invalid(form)
        # Send out Emails.
        flow_cell_created(form.instance)
        # Register event with timeline.
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
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
    permission_required = "flowcells.change_flowcell"

    model = FlowCell
    form_class = FlowCellForm

    slug_url_kwarg = "flowcell"
    slug_field = "sodar_uuid"

    @transaction.atomic
    def form_valid(self, form):
        # Save form, get ``self.object``, ready for updating libraries.
        original = FlowCell.objects.get(pk=form.instance.pk)
        self.object = form.save()
        try:
            self._update_libraries(self.object, form)
        except Exception as e:
            messages.error(self.request, "Could not update libraries entries: %s" % e)
            return self.form_invalid(form)
        # Call into super class, store original object before saving.
        result = super().form_valid(form)
        # Send out Emails.
        flow_cell_updated(original, form.instance)
        # Register event with timeline.
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="flowcells",
                user=self.request.user,
                event_name="flowcell_update",
                description="update flowcell {flowcell}: {extra-flowcell_dict}",
                status_type="OK",
                extra_data={"flowcell_dict": model_to_dict(self.object)},
            )
            tl_event.add_object(obj=self.object, label="flowcell", name=self.object.get_full_name())
        return result


class FlowCellUpdateStatusView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    """Updating of FlowCell records, status field."""

    template_name = "flowcells/flowcell_update_status.html"
    permission_required = "flowcells.change_flowcell"

    model = FlowCell
    form_class = FlowCellUpdateStatusForm

    slug_url_kwarg = "flowcell"
    slug_field = "sodar_uuid"

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["attribute"] = self.kwargs["attribute"]
        return result

    def _is_render_full(self):
        return self.request.GET.get("render_full", "").lower() in ("true", "1")

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data()
        result["render_full"] = self._is_render_full()
        result["attribute"] = self.kwargs["attribute"]
        return result

    def form_invalid(self, form):
        """Show form again with errors in ``render_full`` mode, otherwise push errors into tags."""
        if self._is_render_full():
            return super().form_invalid(form)
        else:
            error_str = "; ".join(
                "%s: %s" % (field, ", ".join(list(errors))) for field, errors in form.errors.items()
            )
            return self._render_row({"errors": error_str})

    def form_valid(self, form):
        result = super().form_valid(form)
        if self._is_render_full():
            # Redirect to detail view
            return result
        else:
            return self._render_row()

    def _render_row(self, context_data={}):
        """Just render one row."""
        # Fresh rendering of the template row
        context = super().get_context_data()
        context["item"] = context["object"]
        context.update(context_data)
        return render(self.request, "flowcells/_flowcell_item.html", context)


class FlowCellToggleWatchingView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    """Updating of FlowCell records, tag ``FLOWCELL_TAG_WATCHING``."""

    permission_required = "flowcells.change_flowcell"
    template_name = "flowcells/flowcell_update_status.html"

    model = FlowCell
    form_class = FlowCellToggleWatchingForm

    slug_url_kwarg = "flowcell"
    slug_field = "sodar_uuid"

    def form_invalid(self, form):
        return self.form_valid(form)

    def form_valid(self, form):
        self._toggle_tag()
        return self._render_row()

    def _toggle_tag(self):
        flowcell = super().get_context_data()["object"]
        tags = flowcell.tags.filter(user=self.request.user, name=FLOWCELL_TAG_WATCHING)
        if tags.exists():
            tags.delete()
        else:
            flowcell.tags.create(user=self.request.user, name=FLOWCELL_TAG_WATCHING)

    def _render_row(self, context_data={}):
        """Just render one row."""
        # Fresh rendering of the template row
        context = super().get_context_data()
        context["item"] = context["object"]
        context.update(context_data)
        return render(self.request, "flowcells/_flowcell_item.html", context)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class FlowCellSuppressWarningView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    """Updating of FlowCell records lane suppress warnings fields."""

    template_name = "flowcells/flowcell_suppress_warning.html"
    permission_required = "flowcells.change_flowcell"

    model = FlowCell
    form_class = FlowCellSuppressWarningForm

    slug_url_kwarg = "flowcell"
    slug_field = "sodar_uuid"

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["warning"] = self.kwargs["warning"]
        return result

    def _kwarg_lanes(self):
        return list(sorted(map(int, self.kwargs["lanes"].split(","))))

    def _is_render_full(self):
        return self.request.GET.get("render_full", "").lower() in ("true", "1")

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data()
        result["render_full"] = self._is_render_full()
        result["warning"] = self.kwargs["warning"]
        result["selected_lanes"] = self._kwarg_lanes()
        field_name = "lanes_suppress_%s_warning" % self.kwargs["warning"]
        curr_lanes = getattr(result["object"], field_name)
        result["other_lanes"] = list(sorted(set(curr_lanes) - set(result["selected_lanes"])))
        result["return_to"] = self.request.GET.get("return_to")
        result["render"] = self.request.GET.get("render")
        return result

    def form_invalid(self, form):
        """Put errors into messages before redirecting to the view again"""
        error_str = "; ".join(
            "%s: %s" % (field, ", ".join(list(errors))) for field, errors in form.errors.items()
        )
        messages.error(self.request, error_str)
        return redirect(self.object.get_absolute_url() + "#index-stats")

    def _redirect_to(self, form):
        """Redirect to flow cell detail view, appropriate tab."""
        field_name = "lanes_suppress_%s_warning" % self.kwargs["warning"]
        lanes = getattr(form.instance, field_name)
        messages.success(
            self.request,
            "{} suppressions for {} {}".format(
                "Activated" if (set(self._kwarg_lanes()) & set(lanes)) else "Deactivated",
                pluralize(self._kwarg_lanes(), "lane,lanes"),
                pretty_range(self._kwarg_lanes()),
            ),
        )
        if self.request.GET.get("return_to", "properties") == "index-stats":
            suffix = "#index-stats"
        else:
            suffix = "#properties"
        return redirect(self.object.get_absolute_url() + suffix)

    def _render_row(self, context_data={}):
        """Just render one row."""
        context = self.get_context_data()
        context["item"] = context["object"]
        context.update(context_data)
        return render(self.request, "flowcells/_flowcell_item.html", context)

    def form_valid(self, form):
        super().form_valid(form)
        if self.request.GET.get("return_to"):
            return self._redirect_to(form)
        else:  # self.request.GET.get('return_to') == "flowcell-line"
            return self._render_row()


class LibrarySuppressWarningView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    """Updating of Library records, suppression of index warnings."""

    template_name = "flowcells/library_suppress_warning.html"
    permission_required = "flowcells.change_flowcell"

    model = Library
    form_class = LibrarySuppressWarningForm

    slug_url_kwarg = "library"
    slug_field = "sodar_uuid"

    def _is_render_full(self):
        return self.request.GET.get("render_full", "").lower() in ("true", "1")

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data()
        result["forloop_counter"] = self.request.GET.get("forloop_counter", "")
        result["render_full"] = self._is_render_full()
        result["barcode_no"] = self.kwargs["barcode_no"]
        if result["barcode_no"] == "1":
            result["other_barcode_no"] = "2"
            result["other_state"] = self.object.suppress_barcode2_not_observed_error
        else:
            result["other_barcode_no"] = "1"
            result["other_state"] = self.object.suppress_barcode1_not_observed_error
        return result

    def form_invalid(self, form):
        """Put errors into messages before redirecting to the view again"""
        error_str = "; ".join(
            "%s: %s" % (field, ", ".join(list(errors))) for field, errors in form.errors.items()
        )
        messages.error(self.request, error_str)
        return redirect(self.object.get_absolute_url() + "#sample-sheet")

    def _render_row(self, context_data={}):
        """Just render one row."""
        context = self.get_context_data()
        context["item"] = context["object"]
        context["render_full"] = self._is_render_full()
        context.update(context_data)
        return render(self.request, "flowcells/_library_item.html", context)

    def form_valid(self, form):
        super().form_valid(form)
        return self._render_row()


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
    permission_required = "flowcells.delete_flowcell"

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
                project=self.get_project(self.request, self.kwargs),
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
            kwargs={"project": self.get_project(self.request, self.kwargs).sodar_uuid},
        )


class MessageAttachmentHelpersMixin:
    """Mixin with helper functions for message attachments."""

    def _handle_attachment_removal(self, form):
        """Handle the removal of files."""
        num_removed = 0
        for name, field in form.fields.items():
            if not name.startswith("del_attachment_") or not field:
                continue  # no deletion field or not checked
            sodar_uuid = name[len("del_attachment_") :]
            try:
                form.instance.get_attachment_files().get(sodar_uuid=sodar_uuid).delete()
                num_removed += 1
            except File.DoesNotExist:
                pass  # swallow exception

    def _handle_file_uploads(self, message):
        """Handle file uploads, if any.

        Ensures to remove the file upload folder for this message.
        """
        project = self.get_project(self.request, self.kwargs)
        folder = self._get_attachment_folder(message)
        if not self.request.FILES:
            return
        for key in ("attachment1", "attachment2", "attachment3"):
            uploaded = self.request.FILES.get(key)
            if uploaded:
                counter = 0
                suffix = ""
                while folder.filesfolders_file_children.filter(name=uploaded.name + suffix):
                    counter += 1
                    suffix = " (%d)" % counter
                new_file = File(
                    name=uploaded.name + suffix,
                    project=project,
                    folder=folder,
                    owner=self.request.user,
                    secret=build_secret(),
                )
                content_file = ContentFile(uploaded.read())
                new_file.file.save(uploaded.name, content_file)
                new_file.save()

    def _get_attachment_folder(self, message):
        """Get the folder containing the attachments of this message."""
        project = self.get_project(self.request, self.kwargs)
        container = self._get_message_attachments_folder()
        message.attachment_folder = container.filesfolders_folder_children.get_or_create(
            name=message.sodar_uuid, owner=self.request.user, project=project, folder=container
        )[0]
        return message.attachment_folder

    def _get_message_attachments_folder(self):
        """Get folder containing all message attachments.

        On creation, the folder will be owned by the first created user that is a super user.
        """
        project = self.get_project(self.request, self.kwargs)
        try:
            return Folder.objects.get(project=project, name="Message Attachments")
        except Folder.DoesNotExist:
            # TODO: assumes there is a "first super user" created on installation, document requirement
            root = get_user_model().objects.filter(is_superuser=True).order_by("pk").first()
            return Folder.objects.create(project=project, name="Message Attachments", owner=root)


class MessageCreateView(
    MessageAttachmentHelpersMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    CreateView,
):
    """Creation of messages."""

    template_name = "flowcells/flowcell_detail.html"
    permission_required = "flowcells.add_message"

    model = Message
    form_class = MessageForm

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        # Enable directly going to the messages.
        result["message_mode"] = True
        # Get flow cell to display as the main "single" object.
        project = self.get_project(self.request, self.kwargs)
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
        project = self.get_project(self.request, self.kwargs)
        flow_cell = project.flowcell_set.get(sodar_uuid=self.kwargs["flowcell"])
        form.instance.flow_cell = flow_cell

        # Prevent "create" when there already is a draft.
        if flow_cell.messages.filter(author=self.request.user, state=MSG_STATE_DRAFT):
            form.add_error(None, "Cannot create message if draft already exists")
            return self.form_invalid(form)

        # Handle submission with "discard"
        if form.cleaned_data["submit"] == "discard":
            messages.success(self.request, "Your message draft has been discarded")
            return redirect(form.instance.flow_cell.get_absolute_url())

        # Handle submission with "save" or "send"
        form.save()
        self._handle_attachment_removal(form)
        self._handle_file_uploads(form.instance)
        if form.cleaned_data["submit"] == "save":
            form.instance.state = MSG_STATE_DRAFT
            form.save()
            messages.success(self.request, "Your message has been saved as a draft.")
            return super().form_valid(form)
        else:  # form.cleaned_data["submit"] == "send"
            form.instance.state = MSG_STATE_SENT
            form.save()
            message_created(form.instance)
            messages.success(self.request, "Your message has been successfully sent.")
            return redirect(flow_cell.get_absolute_url() + "#message-%s" % form.instance.sodar_uuid)


class MessageUpdateView(
    MessageAttachmentHelpersMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    """Updating of Message records"""

    template_name = "flowcells/flowcell_update.html"
    permission_required = "flowcells.change_message"

    model = Message
    form_class = MessageForm

    slug_url_kwarg = "message"
    slug_field = "sodar_uuid"

    def get_queryset(self):
        return Message.objects.filter(flow_cell__project=self.get_project())

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        # Enable directly going to the messages.
        result["message_mode"] = True
        # Get flow cell to display as the main "single" object.
        project = self.get_project(self.request, self.kwargs)
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
        original = Message.objects.get(pk=form.instance.pk)
        self._handle_attachment_removal(form)
        self._handle_file_uploads(form.instance)
        if form.cleaned_data["submit"] == "save":
            form.instance.state = MSG_STATE_DRAFT
            messages.success(self.request, "Your message has been saved as a draft.")
            return super().form_valid(form)
        else:  # form.cleaned_data["submit"] == "send"
            form.instance.state = MSG_STATE_SENT
            form.instance.save()
            if original.state == MSG_STATE_DRAFT:  # now is MSG_STATE_SENT
                message_created(form.instance)
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
    permission_required = "flowcells.delete_message"

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
