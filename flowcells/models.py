import re
import uuid as uuid_object

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q
from mail_factory import factory
import pagerange
from projectroles.models import Project, PROJECT_TAG_STARRED
from filesfolders.models import Folder

from . import bases_mask
from digestiflow.users.models import User
from digestiflow.utils import revcomp
from barcodes.models import BarcodeSetEntry
from sequencers.models import SequencingMachine, INDEX_WORKFLOW_B


# Access Django user model
AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")

#: Threshold on read fraction showing an index to ignore if found in index histogram but not in library.
THRESH_MIN_INDEX_FRAC = 0.01


def pretty_range(value):
    return pagerange.PageRange(value).range


def prefix_match(query, db):
    """Naive implementation of "is seq prefix of one in expecteds or vice versa"."""
    for entry in db:
        min_len = min(len(query), len(entry))
        if query[:min_len] == entry[:min_len]:
            return True
    return False


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

#: RTA version key for v2
RTA_VERSION_V3 = 3

#: RTA version key for 'other'
RTA_VERSION_OTHER = 0

#: RTA version used for a flow cell
RTA_VERSION_CHOICES = (
    #: RTA v1.x, old bcl2fastq required
    (RTA_VERSION_V1, "RTA v1"),
    #: RTA v2.x, bcl2fast2 required
    (RTA_VERSION_V2, "RTA v2"),
    #: RTA v3.x, bcl2fast2 required
    (RTA_VERSION_V3, "RTA v3"),
    #: other, for future-proofness
    (RTA_VERSION_OTHER, "other"),
)


#: Current version of error cache computation code.
FLOWCELL_ERROR_CACHE_VERSION = 2


class FlowCellManager(models.Manager):
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
            | Q(manual_label__icontains=search_term)
            | Q(description__icontains=search_term)
        )
        return objects


