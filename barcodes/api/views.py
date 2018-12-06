"""API Views for the sequencers app."""

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from digestiflow.utils import ProjectMixin
from ..models import BarcodeSet, BarcodeSetEntry
from .serializers import BarcodeSetSerializer, BarcodeSetEntrySerializer

# TODO: authorization still missing, need mixin for this!


class BarcodeSetCreateApiView(ProjectMixin, ListCreateAPIView):
    queryset = BarcodeSet.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = BarcodeSetSerializer
    lookup_field = "barcodeset"

    def perform_create(self, serializer):
        serializer.save(project=self.get_project())


class BarcodeSetUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):
    queryset = BarcodeSet.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = BarcodeSetSerializer
    lookup_field = "barcodeset"


class BarcodeSetEntryCreateApiView(ProjectMixin, ListCreateAPIView):
    queryset = BarcodeSetEntry.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = BarcodeSetEntrySerializer
    lookup_field = "barcodesetentry"

    def perform_create(self, serializer):
        serializer.save(project=self.get_project())


class BarcodeSetEntryUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):
    queryset = BarcodeSetEntry.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = BarcodeSetEntrySerializer
    lookup_field = "barcodesetentry"
