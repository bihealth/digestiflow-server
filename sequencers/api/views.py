"""API Views for the sequencers app."""

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from digestiflow.utils import ProjectMixin
from ..models import SequencingMachine
from .serializers import SequencingMachineSerializer

# TODO: authorization still missing, need mixin for this!


class SequencingMachineCreateApiView(ProjectMixin, ListCreateAPIView):
    queryset = SequencingMachine.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SequencingMachineSerializer
    lookup_field = "sequencer"

    def perform_create(self, serializer):
        serializer.save(project=self.get_project())


class SequencingMachineUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):
    queryset = SequencingMachine.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SequencingMachineSerializer
    lookup_field = "sequencer"
