"""Serializers for the sequencers app."""

import functools

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from filesfolders.models import File, Folder

from sequencers.models import SequencingMachine
from ..models import FlowCell, LaneIndexHistogram, Library, Message


class LaneIndexHistogramSerializer(serializers.ModelSerializer):
    flowcell = serializers.ReadOnlyField(source="flowcell.sodar_uuid")

    def create(self, validated_data):
        validated_data["flowcell"] = self.context["flowcell"]
        try:
            instance = self.context["flowcell"].index_histograms.get(
                lane=validated_data["lane"], index_read_no=validated_data["index_read_no"]
            )
        except LaneIndexHistogram.DoesNotExist:
            return super().create(validated_data)
        else:
            return self.update(instance, validated_data)

    class Meta:
        model = LaneIndexHistogram
        fields = ("sodar_uuid", "flowcell", "lane", "index_read_no", "sample_size", "histogram")
        read_only_fields = ("sodar_uuid", "flowcell")


class LibrarySerializer(serializers.ModelSerializer):
    flow_cell = serializers.ReadOnlyField(source="flowcell.sodar_uuid")
    barcode = serializers.ReadOnlyField(source="barcode.sodar_uuid")
    barcode2 = serializers.ReadOnlyField(source="barcode2.sodar_uuid")

    def update(self, instance, validated_data):
        validated_data["flowcell"] = self.context["flowcell"]
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data["flowcell"] = self.context["flowcell"]
        return super().create(validated_data)

    class Meta:
        model = Library
        fields = (
            "sodar_uuid",
            "flow_cell",
            "name",
            "reference",
            "barcode",
            "barcode_seq",
            "barcode2",
            "barcode_seq2",
            "lane_numbers",
        )
        read_only_fields = ("sodar_uuid", "flow_cell")


class MessageUuidSerializer(serializers.ModelSerializer):
    """Serialize a message into its UUID.

    Read only is implied.
    """

    def to_representation(self, value):
        return value.sodar_uuid

    class Meta:
        model = Message
        fields = ("sodar_uuid",)
        read_only_fields = ("sodar_uuid",)


class FileSerializer(serializers.ModelSerializer):
    """Serialization of files"""

    class Meta:
        model = Message
        fields = ("sodar_uuid",)
        read_only_fields = ("sodar_uuid",)


class MessageSerializer(serializers.ModelSerializer):
    """Full serializers for messages."""

    flow_cell = serializers.ReadOnlyField(source="flowcell.sodar_uuid")
    author = serializers.ReadOnlyField(source="user.username")
    attachment_files = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "sodar_uuid",
            "flow_cell",
            "author",
            "state",
            "subject",
            "body",
            "body_format",
            "tags",
            "attachment_files",
        )
        read_only_fields = ("sodar_uuid", "flow_cell", "tags", "attachment_files")

    def get_attachment_files(self, instance):
        return [
            {"sodar_uuid": a_file.sodar_uuid, "name": a_file.name}
            for a_file in instance.get_attachment_files()
        ]


class FlowCellSerializer(serializers.ModelSerializer):
    sequencing_machine = serializers.CharField(source="sequencing_machine.vendor_id")
    project = serializers.ReadOnlyField(source="project.sodar_uuid")
    demux_operator = serializers.ReadOnlyField(source="demux_operator.username")
    index_histograms = LaneIndexHistogramSerializer(many=True, read_only=True)
    libraries = LibrarySerializer(many=True, read_only=True)
    messages = MessageUuidSerializer(many=True)

    def update(self, instance, validated_data):
        validated_data["project"] = self.context["project"]
        sequencing_machine = validated_data.pop("sequencing_machine")
        sequencing_machine = get_object_or_404(
            SequencingMachine.objects.filter(project=self.context["project"]),
            vendor_id=sequencing_machine.get("vendor_id")
        )
        validated_data["sequencing_machine"] = sequencing_machine
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data["project"] = self.context["project"]
        sequencing_machine = validated_data.pop("sequencing_machine")
        sequencing_machine = get_object_or_404(
            SequencingMachine.objects.filter(project=self.context["project"]),
            vendor_id=sequencing_machine.get("vendor_id")
        )
        validated_data["sequencing_machine"] = sequencing_machine
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
            "libraries",
            "index_histograms",
            "messages",
        )
        read_only_fields = (
            "sodar_uuid",
            "project",
            "demux_operator",
            "libraries",
            "index_histograms",
            "messages",
        )


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializing filesfolders File objects as attachments"""

    def update(self, instance, validated_data):
        validated_data["project"] = self.context["project"]
        validated_data["folder"] = self.context["message"].attachment_folder
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data["project"] = self.context["project"]
        validated_data["folder"] = self.context["message"].attachment_folder
        # TODO: move the attachment folder stuff into the model!
        result = super().create(validated_data)
        self._get_attachment_folder(result)
        result.save()
        return result

    # TODO: remove the following two dupes from normal views

    @functools.lru_cache()
    def _get_attachment_folder(self, message):
        """Get the folder containing the attachments of this message."""
        project = self._get_project(self.request, self.kwargs)
        container = self._get_message_attachments_folder()
        message.attachment_folder = container.filesfolders_folder_children.get_or_create(
            name=message.sodar_uuid, owner=self.request.user, project=project, folder=container
        )[0]
        return message.attachment_folder

    @functools.lru_cache()
    def _get_message_attachments_folder(self):
        """Get folder containing all message attachments.

        On creation, the folder will be owned by the first created user that is a super user.
        """
        project = self._get_project(self.request, self.kwargs)
        try:
            return Folder.objects.get(project=project, name="Message Attachments")
        except Folder.DoesNotExist:
            # TODO: assumes there is a "first super user" created on installation, document requirement
            root = get_user_model().objects.filter(is_superuser=True).order_by("pk").first()
            return Folder.objects.create(project=project, name="Message Attachments", owner=root)

    class Meta:
        model = File
        fields = (
            "sodar_uuid",
            "name",
        )
        read_only_fields = ("sodar_uuid", "name")
