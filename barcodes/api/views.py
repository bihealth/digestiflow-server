"""API Views for the sequencers app."""

from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from digestiflow.utils import ProjectMixin
from ..models import BarcodeSet, BarcodeSetEntry
from .serializers import BarcodeSetSerializer, BarcodeSetEntrySerializer

# TODO: authorization still missing, need mixin for this!


class BarcodeSetViewMixin(ProjectMixin):
    """Common behaviour of BarcodeSet API views."""

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["project"] = self.get_project()
        return result

    def get_queryset(self):
        return BarcodeSet.objects.filter(project=self.get_project())


class BarcodeSetCreateApiView(BarcodeSetViewMixin, ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BarcodeSetSerializer
    permission_required = "barcodes.modify_data"

    def perform_create(self, serializer):
        serializer.save(project=self.get_project())


class BarcodeSetUpdateDestroyApiView(BarcodeSetViewMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BarcodeSetSerializer
    permission_required = "barcodes.modify_data"
    lookup_url_kwarg = "barcodeset"
    lookup_field = "sodar_uuid"


class BarcodeSetEntryApiViewMixin(ProjectMixin):
    """Common functionality for BarcodeSetEntry API views."""

    def get_barcode_set(self):
        return BarcodeSet.objects.filter(project=self.get_project()).get(
            sodar_uuid=self.kwargs["barcodeset"]
        )

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["project"] = self.get_project()
        result["barcode_set"] = self.get_barcode_set()
        return result

    def get_queryset(self):
        return BarcodeSetEntry.objects.filter(barcode_set=self.get_barcode_set())


class BarcodeSetEntryCreateApiView(BarcodeSetEntryApiViewMixin, ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BarcodeSetEntrySerializer
    lookup_url_kwarg = "barcodesetentry"
    lookup_field = "sodar_uuid"


class BarcodeSetEntryUpdateDestroyApiView(
    BarcodeSetEntryApiViewMixin, RetrieveUpdateDestroyAPIView
):
    permission_classes = (IsAuthenticated,)
    serializer_class = BarcodeSetEntrySerializer
    lookup_url_kwarg = "barcodesetentry"
    lookup_field = "sodar_uuid"


class BarcodeSetEntryRetrieveApiView(ProjectMixin, RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = BarcodeSetEntrySerializer
    lookup_url_kwarg = "barcodesetentry"
    lookup_field = "sodar_uuid"

    def get_queryset(self):
        return BarcodeSetEntry.objects.filter(barcode_set__project=self.get_project())
