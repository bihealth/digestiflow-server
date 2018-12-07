"""Serializers for the sequencers app."""

from rest_framework import serializers

from ..models import BarcodeSet, BarcodeSetEntry


class BarcodeSetSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        validated_data["project"] = self.context["project"]
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data["project"] = self.context["project"]
        return super().create(validated_data)

    class Meta:
        model = BarcodeSet
        fields = ("sodar_uuid", "name", "short_name", "description", "set_type")
        read_only_fields = ("sodar_uuid", "entries")


class BarcodeSetEntrySerializer(serializers.ModelSerializer):
    barcode_set = serializers.ReadOnlyField(source="barcode_set.sodar_uuid")

    def update(self, instance, validated_data):
        validated_data["barcode_set"] = self.context["barcode_set"]
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data["barcode_set"] = self.context["barcode_set"]
        return super().create(validated_data)

    class Meta:
        model = BarcodeSetEntry
        fields = ("sodar_uuid", "barcode_set", "name", "sequence")
        read_only_fields = ("sodar_uuid", "barcode_set")
