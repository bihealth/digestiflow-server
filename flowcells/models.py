import uuid as uuid_object

from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from projectroles.models import Project

from digestiflow.users.models import User
from barcodes.models import BarcodeSet, BarcodeSetEntry
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
    sequencing_machine = models.ForeignKey(SequencingMachine, null=False, on_delete=models.PROTECT)

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
        blank=False,
        null=False,
        default=8,
        help_text="Number of lanes on flowcell 8 for HiSeq, 4 for NextSeq",
    )

    #: Name of the sequencing machine operator
    operator = models.CharField(
        blank=True, null=True, max_length=100, verbose_name="Sequencer Operator"
    )

    #: The user responsible for demultiplexing
    demux_operator = models.ForeignKey(
        User,
        blank=True,
        null=True,
        verbose_name="Demultiplexing Operator",
        related_name="demuxed_flowcells",
        on_delete=models.SET_NULL,
        help_text="User responsible for demultiplexing",
    )

    #: RTA version used, required for picking BCL to FASTQ and demultiplexing software
    rta_version = models.IntegerField(
        blank=False,
        null=False,
        default=RTA_VERSION_V2,
        choices=RTA_VERSION_CHOICES,
        help_text="Major RTA version, implies bcl2fastq version",
    )

    #: Status of sequencing
    status_sequencing = models.CharField(
        blank=False,
        null=False,
        max_length=50,
        default=STATUS_INITIAL,
        choices=SEQUENCING_STATUS_CHOICES,
        help_text="Choices for sequencing",
    )

    #: Status of base call to sequence conversion
    status_conversion = models.CharField(
        blank=False,
        null=False,
        max_length=50,
        default=STATUS_INITIAL,
        choices=CONVERSION_STATUS_CHOICES,
        help_text="Choices for sequencing",
    )

    #: Status of data delivery
    status_delivery = models.CharField(
        blank=False,
        null=False,
        max_length=50,
        default=STATUS_INITIAL,
        choices=DELIVERY_STATUS_CHOICES,
        help_text="Choices for sequencing",
    )

    #: What to deliver: sequences, base calls, or both.
    delivery_type = models.CharField(
        blank=False,
        null=False,
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
        unique_together = ("vendor_id", "run_number", "sequencing_machine")
        ordering = ("-run_date", "sequencing_machine", "run_number", "slot")


#: Reference used for identifying human samples
REFERENCE_HUMAN = "hg19"

#: Reference used for identifying mouse samples
REFERENCE_MOUSE = "mm9"

#: Reference used for identifying fly samples
REFERENCE_FLY = "dm6"

#: Reference used for identifying fish samples
REFERENCE_FISH = "danRer6"

#: Reference used for identifying rat samples
REFERENCE_RAT = "rn11"

#: Reference used for identifying worm samples
REFERENCE_WORM = "ce11"

#: Reference used for identifying yeast samples
REFERENCE_YEAST = "sacCer3"

#: Reference used for identifying other samples
REFERENCE_OTHER = "__other__"

#: Reference sequence choices, to identify organisms
REFERENCE_CHOICES = (
    #: H. sapiens
    (REFERENCE_HUMAN, "human"),
    #: M. musculus
    (REFERENCE_MOUSE, "mouse"),
    #: D. melanogaster
    (REFERENCE_FLY, "fly"),
    #: D. rerio
    (REFERENCE_FISH, "zebrafish"),
    #: R. norvegicus
    (REFERENCE_RAT, "rat"),
    #: C. elegans
    (REFERENCE_WORM, "worm"),
    #: S. cerevisae
    (REFERENCE_YEAST, "yeast"),
    #: other
    (REFERENCE_OTHER, "other"),
)


class Library(models.Model):
    """The data stored for each library that is to be sequenced
    """

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Object SODAR UUID"
    )

    #: The flow cell that this library has been sequenced on
    flow_cell = models.ForeignKey(FlowCell, related_name="libraries", on_delete=models.CASCADE)

    #: The name of the library
    name = models.CharField(max_length=100)

    #: The organism to assume for this library, used for QC
    reference = models.CharField(
        null=True, blank=True, max_length=100, default="hg19", choices=REFERENCE_CHOICES
    )

    #: The barcode used for first barcode index this library
    barcode = models.ForeignKey(BarcodeSetEntry, on_delete=models.PROTECT)

    #: Optional a sequence entered directly for the first barcode
    barcode_seq = models.CharField(max_length=200, null=True, blank=True)

    #: The barcode used for second barcode index this library
    barcode2 = models.ForeignKey(
        BarcodeSetEntry, on_delete=models.PROTECT, related_name="barcodes2"
    )

    #: Optionally, a sequence entered directly for the second barcode.  Entered as for dual indexing workflow A.
    barcode_seq2 = models.CharField(max_length=200, null=True, blank=True)

    #: The lanes that the library was sequenced on on the flow cell
    lane_numbers = ArrayField(models.IntegerField(validators=[MinValueValidator(1)]))

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        """ Override to check name/barcode being unique on the flow celllanes and lane numbers are compatible."""
        self._validate_uniqueness()
        self._validate_lane_nos()
        return super().save(*args, **kwargs)

    def _validate_lane_nos(self):
        if any(l > self.flow_cell.num_lanes for l in self.lane_numbers):
            raise ValidationError(
                "Lane no {} > flow cell lane count {}".format(
                    list(sorted(self.lane_numbers)), self.flow_cell.num_lanes
                )
            )

    def _validate_uniqueness(self):
        # Get all libraries sharing any lane on the same flow cell
        libs_on_lanes = Library.objects.filter(
            flow_cell=self.flow_cell, lane_numbers__overlap=self.lane_numbers
        ).exclude(uuid=self.uuid)
        # Check that no libraries exist with the same
        if libs_on_lanes.filter(name=self.name).exists():
            raise ValidationError(
                "There are libraries sharing flow cell lane with the same name as {}".format(
                    self.name
                )
            )
        # Check that no libraries exist with the same primary and secondary barcode
        kwargs = {}
        if self.barcode is None:
            kwargs["barcode__isnull"] = True
        else:
            kwargs["barcode"] = self.barcode
        if self.barcode2 is None:
            kwargs["barcode2__isnull"] = True
        else:
            kwargs["barcode2"] = self.barcode2
        if libs_on_lanes.filter(**kwargs).exists():
            raise ValidationError(
                (
                    "There are libraries sharing flow cell lane with the "
                    "same barcodes as {}: {}/{}".format(self.name, self.barcode, self.barcode2)
                )
            )

    def get_absolute_url(self):
        return self.flow_cell.get_absolute_url()

    def __str__(self):
        return "Library {} on lane(s) {} for {}".format(
            self.name, self.lane_numbers, self.flow_cell
        )


class LaneIndexHistogram(models.Model):
    """Information about the index sequence distribution on a lane for a FlowCell"""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Object SODAR UUID"
    )

    #: The flow cell this information is for.
    flowcell = models.ForeignKey(
        FlowCell, null=False, on_delete=models.CASCADE, related_name="index_histograms"
    )

    #: The lane that this is for.
    lane = models.PositiveIntegerField(null=False, help_text="The lane this information is for.")

    #: The number of the index read that this information is for.
    index_read_no = models.PositiveIntegerField(
        null=False, help_text="The index read this information is for."
    )

    #: The sample size used.
    sample_size = models.PositiveIntegerField(null=False, help_text="Number of index reads read")

    #: The histogram information as a dict from sequence to count.
    histogram = JSONField(help_text="The index histogram information")

    def __str__(self):
        return "Index Histogram index {} lane {} flowcell {}".format(
            self.index_read_no, self.lane, self.flowcell.get_full_name()
        )

    class Meta:
        unique_together = ("flowcell", "lane", "index_read_no")
        ordering = ("flowcell", "lane", "index_read_no")
