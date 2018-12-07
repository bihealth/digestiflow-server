"""Serializers for the sequencers app."""

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from sequencers.models import SequencingMachine
from ..models import FlowCell, LaneIndexHistogram


class LaneIndexHistogramSerializer(serializers.ModelSerializer):
    flowcell = serializers.ReadOnlyField(source="flowcell.sodar_uuid")

    def create(self, validated_data):
        validated_data["flowcell"] = self.context['flowcell']
        try:
            instance = self.context['flowcell'].index_histograms.get(
                lane=validated_data["lane"],
                index_read_no=validated_data["index_read_no"],
            )
        except LaneIndexHistogram.DoesNotExist:
            return super().create(validated_data)
        else:
            return self.update(instance, validated_data)

    class Meta:
        model = LaneIndexHistogram
        fields = ("sodar_uuid", "flowcell", "lane", "index_read_no", "sample_size", "histogram")
        read_only_fields = ("sodar_uuid", "flowcell",)


class FlowCellSerializer(serializers.ModelSerializer):
    sequencing_machine = serializers.CharField(source="sequencing_machine.vendor_id")
    project = serializers.ReadOnlyField(source="project.sodar_uuid")
    demux_operator = serializers.ReadOnlyField(source="demux_operator.username")
    index_histograms = LaneIndexHistogramSerializer(many=True, read_only=True)

    def update(self, instance, validated_data):
        validated_data["project"] = self.context['project']
        sequencing_machine = validated_data.pop('sequencing_machine')
        sequencing_machine = get_object_or_404(
            SequencingMachine, vendor_id=sequencing_machine.get('vendor_id'))
        validated_data['sequencing_machine'] = sequencing_machine
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data["project"] = self.context['project']
        sequencing_machine = validated_data.pop('sequencing_machine')
        sequencing_machine = get_object_or_404(
            SequencingMachine, vendor_id=sequencing_machine.get('vendor_id'))
        validated_data['sequencing_machine'] = sequencing_machine
        return super().create(validated_data)

    class Meta:
        model = FlowCell
        fields = (
            "sodar_uuid",
            "project",
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
            "index_histograms",
        )
        read_only_fields = ("sodar_uuid", "project", "demux_operator", "index_histograms")
