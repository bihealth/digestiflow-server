import uuid as uuid_object

from django.core.urlresolvers import reverse
from django.db import models
from projectroles.models import Project

from digestiflow.users.models import User
from sequencers.models import SequencingMachine


#: Status for "initial"/"not started", not automatically started yet for conversion.
STATUS_INITIAL = "initial"

#: Status for "ready to start"
STATUS_READY = "ready"

#: Status for "in progress"
STATUS_IN_PROGRESS = "in_progress"

#: Status for "complete" (automatic)
STATUS_COMPLETE = "complete"

#: Status for "complete_warnings" (manual)
STATUS_COMPLETE_WARNINGS = "complete_warnings"

#: Status for "failed" (automatic)
STATUS_FAILED = "failed"

#: Status for closed/released/receival confirmed (by user)
STATUS_CLOSED = "closed"

#: Status for confirmed failed/confirmed canceled (by user)
STATUS_CANCELED = "canceled"

#: Status for "skipped" (only used for conversion)
STATUS_SKIPPED = "skipped"

#: Statuses for sequencing
SEQUENCING_STATUS_CHOICES = (
    (STATUS_INITIAL, "not started"),
    (STATUS_IN_PROGRESS, "in progress"),
    (STATUS_COMPLETE, "complete"),
    (STATUS_COMPLETE_WARNINGS, "complete with warnings"),
    (STATUS_CLOSED, "released"),
    (STATUS_FAILED, "failed"),
    (STATUS_CANCELED, "failured confirmed"),
)

#: Statuses for base call to sequence conversion
CONVERSION_STATUS_CHOICES = (
    (STATUS_INITIAL, "keep unstarted"),
    (STATUS_READY, "ready to start"),
    (STATUS_IN_PROGRESS, "in progress"),
    (STATUS_COMPLETE, "complete"),
    (STATUS_COMPLETE_WARNINGS, "complete with warnings"),
    (STATUS_FAILED, "failed"),
    (STATUS_CLOSED, "released"),
    (STATUS_CANCELED, "failured confirmed"),
    (STATUS_SKIPPED, "skipped"),
)

#: Statuses for delivery
DELIVERY_STATUS_CHOICES = (
    (STATUS_INITIAL, "not started"),
    (STATUS_IN_PROGRESS, "in progress"),
    (STATUS_COMPLETE, "complete"),
    (STATUS_COMPLETE_WARNINGS, "complete with warnings"),
    (STATUS_CLOSED, "received"),
    (STATUS_FAILED, "canceled"),
    (STATUS_CANCELED, "canceled confirmed"),
    (STATUS_SKIPPED, "skipped"),
)

#: Delivery of sequences (FASTQ)
DELIVERY_TYPE_SEQ = "seq"

#: Delivery of base calls (BCL)
DELIVERY_TYPE_BCL = "bcl"

#: Delivery of both sequences and base calls
DELIVERY_TYPE_BOTH = "seq_bcl"

#: Delivery options
DELIVERY_CHOICES = (
    (DELIVERY_TYPE_SEQ, "sequences"),
    (DELIVERY_TYPE_BCL, "base calls"),
    (DELIVERY_TYPE_BOTH, "sequences + base calls"),
)


#: RTA version key for v1
RTA_VERSION_V1 = 1

#: RTA version key for v2
RTA_VERSION_V2 = 2

#: RTA version key for 'other'
RTA_VERSION_OTHER = 0

#: RTA version used for a flow cell
RTA_VERSION_CHOICES = (
    #: RTA v1.x, old bcl2fastq required
    (RTA_VERSION_V1, "RTA v1"),
    #: RTA v2.x, bcl2fast2 required
    (RTA_VERSION_V2, "RTA v2"),
    #: other, for future-proofness
    (RTA_VERSION_OTHER, "other"),
)


