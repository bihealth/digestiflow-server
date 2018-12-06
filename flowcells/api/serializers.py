"""Serializers for the sequencers app."""

from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import serializers

from sequencers.models import SequencingMachine
from ..models import FlowCell


class FlowCellSerializer(serializers.ModelSerializer):
    sequencing_machine = serializers.CharField(source='sequencing_machine.vendor_id')
    demux_operator = serializers.ReadOnlyField(source="demux_operator.username")

    def create(self, validated_data):
        # TODO: query set for sequencing machine!
        sequencing_machine = validated_data.pop('sequencing_machine')
        sequencing_machine = get_object_or_404(
            SequencingMachine, vendor_id=sequencing_machine.get('vendor_id'))
        validated_data['sequencing_machine'] = sequencing_machine
        with transaction.atomic():
            return super().create(validated_data)

    class Meta:
        model = FlowCell
        fields = (
            "sodar_uuid",
            "run_date",
            "run_number",
            "slot",
            "vendor_id",
            "label",
            "manual_label",
            "description",
            "num_lanes",
            "operator",
            "rta_version",
            "status_sequencing",
            "status_conversion",
            "status_delivery",
            "delivery_type",
            "planned_reads",
            "current_reads",
            "barcode_mismatches",
            "sequencing_machine",
            "demux_operator",
        )
        read_only_fields = ("sodar_uuid", "demux_operator")
