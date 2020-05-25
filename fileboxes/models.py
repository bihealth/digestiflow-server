import datetime
import uuid as uuid_object

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from projectroles.models import Project

#: Shortcut to Django User model class.
from projectroles.plugins import get_backend_api

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class FileBoxManager(models.Manager):
    """Manager for custom table-level FileBox queries"""

    def find(self, search_term, keywords=None):
        """Return objects matching the query.

        :param search_term: Search term (string)
        :param keywords: Optional search keywords as key/value pairs (dict)
        :return: Python list of FileBox objects
        """
        objects = super().get_queryset()
        objects = objects.filter(
            Q(title__icontains=search_term) | Q(description__icontains=search_term)
        )
        return objects


#: Choices for the state of the meta data in the management.
CHOICES_STATE_META = (
    ("ACTIVE", "active (created)"),
    ("INACTIVE", "inactive (access blocked)"),
    ("DELETED", "deleted"),
)


#: Choices for the state of the data on the disk.
CHOICES_STATE_DATA = (
    ("ACTIVE", "active (created)"),
    ("INACTIVE", "inactive (access blocked)"),
    ("DELETING", "deleting"),
    ("DELETED", "deleted"),
)


def fourteen_days_in_the_future():
    return timezone.now() + datetime.timedelta(days=14)


def twenty_one_days_in_the_future():
    return timezone.now() + datetime.timedelta(days=21)


class FileBox(models.Model):
    """Information stored for each file exchange box."""

    #: Search-enabled manager.
    objects = FileBoxManager()

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="SODAR UUID")

    #: The project containing this file box.
    project = models.ForeignKey(Project, help_text="Project that this file box belongs to")

    #: Date when write access is lost.
    date_frozen = models.DateTimeField(null=False, blank=False, default=fourteen_days_in_the_future)
    #: Date when data is removed.
    date_expiry = models.DateTimeField(
        null=False, blank=False, default=twenty_one_days_in_the_future
    )

    #: The current state in the database.
    state_meta = models.CharField(
        max_length=32,
        null=False,
        blank=False,
        default="INITIAL",
        choices=CHOICES_STATE_META,
        help_text="State in the management system",
    )
    #: The current state in the file system.
    state_data = models.CharField(
        max_length=32, null=False, blank=False, default="INITIAL", choices=CHOICES_STATE_DATA
    )

    #: The title of the file box.
    title = models.CharField(max_length=200, null=False, blank=False, help_text="File box title")
    #: Additional description.
    description = models.TextField(
        null=True, blank=True, help_text="File box description; optional"
    )

    def update_state_meta(self, user, field, new_state):
        # Add audit trail event.
        self.audit_entries.create(
            actor=user,
            action="UPDATE_STATE",
            message="updated %s of file box '%s' from '%s' to '%s'"
            % (field, self.title, getattr(self, field), new_state),
        )
        # Register event with timeline.
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.project,
                app_name="fileboxes",
                user=user,
                event_name="filebox_update_state",
                description="updating state of file box {filebox}",
                status_type="OK",
            )
            tl_event.add_object(obj=self, label="filebox", name=self.title)

    def grant_list(self):
        return [grant.username for grant in self.account_grants.all()]

    def get_absolute_url(self):
        return reverse(
            "fileboxes:filebox-detail",
            kwargs={"project": self.project.sodar_uuid, "filebox": self.sodar_uuid},
        )

    class Meta:
        ordering = ("-date_created",)


#: Choices for the FileBoxAuditEntry.action field.
ACTION_CHOICES = (
    ("CREATE", "created"),
    ("ADD_MEMBER", "member added"),
    ("REMOVE_MEMBER", "member removed"),
    ("UPDATE_STATE", "state updated"),
    ("UPDATE_ATTRS", "attribute(s) updated"),  # non-state field(s)
    ("FS_APPLY_STATE", "state applied to file system"),
    ("FS_DATA_REMOVED", "all data removed from file system"),
)


class FileBoxAuditEntry(models.Model):
    """Audit trail entry for a FileBox record."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="SODAR UUID")

    file_box = models.ForeignKey(
        FileBox,
        related_name="audit_entries",
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        help_text="The file box that this audit entry belongs to",
    )
    actor = models.ForeignKey(
        AUTH_USER_MODEL,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        help_text="The actor in this audit trail entry",
    )
    action = models.TextField(
        null=False, blank=False, choices=ACTION_CHOICES, help_text="The action that was performed"
    )
    message = models.TextField(
        null=False, blank=False, help_text="The user-readable audit trail message"
    )
    raw_log = models.TextField(null=True, blank=True, help_text="Raw text output")

    def get_project(self):
        return self.file_box.project

    class Meta:
        ordering = ("-date_created",)


class FileBoxAccountGrant(models.Model):
    """An entry granting access to an account."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="SODAR UUID")

    file_box = models.ForeignKey(
        FileBox,
        related_name="account_grants",
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        help_text="The file box that this audit entry belongs to",
    )

    username = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        help_text="User name of the account that is granted access",
    )
    full_name = models.CharField(
        max_length=200, blank=True, null=True, help_text="Full name of the account's owner"
    )
    email = models.CharField(
        max_length=200, blank=True, null=True, help_text="Email of the account"
    )

    class Meta:
        ordering = ("username",)
