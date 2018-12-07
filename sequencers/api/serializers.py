"""Serializers for the sequencers app."""

from rest_framework import serializers

from ..models import SequencingMachine


class SequencingMachineSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        validated_data["project"] = self.context["project"]
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data["project"] = self.context["project"]
        return super().create(validated_data)

    class Meta:
        model = SequencingMachine
        fields = (
            "sodar_uuid",
            "vendor_id",
            "label",
            "description",
            "machine_model",
            "slot_count",
            "dual_index_workflow",
        )
