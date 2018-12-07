"""API Views for the sequencers app."""

from django.shortcuts import get_object_or_404
from projectroles.models import Project
from projectroles.views import ProjectPermissionMixin, APIPermissionMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from digestiflow.utils import ProjectMixin
from ..models import FlowCell, LaneIndexHistogram
from .serializers import FlowCellSerializer, LaneIndexHistogramSerializer

# TODO: authorization still missing, need mixin for this!


class FlowCellApiViewMixin(ProjectMixin):
    """Common behaviour of FlowCell API views."""

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["project"] = self.get_project()
        return result

    def get_queryset(self):
        return FlowCell.objects.filter(project=self.get_project())


class FlowCellListCreateApiView(FlowCellApiViewMixin, ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FlowCellSerializer
    permission_required = "flowcells.modify_data"


class FlowCellUpdateDestroyApiView(FlowCellApiViewMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FlowCellSerializer
    lookup_url_kwarg = "flowcell"
    lookup_field = "sodar_uuid"
    permission_required = "flowcells.modify_data"


class FlowCellResolveApiView(FlowCellApiViewMixin, ModelViewSet):
    """Resolve flow cell attributes to UUID"""

    permission_classes = (IsAuthenticated,)
    serializer_class = FlowCellSerializer
    lookup_field = "flowcell"
    permission_required = "flowcells.modify_data"

    def resolve(self, _request, project, instrument_id, run_no, flowcell_id):
        project = Project.objects.get(sodar_uuid=project)
        flowcell = get_object_or_404(
            FlowCell.objects.filter(project=project),
            sequencing_machine__vendor_id=instrument_id,
            run_number=run_no,
            vendor_id=flowcell_id,
        )
        # Because this does not fit list_route or detail_route, we have to check permissions manually.
        return Response(self.get_serializer(flowcell).data)


class LaneIndexHistogramApiViewMixin(ProjectMixin):
    """Common functionality for LaneIndexHistogram API views."""

    def get_flowcell(self):
        return FlowCell.objects.filter(project=self.get_project()).get(
            sodar_uuid=self.kwargs["flowcell"]
        )

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["project"] = self.get_project()
        result["flowcell"] = self.get_flowcell()
        return result

    def get_queryset(self):
        return LaneIndexHistogram.objects.filter(flowcell=self.get_flowcell())


class LaneIndexHistogramListCreateApiView(LaneIndexHistogramApiViewMixin, ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LaneIndexHistogramSerializer
    lookup_url_kwarg = "indexhistogram"
    lookup_field = "sodar_uuid"
    permission_required = "flowcells.modify_data"


class LaneIndexHistogramUpdateDestroyApiView(
    LaneIndexHistogramApiViewMixin, RetrieveUpdateDestroyAPIView
):
    permission_classes = (IsAuthenticated,)
    serializer_class = LaneIndexHistogramSerializer
    lookup_url_kwarg = "indexhistogram"
    lookup_field = "sodar_uuid"
    permission_required = "flowcells.modify_data"