class FlowCell(models.Model):
    """Information stored for each flow cell"""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Barcodeset SODAR UUID"
    )

    #: The project containing this barcode set.
    project = models.ForeignKey(Project, help_text="Project in which this flow cell belongs")

    #: Run date of the flow cell
    run_date = models.DateField()

    #: The sequencer used for processing this flow cell
    sequencing_machine = models.ForeignKey(
        SequencingMachine, null=True, blank=True, on_delete=models.PROTECT
    )

    #: The run number on the machine
    run_number = models.PositiveIntegerField()

    #: The slot of the machine
    slot = models.CharField(max_length=1)

    #: The vendor ID of the flow cell name
    vendor_id = models.CharField(max_length=40)

    #: The label of the flow cell
    label = models.CharField(blank=True, null=True, max_length=100)

    #: Manual override for the flow cell label.
    manual_label = models.CharField(
        blank=True,
        null=True,
        max_length=100,
        help_text="Manual label for overriding the one from the folder name",
    )

    #: Short description length
    description = models.TextField(
        blank=True, null=True, help_text="Short description of the flow cell"
    )

    #: Number of lanes on the flow cell
    num_lanes = models.IntegerField(
        default=8, help_text="Number of lanes on flowcell 8 for HiSeq, 4 for NextSeq"
    )

    #: Name of the sequencing machine operator
    operator = models.CharField(max_length=100, verbose_name="Sequencer Operator")

    #: The user responsible for demultiplexing
    demux_operator = models.ForeignKey(
        User,
        verbose_name="Demultiplexing Operator",
        related_name="demuxed_flowcells",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User responsible for demultiplexing",
    )

    #: RTA version used, required for picking BCL to FASTQ and demultiplexing software
    rta_version = models.IntegerField(
        default=RTA_VERSION_V2,
        choices=RTA_VERSION_CHOICES,
        help_text="Major RTA version, implies bcl2fastq version",
    )

    #: Status of sequencing
    status_sequencing = models.CharField(
        max_length=50,
        default=STATUS_INITIAL,
        choices=SEQUENCING_STATUS_CHOICES,
        help_text="Choices for sequencing",
    )

    #: Status of base call to sequence conversion
    status_conversion = models.CharField(
        max_length=50,
        default=STATUS_INITIAL,
        choices=CONVERSION_STATUS_CHOICES,
        help_text="Choices for sequencing",
    )

    #: Status of data delivery
    status_delivery = models.CharField(
        max_length=50,
        default=STATUS_INITIAL,
        choices=DELIVERY_STATUS_CHOICES,
        help_text="Choices for sequencing",
    )

    #: What to deliver: sequences, base calls, or both.
    delivery_type = models.CharField(
        max_length=50,
        default=DELIVERY_TYPE_SEQ,
        choices=DELIVERY_CHOICES,
        help_text="Choices for data delivery type",
    )

    #: Information about the planned read in Picard notation, that is B for Sample Barcode, M for molecular barcode,
    #: T for Template, and S for skip.
    planned_reads = models.CharField(
        max_length=200, blank=True, null=True, help_text="Specification of the planned reads"
    )

    #: Information about the currently performed reads in Picard notation.
    current_reads = models.CharField(
        max_length=200, blank=True, null=True, help_text="Specification of the current reads"
    )

    #: Number of mismatches to allow, defaults to ``None`` which triggers to use the default.
    barcode_mismatches = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Number of mismatches to allow"
    )

    def get_absolute_url(self):
        return reverse(
            "flowcells:flowcell-detail",
            kwargs={"project": self.project.sodar_uuid, "flowcell": self.sodar_uuid},
        )

    def get_full_name(self):
        """Return full flow cell name"""
        values = (
            self.run_date,
            self.sequencing_machine,
            self.run_number,
            self.slot,
            self.vendor_id,
            self.label,
        )
        if all(not x for x in values):
            return ""
        else:
            run_date = "" if not self.run_date else self.run_date.strftime("%y%m%d")
            vendor_id = "" if not self.sequencing_machine else self.sequencing_machine.vendor_id
            run_number = "{:04}".format(0 if not self.run_number else self.run_number)
            return "_".join(
                map(str, (run_date, vendor_id, run_number, self.slot, self.vendor_id, self.label))
            )

    def __str__(self):
        return "FlowCell %s" % self.get_full_name()

    class Meta:
        ordering = ("-run_date", "sequencing_machine", "run_number", "slot")
