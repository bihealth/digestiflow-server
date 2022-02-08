"""Models for managing barcode sets and barcodes in DigestiFlow."""

import re
import uuid as uuid_object

from django.apps import apps
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField
from projectroles.models import Project


def revcomp(s):
    """Reverse complement function"""
    comp_map = {"A": "T", "a": "t", "C": "G", "c": "g", "g": "c", "G": "C", "T": "A", "t": "a"}
    return "".join(reversed([comp_map.get(x, x) for x in s]))


class BarcodeSetManager(models.Manager):
    """Manager for custom table-level BarcodeSet queries"""

    def find(self, search_term, _keywords=None):
        """Return objects matching the query.

        :param search_term: Search term (string)
        :param keywords: Optional search keywords as key/value pairs (dict)
        :return: Python list of BaseFilesfolderClass objects
        """
        objects = super().get_queryset().order_by("name")
        objects = objects.filter(
            Q(name__icontains=search_term)
            | Q(short_name__icontains=search_term)
            | Q(description__icontains=search_term)
        )
        return objects


#: Generic barcode set.
BARCODE_SET_GENERIC = "generic"

#: 10x genomics convention
BARCODE_SET_10X_GENOMICS = "10x_genomics"

#: Choices for barcode sets and barcodes.
BARCODE_SET_TYPES = (
    (BARCODE_SET_GENERIC, "generic"),
    (BARCODE_SET_10X_GENOMICS, "10x Genomics convention"),
)


class BarcodeSet(models.Model):
    """A set of ``BarcodeSet`` records."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Barcodeset SODAR UUID"
    )

    #: The project containing this barcode set.
    project = models.ForeignKey(
        Project, help_text="Project in which this objects belongs", on_delete=models.CASCADE,
    )

    #: Full name of the index set
    name = models.CharField(max_length=100, help_text="Full name of the barcode adapter set")

    #: Short, unique identifier of the barcode index set
    short_name = models.CharField(
        max_length=100, db_index=True, help_text="Short, unique identifier of barcode adapter set"
    )

    #: Optional, short description of the barcode set, including copyright
    #: notices etc.
    description = models.TextField(
        blank=True, null=True, help_text="Short description of the barcode set."
    )

    #: The barcode set type (e.g., for 10x convention).
    set_type = models.CharField(
        max_length=100,
        choices=BARCODE_SET_TYPES,
        default=BARCODE_SET_GENERIC,
        help_text="Type of barcode set.",
    )

    def get_absolute_url(self):
        return reverse(
            "barcodes:barcodeset-detail",
            kwargs={"project": self.project.sodar_uuid, "barcodeset": self.sodar_uuid},
        )

    def get_flowcells(self):
        flowcell_model = apps.get_model("flowcells.FlowCell")
        return flowcell_model.objects.filter(
            Q(libraries__barcode__barcode_set__id=self.id)
            | Q(libraries__barcode2__barcode_set__id=self.id)
        ).distinct()

    #: Search-enabled manager.
    objects = BarcodeSetManager()

    class Meta:
        ordering = ["name"]
        unique_together = ("project", "short_name")

    def __str__(self):
        return "{} ({})".format(self.name, self.short_name)


class BarcodeSetEntryManager(models.Manager):
    """Manager for custom table-level ``BarcodeSetEntry`` queries"""

    def find(self, search_term, _keywords=None):
        """Return objects matching the query.

        :param search_term: Search term (string)
        :param keywords: Optional search keywords as key/value pairs (dict)
        :return: Python list of BaseFilesfolderClass objects
        """
        objects = super().get_queryset().order_by("name")
        query = Q(name__icontains=search_term) | Q(sequence__icontains=search_term)
        if re.match(r"^[acgtnACGTN]+$", search_term):
            query = query | Q(sequence__icontains=revcomp(search_term))
        objects = objects.filter(query)
        return objects


class BarcodeSetEntry(models.Model):
    """A named barcode sequence in a ``BarcodeSet``."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Barcodeset SODAR UUID"
    )

    #: The barcode set that this barcode belongs to
    barcode_set = models.ForeignKey(BarcodeSet, related_name="entries", on_delete=models.CASCADE)

    #: Sample sheet line for custom ordering.
    rank = models.PositiveIntegerField(blank=True, null=True)

    #: The identifier of the adapter, e.g., 'AR001'.  This has to be unique in the context of the ``BarcodeSet``
    name = models.CharField(max_length=100, db_index=True, unique=False)

    #: Alternative names for the adapter (e.g., ['01', '1']), uniqueness also applies here in the context of the
    #: ``BarcodeSet``.
    aliases = ArrayField(models.CharField(max_length=100, db_index=True, unique=False), default=[])

    #: DNA sequence of the barcode.  In the case of dual indexing, use the sequence as for workflow A.
    sequence = models.CharField(max_length=200)

    #: Search-enabled manager.
    objects = BarcodeSetEntryManager()

    class Meta:
        ordering = ["barcode_set", "rank", "name"]

    def save(self, *args, **kwargs):
        """Version of save() that ensure uniqueness of the name within the ``BarcodeSet``."""
        self._validate_unique()
        super().save(*args, **kwargs)

    def _validate_unique(self):
        """Validates that the name and sequence are unique within the ``BarcodeSet``."""
        # TODO: validate alias uniueness
        for key in ("name", "sequence"):
            qs = BarcodeSetEntry.objects.filter(**{key: getattr(self, key)})
            if self.pk is not None:
                qs = qs.exclude(pk=self.pk)
            if qs.filter(barcode_set=self.barcode_set).exists():
                raise ValidationError(
                    "Barcode {} {} must be unique in barcode set!".format(key, getattr(self, key))
                )

    def get_absolute_url(self):
        """Return absolute URL to barcode set with highlight of barcode."""
        return (
            reverse(
                "barcodes:barcodeset-detail",
                kwargs={
                    "project": self.barcode_set.project.sodar_uuid,
                    "barcodeset": self.barcode_set.sodar_uuid,
                },
            )
            + "?barcode_set_entry=%s" % self.sodar_uuid
        )

    def __str__(self):
        return "{} ({})".format(self.name, self.sequence)
