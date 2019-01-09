"""API Views for the sequencers app."""

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from digestiflow.utils import ProjectMixin
from ..models import SequencingMachine
from .serializers import SequencingMachineSerializer

# TODO: authorization still missing, need mixin for this!


class SequencingMachineCreateApiView(ProjectMixin, ListCreateAPIView):
    queryset = SequencingMachine.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SequencingMachineSerializer
    lookup_url_kwarg = "sequencer"
    lookup_field = "sodar_uuid"

    def get_queryset(self):
        return SequencingMachine.objects.filter(project=self.get_project())


class SequencingMachineUpdateDestroyApiView(ProjectMixin, RetrieveUpdateDestroyAPIView):
    queryset = SequencingMachine.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SequencingMachineSerializer
    lookup_url_kwarg = "sequencer"
    lookup_field = "sodar_uuid"

    def get_queryset(self):
        return SequencingMachine.objects.filter(project=self.get_project())


class SequencingMachineByVendorApiView(ProjectMixin, RetrieveAPIView):
    queryset = SequencingMachine.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SequencingMachineSerializer
    lookup_url_kwarg = "sequencer"
    lookup_field = "vendor_id"

    def get_queryset(self):
        return SequencingMachine.objects.filter(project=self.get_project())
