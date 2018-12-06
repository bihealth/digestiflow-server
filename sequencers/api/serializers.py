"""Serializers for the sequencers app."""

from rest_framework import serializers

from ..models import SequencingMachine


class SequencingMachineSerializer(serializers.ModelSerializer):
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