def validate_bases_mask(value):
    """Django validator for bases mask values."""
    if value:
        try:
            bases_mask.split_bases_mask(value)
        except bases_mask.BaseMaskConfigException as e:
            raise ValidationError(str(e)) from e


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
        max_length=200,
        blank=True,
        null=True,
        validators=[validate_bases_mask],
        help_text="Specification of the planned reads",
    )

    #: Information about the currently performed reads in Picard notation.
    current_reads = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        validators=[validate_bases_mask],
        help_text="Specification of the current reads",
    )

    #: Optional override for reads information to override ``planned_reads`` in demultiplexing (in Picard notation)
    demux_reads = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        validators=[validate_bases_mask],
        help_text="Specification of the reads to use for demultiplexing (defaults to planned reads)",
    )

    #: Whether or not to create FASTQ for index reads.
    create_fastq_for_index_reads = models.BooleanField(
        default=False, verbose_name="Create FAST files for index reads"
    )

    #: Minimum trimmed read length.
    minimum_trimmed_read_length = models.IntegerField(
        blank=True,
        null=True,
        help_text="Optional, remove reads shorter than this length after adapter trimming",
    )

    #: Masking of short adapter reads.
    mask_short_adapter_reads = models.IntegerField(
        blank=True, null=True, help_text="Optional, Minimal length for adapter reads"
    )

    #: Number of mismatches to allow, defaults to ``None`` which triggers to use the default.
    barcode_mismatches = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Number of mismatches to allow"
    )

    #: Lanes to suppress the "no sample sheet information available" for
    lanes_suppress_no_sample_sheet_warning = ArrayField(
        models.PositiveIntegerField(),
        blank=True,
        default=list,
        help_text="The lanes for which missing sample sheet information should be suppressed",
    )

    #: Lanes to suppress "index sequence found with no entry in sample sheet" for
    lanes_suppress_no_sample_found_for_observed_index_warning = ArrayField(
        models.PositiveIntegerField(),
        blank=True,
        default=list,
        help_text="The lanes for which indexes without matching entry in the sample sheet should be ignored",
    )

    #: Version of the ``cache_*_error`` fields.
    error_caches_version = models.IntegerField(null=True, blank=True, default=None)

    #: Cache for index errors ``dict``.  The value maps tuples ``[name, index_read_no_seq]`` to lists
    #: of error messages.  Built on saving the ``FlowCell`` record, must be updated in a background job
    #: when the error building changes.
    cache_index_errors = JSONField(null=True, blank=True, default=None)

    #: Cache for reverse index errors, i.e., mapping from string with library UUID to pair of lists.  The lists contain
    #: the error messages for barcode #1 and barcode #2 for the given library.
    cache_reverse_index_errors = JSONField(null=True, blank=True, default=None)

    #: Cache for sample sheet errors.  A ``dict`` that maps the library UUID to a dict mapping ``"barcode"``
    #: and ``"barcode2"`` to the list of error messages for the library and the given barcode.
    cache_sample_sheet_errors = JSONField(null=True, blank=True, default=None)

    #: Search-enabled manager.
    objects = FlowCellManager()

    @property
    def is_paired(self):
        """Return whether flow cell contains paired read data."""
        return (self.planned_reads or "").count("T") > 1

    def get_planned_reads_tuples(self):
        """Return a tuple of planned read descriptions ``((count, letter))``."""
        regex = re.compile("([0-9]+)([a-zA-Z])")
        result = []
        for count, letter in re.findall(regex, self.planned_reads or ""):
            result.append((int(count), letter))
        return tuple(result)

    def get_sent_messages(self):
        """Return all published messages that are no drafts."""
        return self.messages.filter(state=MSG_STATE_SENT)

    @property
    def name(self):
        """Used for sorting results."""
        return self.vendor_id

    def get_absolute_url(self):
        return reverse(
            "flowcells:flowcell-detail",
            kwargs={"project": self.project.sodar_uuid, "flowcell": self.sodar_uuid},
        )

    def save(self, *args, **kwargs):
        """Override ``save()`` to update error messages."""
        self.update_error_caches()
        return super().save(*args, **kwargs)

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

    def has_sheet_for_lane(self, lane):
        if hasattr(self, "_has_sheet_for_lane"):
            return self._has_sheet_for_lane[lane]
        self._has_sheet_for_lane = {number: False for number in range(1, self.num_lanes + 1)}
        for lib in self.libraries.all():
            for number in lib.lane_numbers:
                self._has_sheet_for_lane[number] = True
        return self._has_sheet_for_lane[lane]

    def get_known_contaminations(self):
        """Return known contaminations dict, cut down to the sequence lengths of observed sequences."""
        if hasattr(self, "_known_contaminations"):
            return self._known_contaminations
        self._known_contaminations = {}
        all_contaminations = list(KnownIndexContamination.objects.all())
        for hist in self.index_histograms.all():
            for length in set(len(seq) for seq in hist.histogram.keys()):
                self._known_contaminations.update(
                    {entry.sequence[:length]: entry for entry in all_contaminations}
                )
        return self._known_contaminations

    def is_error_cache_update_pending(self):
        """Return whether the error caches still need an update."""
        return any(
            (
                self.cache_index_errors is None,
                self.cache_reverse_index_errors is None,
                self.cache_sample_sheet_errors is None,
                self.error_caches_version != FLOWCELL_ERROR_CACHE_VERSION,
            )
        )

    def update_error_caches(self):
        """Update ``cache_*`` properties and return ``self``.

        Meant to be called ``obj.update_error_cached().save()``.
        """
        self.cache_index_errors = self._build_index_errors()
        self.cache_reverse_index_errors = self._build_reverse_index_errors()
        self.cache_sample_sheet_errors = self._build_sample_sheet_errors()
        self.error_caches_version = FLOWCELL_ERROR_CACHE_VERSION
        return self

    def get_index_errors(self):
        """Return the index errors from the cached value.

        If the cache is empty, an empty ``dict`` is returned.  Use ``is_error_cache_update_pending()`` for
        checking first.
        """
        if hasattr(self, "_index_errors"):
            return self._index_errors
        else:
            self._index_errors = {tuple(k): v for k, v in (self.cache_index_errors or [])}
            return self._index_errors

    def _build_index_errors(self):
        """Analyze index histograms for problems and inconsistencies with sample sheet.

        Finds index histogram sequences that are not present in the sample sheet.

        Return map (list of pairs) from lane number, index read, and sequence to list of errors.
        """
        # Short-circuit if sample sheet is empty.
        if not self.libraries.all():
            return []
        # Pre-fetch libraries.
        libraries = {}
        for library in self.libraries.prefetch_related("barcode", "barcode2"):
            for lane_number in library.lane_numbers:
                libraries.setdefault(lane_number, []).append(library)
        # Build error messages
        result = {}
        for hist in self.index_histograms.all():
            if not self.has_sheet_for_lane(hist.lane):
                continue  # no errors if no sheet for lane
            # Collect sequences we expect to see for this lane and read number
            expected_seqs = set()
            for library in libraries.get(hist.lane, ()):
                if hist.index_read_no == 1:
                    barcode = library.barcode
                    barcode_seq = library.barcode_seq
                else:
                    barcode = library.barcode2
                    barcode_seq = library.barcode_seq2
                the_seq = barcode.sequence if barcode else barcode_seq
                if not the_seq:
                    continue
                if (
                    hist.index_read_no == 2
                    and self.sequencing_machine.dual_index_workflow == INDEX_WORKFLOW_B
                ):
                    the_seq = revcomp(the_seq)
                expected_seqs.add(the_seq)
            # Collect errors and write into result
            sample_size = hist.sample_size
            for seq, count in hist.histogram.items():
                errors = []
                if not seq or seq in self.get_known_contaminations():
                    continue  # contamination are not errors, will be displayed in template
                if not prefix_match(seq, expected_seqs):
                    if (
                        hist.lane
                        not in self.lanes_suppress_no_sample_found_for_observed_index_warning
                    ):
                        errors += [
                            "found barcode {} on lane {} and index read {} in BCLs but not in sample sheet".format(
                                seq, hist.lane, hist.index_read_no
                            )
                        ]
                if errors and (count / sample_size >= THRESH_MIN_INDEX_FRAC):
                    result[(hist.lane, hist.index_read_no, seq)] = errors
        return list(result.items())

    def get_reverse_index_errors(self):
        """Return index errors from the cached value.

        If the cache is empty, an empty ``dict`` is returned.  Use ``is_error_cache_update_pending()`` for
        checking first.
        """
        if hasattr(self, "_reverse_index_errors"):
            return self._reverse_index_errors
        else:
            self._reverse_index_errors = {k: v for k, v in (self.cache_reverse_index_errors or [])}
            return self._reverse_index_errors

    def _build_reverse_index_errors(self):
        """Analyze sample sheet for inconsistencies with index histograms.

        That is, instead of looking up indices from histograms in sample sheet (as done in ``get_index_errors()``),
        look at sample sheet and look whether sample sheet sequences can be found in the adapter histograms.

        Returns an error message mapping (list of pairs) from library UUID to pair of list of error messages (for first
        and second index).
        """
        # Short-circuit if there are no index histograms.
        if not self.index_histograms.all():
            return []
        # Pre-fetch the lane histograms
        lane_histos = {}
        for histo in self.index_histograms.all():
            lane_histos.setdefault(histo.lane, {}).setdefault(histo.index_read_no, []).append(histo)
        # Perform the checking
        result = {}
        for library in self.libraries.prefetch_related("barcode", "barcode2").all():
            error_lanes = []
            error_lanes2 = []
            # Collect sequences seen for this lane and read number
            for lane_number in library.lane_numbers:
                # Check for error in barcode
                if library.get_barcode_seq():
                    seen_seqs = set()
                    for hist in lane_histos.get(lane_number, {}).get(1, []):
                        seen_seqs |= set(hist.histogram.keys())
                    if (
                        not prefix_match(library.get_barcode_seq(), seen_seqs)
                        and not library.suppress_barcode1_not_observed_error
                    ):
                        error_lanes.append(lane_number)
                # Check for error in barcode2
                if library.get_barcode_seq2():
                    seen_seqs2 = set()
                    for hist in lane_histos.get(lane_number, {}).get(2, []):
                        seen_seqs2 |= set(hist.histogram.keys())
                    if (
                        not prefix_match(library.get_barcode_seq2(), seen_seqs2)
                        and not library.suppress_barcode2_not_observed_error
                    ):
                        error_lanes2.append(lane_number)
            # Build error message for this library, if any lanes are problematic
            msgs = []
            msgs2 = []
            if error_lanes:
                msgs = [
                    "barcode #1 {} ({}) for library {} not found in adapters on lane{} {}".format(
                        library.get_barcode_seq(),
                        library.barcode.name if library.barcode else "manually entered",
                        library.name,
                        "s" if len(error_lanes) > 1 else "",
                        pretty_range(error_lanes),
                    )
                ]
            if error_lanes2:
                msgs2 = [
                    "barcode #2 {} ({}) for library {} not found in adapters on lane{} {}".format(
                        library.get_barcode_seq2(),
                        library.barcode2.name if library.barcode2 else "manually entered",
                        library.name,
                        "s" if len(error_lanes2) > 1 else "",
                        pretty_range(error_lanes2),
                    )
                ]

            # Build error message for per-library demux cycles if problematic.
            library_cycles = []
            if library.demux_reads:
                try:
                    len1 = bases_mask.bases_mask_length(self.planned_reads or "")
                    len2 = bases_mask.bases_mask_length(library.demux_reads)
                    if len1 != len2:
                        library_cycles.append(
                            "Demultiplexing cycles incompatible with flow cell cycles (%d vs. %d)."
                            % (len1, len2)
                        )
                except bases_mask.BaseMaskConfigException:
                    library_cycles.append("Invalid per-library demultiplexing cycles")

            # Build error message for the barcode sequences.
            if library.demux_reads:
                demux_reads = library.demux_reads or self.demux_reads or self.planned_reads
                try:
                    barcodes = [
                        count for op, count in bases_mask.split_bases_mask(demux_reads) if op == "B"
                    ]
                except bases_mask.BaseMaskConfigException:
                    pass  # will have error above already
                if len(barcodes) == 2:
                    msg = "Demultiplexing instructions have two barcodes."
                    if not library.get_barcode_seq():
                        msgs.append(msg)
                    elif barcodes[0] > len(library.get_barcode_seq()):
                        msgs.append(
                            "Demultiplexing instructions need %d bases but barcode seq #1 has only length %d"
                            % (barcodes[0], len(library.get_barcode_seq()))
                        )
                    if not library.get_barcode_seq2():
                        msgs2.append(msg)
                    elif barcodes[1] > len(library.get_barcode_seq2()):
                        msgs.append(
                            "Demultiplexing instructions need %d bases but barcode seq #2 has only length %d"
                            % (barcodes[1], len(library.get_barcode_seq2()))
                        )
                elif len(barcodes) == 1:
                    if not library.get_barcode_seq():
                        msgs.append(msg)
                    elif barcodes[0] > len(library.get_barcode_seq()):
                        msgs.append(
                            "Demultiplexing instructions need %d bases but barcode seq #1 has only length %d"
                            % (barcodes[0], len(library.get_barcode_seq()))
                        )
                    if library.get_barcode_seq2():
                        msgs2.append("Demultiplexing instructions have only one barcode.")
                elif len(barcodes) == 0:
                    if library.get_barcode_seq():
                        msgs.append("Demultiplexing instructions don't have barcodes.")
                    if library.get_barcode_seq2():
                        msgs2.append("Demultiplexing instructions don't have barcodes.")

            if any((msgs, msgs2, library_cycles)):
                result[library.sodar_uuid_str] = {
                    "barcode": msgs,
                    "barcode2": msgs2,
                    "library_cycles": library_cycles,
                }
        return list(result.items())

    def get_sample_sheet_errors(self):
        """Return sample sheet errors from the cached value.

        The value is built on the fly if no cache exists yet.
        """
        if hasattr(self, "_sample_sheet_errors"):
            return self._sample_sheet_errors
        else:
            self._sample_sheet_errors = {k: v for k, v in (self.cache_sample_sheet_errors or [])}
            return self._sample_sheet_errors

    def _build_sample_sheet_errors(self):
        """Analyze the sample sheet for problems and inconsistencies.

        Returns map (list of pairs) from library UUID to dict with field names to list of error messages.
        """
        # Resulting error map, empty if no errors
        result = {}
        # Library from UUID
        by_uuid = {}
        # Maps for ambiguity checking
        by_name = {}  # (lane, name) => library
        by_barcode = {}  # (lane, barcode) => library
        by_barcode2 = {}  # (lane, barcode) => library

        # Gather information about libraries, directly validate names and lane numbers
        for library in self.libraries.prefetch_related("barcode", "barcode2").all():
            by_uuid[library.sodar_uuid_str] = library
            # Directly check for invalid characters
            if not re.match("^[a-zA-Z0-9_-]+$", library.name):
                result.setdefault(library.sodar_uuid_str, {}).setdefault("name", []).append(
                    "Library names may only contain alphanumeric characters, hyphens, and underscores"
                )
            # Directly check for invalid lanes
            bad_lanes = list(
                sorted(no for no in library.lane_numbers if no < 1 or no > self.num_lanes)
            )
            if bad_lanes:
                result.setdefault(library.sodar_uuid_str, {}).setdefault(
                    "lane",
                    [
                        "Flow cell does not have lane{} #{}".format(
                            "s" if len(bad_lanes) > 1 else "", pretty_range(bad_lanes)
                        )
                    ],
                )
            # Store per-lane information for ambiguity evaluation
            for lane in library.lane_numbers:
                by_name.setdefault((lane, library.name), []).append(library)
                by_barcode.setdefault((lane, library.get_barcode_seq()), {})[
                    library.sodar_uuid_str
                ] = library
                by_barcode2.setdefault((lane, library.get_barcode_seq2()), {})[
                    library.sodar_uuid_str
                ] = library

        # Check uniqueness of sample name with lane.
        bad_lanes = {}
        for (lane, _name), libraries in by_name.items():
            if len(libraries) != 1:
                for library in libraries:
                    bad_lanes.setdefault(library.sodar_uuid_str, []).append(lane)
        for sodar_uuid, lanes in bad_lanes.items():
            library = by_uuid[sodar_uuid]
            result.setdefault(sodar_uuid, {}).setdefault("name", []).append(
                "Library name {} is not unique for lane{} {}".format(
                    library.name, "s" if len(lanes) > 1 else "", pretty_range(lanes)
                )
            )

        # Check uniqueness of barcode sequence combination with lane.  This is a bit more involved as a clash in
        # one of the indices is not yet an error, it has to be in both.
        bad_lanes = {}
        for (lane, _seq), libraries in by_barcode.items():
            for library in libraries.values():
                other_libraries = by_barcode2[(lane, library.get_barcode_seq2())]
                clashes = (set(libraries.keys()) & set(other_libraries.keys())) - {
                    library.sodar_uuid_str
                }
                if clashes:
                    bad_lanes.setdefault(library.sodar_uuid_str, []).append(lane)
        for sodar_uuid, lanes in bad_lanes.items():
            library = by_uuid[sodar_uuid]
            keys = []
            if not library.get_barcode_seq() and not library.get_barcode_seq2():
                keys = ["barcode", "barcode2"]
            else:
                if library.get_barcode_seq():
                    keys.append("barcode")
                if library.get_barcode_seq2():
                    keys.append("barcode2")
            for key in keys:
                result.setdefault(sodar_uuid, {}).setdefault(key, []).append(
                    "Barcode combination {}/{} is not unique for lane{} {}".format(
                        library.get_barcode_seq() or "-",
                        library.get_barcode_seq2() or "-",
                        "s" if len(lanes) > 1 else "",
                        pretty_range(lanes),
                    )
                )
        return list(result.items())

    def is_user_watching(self, user):
        """Return whether the given user is watching."""
        try:  # use a little hack to prevent query if prefetched
            tags = self._prefetched_objects_cache["tags"]
            # Ok, it's pefetched
            return bool(
                [tag for tag in tags if tag.user == user and tag.name == FLOWCELL_TAG_WATCHING]
            )
        except (AttributeError, KeyError) as e:
            print(e)
            # Not prefetched
            return self.tags.filter(user=user, name=FLOWCELL_TAG_WATCHING).exists()

    def __str__(self):
        return "FlowCell %s" % self.get_full_name()

    class Meta:
        unique_together = ("vendor_id", "run_number", "sequencing_machine")
        ordering = ("-run_date", "sequencing_machine", "run_number", "slot")


