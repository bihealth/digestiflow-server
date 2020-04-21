"""Serializers for the fileboxes app."""

from rest_framework import serializers
from ..models import FileBox, FileBoxAccountGrant, FileBoxAuditEntry


class FileBoxAccountGrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileBoxAccountGrant
        fields = (
            "sodar_uuid",
            "username",
        )


class FileBoxAuditEntrySerializer(serializers.ModelSerializer):
    file_box = serializers.ReadOnlyField(source="file_box.sodar_uuid")

    def create(self, validated_data):
        validated_data["actor"] = self.context["request"].user
        validated_data["file_box"] = self.context["file_box"]
        return super().create(validated_data)

    class Meta:
        model = FileBoxAuditEntry
        fields = (
            "sodar_uuid",
            "file_box",
            "actor",
            "action",
            "message",
            "raw_log",
        )
        read_only_fields = (
            "sodar_uuid",
            "file_box",
            "actor",
        )


class FileBoxSerializer(serializers.ModelSerializer):
    project = serializers.ReadOnlyField(source="project.sodar_uuid")
    account_grants = FileBoxAccountGrantSerializer(many=True, read_only=True)

    def update(self, instance, validated_data):
        if instance.state_data != validated_data.get("state_data"):
            instance.update_state_meta(
                self.context["request"].user, "state_data", validated_data.get("state_data")
            )
        return super().update(instance, validated_data)

    class Meta:
        model = FileBox
        fields = (
            "sodar_uuid",
            "project",
            "title",
            "description",
            "date_frozen",
            "date_expiry",
            "state_meta",
            "state_data",  # only writeable field
            "account_grants",
        )
        read_only_fields = (
            "sodar_uuid",
            "project",
            "title",
            "description",
            "date_frozen",
            "date_expiry",
            "state_meta",
            "account_grants",
        )
