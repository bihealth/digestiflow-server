"""Serializers for the sequencers app."""

from rest_framework import serializers

from ..models import BarcodeSet, BarcodeSetEntry


class BarcodeSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarcodeSet
        fields = ("sodar_uuid", "name", "short_name", "description", "set_type")
        read_only_fields = ("entries",)


class BarcodeSetEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = BarcodeSetEntry
        fields = ("sodar_uuid", "barcode_set", "name", "sequence")