#: Identifier for "watching" tag.
FLOWCELL_TAG_WATCHING = "WATCHING"


class FlowCellTag(models.Model):
    """Tag assigned by a user to a project"""

    #: FlowCell to which the tag is assigned
    flowcell = models.ForeignKey(
        FlowCell, null=False, related_name="tags", help_text="FlowCell to which the tag is assigned"
    )

    #: User for whom the tag is assigned
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        null=False,
        related_name="flowcell_tags",
        help_text="User for whom the tag is assigned",
    )

    #: Name of tag to be assigned
    name = models.CharField(
        max_length=64,
        unique=False,
        null=False,
        blank=False,
        default=FLOWCELL_TAG_WATCHING,
        help_text="Name of tag to be assigned",
    )

    #: FlowCellTag SODAR UUID
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="FlowCellTag SODAR UUID"
    )

    class Meta:
        ordering = ["flowcell__vendor_id", "user__username", "name"]
        unique_together = (("flowcell", "user", "name"),)

    def __str__(self):
        return "{}: {}: {}".format(self.flowcell.name, self.user.username, self.name)


def flow_cell_created(instance):
    """Handle "save" event for ``FlowCell`` objects."""
    # Subscribe the users that have the project starred.
    users = [tag.user for tag in instance.project.tags.filter(name=PROJECT_TAG_STARRED)]
    if instance.demux_operator and instance.demux_operator not in users:
        users.append(instance.demux_operator)
    for user in users:
        instance.tags.create(user=user, name=FLOWCELL_TAG_WATCHING)
    # Notify subscribers
    for user in users:
        factory.mail("flowcell_created", (user.email,), {"user": user, "flowcell": instance})


