"""API Views for the flowcells app."""

from django.shortcuts import get_object_or_404
from projectroles.models import Project
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser

from digestiflow.utils import ProjectMixin, SodarObjectInProjectPermissions
from ..models import (
    FlowCell,
    LaneIndexHistogram,
    Message,
    flow_cell_created,
    flow_cell_updated,
    message_created,
    MSG_STATE_SENT,
    MSG_STATE_DRAFT,
)
from .serializers import (
    FlowCellSerializer,
    LaneIndexHistogramSerializer,
    MessageSerializer,
    AttachmentSerializer,
)

# TODO: authorization still missing, need mixin for this!


class FlowCellApiViewMixin(ProjectMixin):
    """Common behaviour of FlowCell API views."""

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["project"] = self.get_project()
        return result

    def get_queryset(self):
        return FlowCell.objects.filter(project=self.get_project()).prefetch_related(
            "index_histograms",
            "messages",
            "libraries",
            "libraries__barcode",
            "libraries__barcode__barcode_set",
            "libraries__barcode2",
            "libraries__barcode2__barcode_set",
        )


class FlowCellListCreateApiView(FlowCellApiViewMixin, ListCreateAPIView):
    permission_classes = (SodarObjectInProjectPermissions,)
    serializer_class = FlowCellSerializer

    def get_queryset(self):
        """Restrict flow cells to those with a sequencing, processing, or delivery state from query string.

        For this, the query parameters "sequencing_status", "conversion_status", and "delivery_status" are interpreted.
        """
        queryset = super().get_queryset().all()
        for token in ("sequencing", "conversion", "delivery"):
            key = "status_%s" % token
            status = self.request.query_params.get(key, None)
            if status:
                queryset = queryset.filter(**{key: status})
        return queryset

    def perform_create(self, serializer):
        super().perform_create(serializer)
        flow_cell_created(serializer.instance)


class FlowCellUpdateDestroyApiView(FlowCellApiViewMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (SodarObjectInProjectPermissions,)
    serializer_class = FlowCellSerializer
    lookup_url_kwarg = "flowcell"
    lookup_field = "sodar_uuid"

    def perform_update(self, serializer):
        original = FlowCell.objects.get(pk=serializer.instance.pk)
        super().perform_update(serializer)
        flow_cell_updated(original, serializer.instance)


class FlowCellResolveApiView(FlowCellApiViewMixin, ModelViewSet):
    """Resolve flow cell attributes to UUID"""

    permission_classes = (SodarObjectInProjectPermissions,)
    serializer_class = FlowCellSerializer

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
    permission_classes = (SodarObjectInProjectPermissions,)
    serializer_class = LaneIndexHistogramSerializer


class LaneIndexHistogramUpdateDestroyApiView(
    LaneIndexHistogramApiViewMixin, RetrieveUpdateDestroyAPIView
):
    permission_classes = (SodarObjectInProjectPermissions,)
    serializer_class = LaneIndexHistogramSerializer
    lookup_url_kwarg = "indexhistogram"
    lookup_field = "sodar_uuid"


class MessageApiViewMixin(ProjectMixin):
    """Common functionality for Message API views."""

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
        return Message.objects.filter(flow_cell=self.get_flowcell())


class MessageListCreateApiView(MessageApiViewMixin, ListCreateAPIView):
    permission_classes = (SodarObjectInProjectPermissions,)
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        message_created(serializer.instance)


class MessageUpdateDestroyApiView(MessageApiViewMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (SodarObjectInProjectPermissions,)
    serializer_class = MessageSerializer
    lookup_url_kwarg = "message"
    lookup_field = "sodar_uuid"

    def perform_update(self, serializer):
        original = Message.objects.get(pk=serializer.instance.pk)
        super().perform_update(serializer)
        if original.state == MSG_STATE_DRAFT and serializer.instance.state == MSG_STATE_SENT:
            message_created(serializer.instance)


class AttachmentApiViewMixin(ProjectMixin):
    """Common functionality for filesfolders File attachment API views."""

    def get_flowcell(self):
        return FlowCell.objects.filter(project=self.get_project()).get(
            sodar_uuid=self.kwargs["flowcell"]
        )

    def get_message(self):
        flow_cell = self.get_flowcell()
        return flow_cell.messages.get(sodar_uuid=self.kwargs["message"])

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["project"] = self.get_project()
        result["flowcell"] = self.get_flowcell()
        result["message"] = self.get_message()
        return result

    def get_queryset(self):
        return self.get_message().get_attachment_files()


class AttachmentListApiView(AttachmentApiViewMixin, ListCreateAPIView):
    parser_classes = (MultiPartParser,)
    permission_classes = (SodarObjectInProjectPermissions,)
    serializer_class = AttachmentSerializer


class AttachmentRetrieveApiView(AttachmentApiViewMixin, RetrieveUpdateDestroyAPIView):
    parser_classes = (MultiPartParser,)
    permission_classes = (SodarObjectInProjectPermissions,)
    serializer_class = AttachmentSerializer
    lookup_url_kwarg = "file"
    lookup_field = "sodar_uuid"
