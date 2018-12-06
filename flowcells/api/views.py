"""API Views for the sequencers app."""

from django.shortcuts import get_object_or_404
from projectroles.views import ProjectPermissionMixin, APIPermissionMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from digestiflow.utils import ProjectMixin
from ..models import FlowCell
from .serializers import FlowCellSerializer

# TODO: authorization still missing, need mixin for this!


class FlowCellCreateApiView(ProjectMixin, ListCreateAPIView):
    queryset = FlowCell.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = FlowCellSerializer
    lookup_field = "flowcell"
    permission_required = "flowcells.modify_data"

    def perform_create(self, serializer):
        serializer.save(project=self.get_project())


class FlowCellUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):
    queryset = FlowCell.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = FlowCellSerializer
    lookup_field = "flowcell"
    permission_required = "flowcells.modify_data"


class FlowCellResolveApiView(ModelViewSet):
    """Resolve flow cell attributes to UUID"""

    queryset = FlowCell.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = FlowCellSerializer
    lookup_field = "flowcell"
    permission_required = "flowcells.modify_data"

    def resolve(self, request, project, instrument_id, run_no, flowcell_id):
        flowcell = get_object_or_404(
            self.queryset,
            sequencing_machine__vendor_id=instrument_id,
            run_number=run_no,
            vendor_id=flowcell_id,
        )
        # Because this does not fit list_route or detail_route, we have to check permissions manually.
        return Response(self.get_serializer(flowcell).data)
