"""The views for the sequencers app."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin

from .forms import SequencingMachineForm
from .models import SequencingMachine


class SequencingMachineListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display list of all SequencingMachine records"""

    template_name = "sequencers/sequencer_list.html"
    permission_required = "sequencers.view_data"

    model = SequencingMachine

    def get_queryset(self):
        return super().get_queryset().filter(project__sodar_uuid=self.kwargs["project"])


class SequencingMachineDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display detail of SequencingMachine records"""

    template_name = "sequencers/sequencer_detail.html"
    permission_required = "sequencers.view_data"

    model = SequencingMachine

    slug_url_kwarg = "sequencer"
    slug_field = "sodar_uuid"


class SequencingMachineCreateView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    CreateView,
):
    """Display list of all SequencingMachine records"""

    template_name = "sequencers/sequencer_create.html"
    permission_required = "sequencers.modify_data"

    model = SequencingMachine
    form_class = SequencingMachineForm

    def form_valid(self, form):
        """Automatically set the project property."""
        form.instance.project = self._get_project(self.request, self.kwargs)
        return super().form_valid(form)


class SequencingMachineUpdateView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    """Updating of SequencingMachine records"""

    template_name = "sequencers/sequencer_update.html"
    permission_required = "sequencers.modify_data"

    model = SequencingMachine
    form_class = SequencingMachineForm

    slug_url_kwarg = "sequencer"
    slug_field = "sodar_uuid"


class SequencingMachineDeleteView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DeleteView,
):
    """Deletion of SequencingMachine records"""

    template_name = "sequencers/sequencer_confirm_delete.html"
    permission_required = "sequencers.modify_data"

    model = SequencingMachine

    slug_url_kwarg = "sequencer"
    slug_field = "sodar_uuid"

    def get_success_url(self):
        return reverse(
            "sequencers:sequencer-list",
            kwargs={"project": self._get_project(self.request, self.kwargs).sodar_uuid},
        )