def flow_cell_updated(original, updated):
    # Notify subscribers only on status change
    users = [tag.user for tag in updated.tags.filter(name=FLOWCELL_TAG_WATCHING)]
    if updated.demux_operator and updated.demux_operator not in users:
        users.append(updated.demux_operator)
    if (
        original.status_sequencing != updated.status_sequencing
        or original.status_conversion != updated.status_conversion
        or original.status_delivery != updated.status_delivery
    ):
        for user in users:
            factory.mail(
                "flowcell_state_changed", (user.email,), {"user": user, "flowcell": updated}
            )


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


class LibraryManager(models.Manager):
    """Manager for custom table-level Library queries"""

    def find(self, search_term, _keywords=None):
        """Return objects matching the query.

        :param search_term: Search term (string)
        :param keywords: Optional search keywords as key/value pairs (dict)
        :return: Python list of BaseFilesfolderClass objects
        """
        objects = super().get_queryset()
        objects = objects.filter(
            Q(name__icontains=search_term)
            | Q(barcode__sequence__icontains=search_term)
            | Q(barcode_seq__icontains=search_term)
            | Q(barcode2__sequence__icontains=search_term)
            | Q(barcode_seq2__icontains=search_term)
        )
        return objects


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

    #: Sample sheet line for custom ordering.
    rank = models.PositiveIntegerField(blank=True, null=True)

    #: The flow cell that this library has been sequenced on
    flow_cell = models.ForeignKey(FlowCell, related_name="libraries", on_delete=models.CASCADE)

    #: The name of the library
    name = models.CharField(max_length=100)

    #: A Project identifier
    project_id = models.CharField(max_length=200, blank=True, null=True)

    #: The organism to assume for this library, used for QC
    reference = models.CharField(
        null=True, blank=True, max_length=100, default="hg19", choices=REFERENCE_CHOICES
    )

    #: The barcode used for first barcode index this library
    barcode = models.ForeignKey(BarcodeSetEntry, null=True, blank=True, on_delete=models.PROTECT)

    #: Optional a sequence entered directly for the first barcode
    barcode_seq = models.CharField(max_length=200, null=True, blank=True)

    #: The barcode used for second barcode index this library
    barcode2 = models.ForeignKey(
        BarcodeSetEntry, null=True, blank=True, on_delete=models.PROTECT, related_name="barcodes2"
    )

    #: Optionally, a sequence entered directly for the second barcode.  Entered as for dual indexing workflow A.
    barcode_seq2 = models.CharField(max_length=200, null=True, blank=True)

    #: The lanes that the library was sequenced on on the flow cell
    lane_numbers = ArrayField(models.IntegerField(validators=[MinValueValidator(1)]))

    #: Whether or not to suppress errors because the library could not be found in the adapter histograms.
    suppress_barcode1_not_observed_error = models.BooleanField(
        default=False,
        blank=True,
        help_text='Suppress "index not observed" error in barcode 1 for this library.',
    )

    #: Whether or not to suppress errors because the library could not be found in the adapter histograms.
    suppress_barcode2_not_observed_error = models.BooleanField(
        default=False,
        blank=True,
        help_text='Suppress "index not observed" error in barcode 2 for this library.',
    )

    #: Optional override for reads information to the flowcell-level demultiplexing information
    demux_reads = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Specification of the reads to use for demultiplexing (defaults to planned_reads)",
    )

    #: Search-enabled manager.
    objects = LibraryManager()

    class Meta:
        ordering = ["flow_cell", "rank", "name"]

    @property
    def sodar_uuid_str(self):
        return str(self.sodar_uuid)

    def get_barcode_seq(self):
        """Return barcode sequence #1 either from barcode or bacode_seq"""
        if self.barcode:
            return self.barcode.sequence
        else:
            return self.barcode_seq

    def get_barcode_seq2(self, revcomp_if_needed=True):
        """Return barcode sequence #2 either from barcode or bacode_seq.

        Reverse-complement appropriately unless ``revcomp_if_needed`` is ``False``.
        """
        if self.barcode2:
            seq = self.barcode2.sequence
        else:
            seq = self.barcode_seq2
        if seq and self.flow_cell.sequencing_machine.dual_index_workflow == INDEX_WORKFLOW_B:
            if revcomp_if_needed:
                seq = revcomp(seq)
        return seq

    def get_absolute_url(self):
        return self.flow_cell.get_absolute_url() + "?library=%s" % self.sodar_uuid

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

    #: The lane that this histogram is for.
    lane = models.PositiveIntegerField(null=False, help_text="The lane this information is for.")

    #: The number of the index read that this information is for.
    index_read_no = models.PositiveIntegerField(
        null=False, help_text="The index read this information is for."
    )

    #: The sample size used.
    sample_size = models.PositiveIntegerField(null=False, help_text="Number of index reads read")

    #: The histogram information as a dict from sequence to count.
    histogram = JSONField(help_text="The index histogram information")

    #: The threshold on fraction for including an adapter.
    min_index_fraction = models.FloatField(
        default=0.01,
        help_text="Minimal fraction that an adapter must have to appear in index histogram",
    )

    def __str__(self):
        return "Index Histogram index {} lane {} flowcell {}".format(
            self.index_read_no, self.lane, self.flowcell.get_full_name()
        )

    class Meta:
        unique_together = ("flowcell", "lane", "index_read_no")
        ordering = ("flowcell", "lane", "index_read_no")


