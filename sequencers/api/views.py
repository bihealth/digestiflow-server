"""API Views for the ``sequencers`` app."""

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView

from digestiflow.utils import ProjectMixin, SodarObjectInProjectPermissions
from ..models import SequencingMachine
from .serializers import SequencingMachineSerializer


class SequencingMachineApiViewMixin(ProjectMixin):
    """Common behaviour of FlowCell API views."""

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["project"] = self.get_project()
        return result

    def get_queryset(self):
        return SequencingMachine.objects.filter(project=self.get_project())


class SequencingMachineCreateApiView(SequencingMachineApiViewMixin, ListCreateAPIView):
    queryset = SequencingMachine.objects.all()
    permission_classes = (SodarObjectInProjectPermissions,)
    serializer_class = SequencingMachineSerializer
    lookup_url_kwarg = "sequencer"
    lookup_field = "sodar_uuid"


class SequencingMachineUpdateDestroyApiView(
    SequencingMachineApiViewMixin, RetrieveUpdateDestroyAPIView
):
    queryset = SequencingMachine.objects.all()
    permission_classes = (SodarObjectInProjectPermissions,)
    serializer_class = SequencingMachineSerializer
    lookup_url_kwarg = "sequencer"
    lookup_field = "sodar_uuid"


class SequencingMachineByVendorApiView(SequencingMachineApiViewMixin, RetrieveAPIView):
    queryset = SequencingMachine.objects.all()
    permission_classes = (SodarObjectInProjectPermissions,)
    serializer_class = SequencingMachineSerializer
    lookup_url_kwarg = "sequencer"
    lookup_field = "vendor_id"
