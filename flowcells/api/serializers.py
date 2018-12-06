"""Serializers for the sequencers app."""

from rest_framework import serializers

from ..models import FlowCell


class FlowCellSerializer(serializers.ModelSerializer):
    sequencing_machine = serializers.ReadOnlyField(source="sequencing_machine.vendor_id")
    demux_operator = serializers.ReadOnlyField(source="demux_operator.username")

    class Meta:
        model = FlowCell
        fields = (
            "sodar_uuid",
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
        read_only_fields = ("sequencing_machine", "demux_operator")
