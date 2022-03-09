"""Models for managing sequencers in DigestiFlow."""

import uuid as uuid_object

from django.db import models
from django.db.models import Q
from django.urls import reverse

from projectroles.models import Project


#: Key value for machine model iSeq
MACHINE_MODEL_ISEQ = "iSeq"

#: Key value for machine model MiSeq
MACHINE_MODEL_MISEQ = "MiSeq"

#: Key value for machine model MiniSeq
MACHINE_MODEL_MINISEQ = "MiniSeq"

#: Key value for machine model NextSeq500
MACHINE_MODEL_NEXTSEQ500 = "NextSeq500"

#: Key value for machine model HiSeq1000
MACHINE_MODEL_HISEQ1000 = "HiSeq1000"

#: Key value for machine model HiSeq1500
MACHINE_MODEL_HISEQ1500 = "HiSeq1500"

#: Key value for machine model HiSeq2000
MACHINE_MODEL_HISEQ2000 = "HiSeq2000"

#: Key value for machine model HiSeq3000
MACHINE_MODEL_HISEQ3000 = "HiSeq3000"

#: Key value for machine model HiSeq4000
MACHINE_MODEL_HISEQ4000 = "HiSeq4000"

#: Key value for machine model NovaSeq6000
MACHINE_MODEL_NOVASEQ6000 = "NovaSeq6000"

#: Key value for 'other' machine models
MACHINE_MODEL_OTHER = "other"

#: Choices for machine models
MACHINE_MODELS = (
    (MACHINE_MODEL_ISEQ, "iSeq"),
    (MACHINE_MODEL_MISEQ, "MiSeq"),
    (MACHINE_MODEL_MINISEQ, "MiniSeq"),
    (MACHINE_MODEL_NEXTSEQ500, "NextSeq 500"),
    (MACHINE_MODEL_HISEQ1000, "HiSeq 1000"),
    (MACHINE_MODEL_HISEQ1500, "HiSeq 1500"),
    (MACHINE_MODEL_HISEQ2000, "HiSeq 2000"),
    (MACHINE_MODEL_HISEQ3000, "HiSeq 3000"),
    (MACHINE_MODEL_HISEQ4000, "HiSeq 4000"),
    (MACHINE_MODEL_NOVASEQ6000, "NovaSeq 6000"),
    (MACHINE_MODEL_OTHER, "Other"),  # be a bit more future proof
)

#: Key value for index workflow A
INDEX_WORKFLOW_A = "A"

#: Key value for index workflow B
INDEX_WORKFLOW_B = "B"

#: Choices for index workflows, determines whether the second index is read as reverse-complement or not for dual
#: indexing.  Could be inferred from the machine type but not doing so as we would have to know all machine types
#: at any time.
INDEX_WORKFLOWS = (
    (INDEX_WORKFLOW_A, "MiSeq, HiSeq 2000/2500, NovaSeq 6000"),
    (INDEX_WORKFLOW_B, "iSeq, MiniSeq, NextSeq, HiSeq 3000/4000, HiSeq X"),
)


class SequencingMachineManager(models.Manager):
    """Manager for custom table-level SequencingMachine queries"""

    def find(self, search_term, _keywords=None):
        """Return objects matching the query.

        :param search_term: Search term (string)
        :param keywords: Optional search keywords as key/value pairs (dict)
        :return: Python list of BaseFilesfolderClass objects
        """
        objects = super().get_queryset()
        objects = objects.filter(
            Q(vendor_id__icontains=search_term)
            | Q(label__icontains=search_term)
            | Q(description__icontains=search_term)
        )
        return objects


class SequencingMachine(models.Model):
    """Represent a sequencing machine instance"""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Machine SODAR UUID"
    )

    #: The project containing this sequencer.
    project = models.ForeignKey(
        Project, help_text="Project in which this objects belongs", on_delete=models.CASCADE
    )

    #: Vendor ID of the machine, reflected in file names and read names later on.
    vendor_id = models.CharField(
        db_index=True,
        max_length=100,
        help_text=(
            "The vendor (Illumina) assigned ID of your sequencer. "
            "E.g., the ID might be something like NB501234 for a NextSeq, or "
            "ST-K12345 for a HiSeq."
        ),
    )

    #: Human-readable label of the machine
    label = models.CharField(max_length=100, help_text='Assign a short name, e.g. "HiSeq #1".')

    #: Optional, short description of the machine
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Brief description of the machine, e.g., "HiSeq 4000 bought in 2015".',
    )

    #: The machine model to use
    machine_model = models.CharField(
        choices=MACHINE_MODELS, max_length=100, help_text="The model of the machine"
    )

    #: Number of slots in the machine
    slot_count = models.IntegerField(
        default=1,
        help_text="Maximal number of flow cells in one run, e.g. 1 for NextSeq, 2 for HiSeq 4000",
    )

    #: Workflow used for dual indexing
    dual_index_workflow = models.CharField(
        max_length=10,
        choices=INDEX_WORKFLOWS,
        default=INDEX_WORKFLOW_A,
        help_text="Workflow to use for dual indexing",
    )

    #: Search-enabled manager.
    objects = SequencingMachineManager()

    class Meta:
        ordering = ["vendor_id"]
        unique_together = ("project", "vendor_id")

    def get_absolute_url(self):
        """Return URL for displaying the sequencer details."""
        return reverse(
            "sequencers:sequencer-detail",
            kwargs={"project": self.project.sodar_uuid, "sequencer": self.sodar_uuid},
        )

    def __str__(self):
        return "SequencingMachine: %s%s" % (
            self.vendor_id,
            " (%s)" % self.label if self.label else "",
        )