#: Message state for draft
MSG_STATE_DRAFT = "draft"

#: Message state for sent
MSG_STATE_SENT = "sent"

#: Choices for message states
MSG_STATE_CHOICES = ((MSG_STATE_DRAFT, "Draft"), (MSG_STATE_SENT, "Sent"))

#: Format is plain text.
FORMAT_PLAIN = "text/plain"

#: Format is Markdown.
FORMAT_MARKDOWN = "text/markdown"

#: Choices for the format
FORMAT_CHOICES = ((FORMAT_PLAIN, "Plain Text"), (FORMAT_MARKDOWN, "Markdown"))


class MessageManager(models.Manager):
    """Manager for custom table-level Message queries"""

    def find(self, search_term, _keywords=None):
        """Return objects matching the query.

        :param search_term: Search term (string)
        :param keywords: Optional search keywords as key/value pairs (dict)
        :return: Python list of BaseFilesfolderClass objects
        """
        objects = super().get_queryset()
        objects = objects.filter(Q(subject__icontains=search_term) | Q(body__icontains=search_term))
        return objects


class Message(models.Model):
    """A message that is attached to a FlowCell."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Object SODAR UUID"
    )

    #: The flow cell that this library has been sequenced on
    author = models.ForeignKey(User, related_name="messages", null=True, on_delete=models.SET_NULL)

    #: The flow cell that this library has been sequenced on
    flow_cell = models.ForeignKey(FlowCell, related_name="messages", on_delete=models.CASCADE)

    #: The state of the message.
    state = models.CharField(
        max_length=50,
        null=False,
        choices=MSG_STATE_CHOICES,
        default=MSG_STATE_DRAFT,
        help_text="Status of the message",
    )

    #: The format of the body.
    body_format = models.CharField(
        max_length=50,
        null=False,
        choices=FORMAT_CHOICES,
        default=FORMAT_PLAIN,
        help_text="Format of the message body",
    )

    #: A list of tags.
    tags = ArrayField(models.CharField(max_length=100, blank=False), blank=True, default=list)

    #: The title of the message
    subject = models.CharField(max_length=200, null=True, blank=True, help_text="Message subject")

    #: Body text.
    body = models.TextField(null=False, blank=False, help_text="Message body")

    #: Folder for the attachments, if any.
    attachment_folder = models.ForeignKey(
        Folder, help_text="Folder for the attachments, if any.", on_delete=models.PROTECT
    )

    #: Search-enabled manager.
    objects = MessageManager()

    def save(self, *args, **kwargs):
        try:
            self.attachment_folder
        except Folder.DoesNotExist:
            self.attachment_folder = self._create_attachment_folder()
        super().save(*args, **kwargs)

    def get_project(self):
        """Return the project of the message's flow cell.

        This is required for authorization.
        """
        return self.flow_cell.project

    @transaction.atomic
    def _create_attachment_folder(self):
        """Get the folder containing the attachments of this message."""
        project = self.flow_cell.project
        container = self._get_message_attachments_folder(project)
        return container.filesfolders_folder_children.get_or_create(
            name=self.sodar_uuid, owner=self.author, project=project, folder=container
        )[0]

    def _get_message_attachments_folder(self, project):
        """Get folder containing all message attachments.

        On creation, the folder will be owned by the first created user that is a super user.

        This will only work properly if you created a super user at the very beginning.
        """
        try:
            return Folder.objects.get(project=project, name="Message Attachments")
        except Folder.DoesNotExist:
            root = get_user_model().objects.filter(is_superuser=True).order_by("pk").first()
            return Folder.objects.create(project=project, name="Message Attachments", owner=root)

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        try:
            self.attachment_folder.delete()
        except Folder.DoesNotExist:
            pass  # swallow
        return result

    class Meta:
        ordering = ("date_created",)

    def get_absolute_url(self):
        if self.state == MSG_STATE_DRAFT:
            suffix = "#message-form"
        else:
            suffix = "#message-%s" % self.sodar_uuid
        return (
            reverse(
                "flowcells:flowcell-detail",
                kwargs={
                    "project": self.flow_cell.project.sodar_uuid,
                    "flowcell": self.flow_cell.sodar_uuid,
                },
            )
            + suffix
        )

    def get_attachment_files(self):
        """Returns QuerySet with the attached files"""
        try:
            return self.attachment_folder.filesfolders_file_children.all()
        except Folder.DoesNotExist:
            return Folder.objects.none()

    def __str__(self):
        return "[%s] %s" % (self.date_created, self.subject if self.subject else "<no subject>")


def message_created(message):
    """Handle "save" event for ``Message`` objects."""
    # Notify subscribers only on status change
    flowcell = message.flow_cell
    users = [tag.user for tag in flowcell.tags.filter(name=FLOWCELL_TAG_WATCHING)]
    if flowcell.demux_operator and flowcell.demux_operator not in users:
        users.append(flowcell.demux_operator)
    for user in users:
        if user != message.author:
            factory.mail(
                "flowcell_message",
                (user.email,),
                {"user": user, "flowcell": flowcell, "message": message},
            )


class KnownIndexContamination(models.Model):
    """Known contamination """

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Object SODAR UUID"
    )

    #: Title of the contamination.
    title = models.CharField(max_length=200)

    #: Sequence of the contamination.
    sequence = models.CharField(max_length=200)

    #: Textual description of the contamination.
    description = models.TextField()

    #: Whether or not an immutable factory default.
    factory_default = models.BooleanField(default=False, help_text="Is immutable factory default")

    def __str__(self):
        return "{}: {}".format(self.sequence, self.title)
