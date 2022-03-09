import itertools

from django import template
from django.db.models import Q
from django.utils.safestring import mark_safe

from .. import bases_mask
from ..models import (
    FlowCell,
    REFERENCE_CHOICES,
    pretty_range,
    SEQUENCING_STATUS_CHOICES,
    CONVERSION_STATUS_CHOICES,
    DELIVERY_STATUS_CHOICES,
)

register = template.Library()


FLOWCELL_STATUS = {
    "initial": {
        "class": "text-muted fc-super-muted",
        "icon": "mdi:asterisk",
        "title": "not started",
    },
    "ready": {
        "class": "text-info",
        "icon": "mdi:timer-sand",
        "title": "ready to start",
    },
    "in_progress": {
        "class": "",
        "icon": "mdi:timer-sand-paused",
        "title": "in progress",
    },
    "complete": {
        "class": "text-success",
        "icon": "mdi:timer-sand-complete",
        "title": "complete (but unconfirmed)",
    },
    "complete_warnings": {
        "class": "text-warning",
        "icon": "mdi:alert-box",
        "title": "complete with warnings",
    },
    "failed": {
        "class": "text-danger",
        "icon": "mdi:timer-sand-complete",
        "title": "failed / canceled",
    },
    "closed": {
        "class": "text-success",
        "icon": "mdi:check-bold",
        "title": "released confirmed",
    },
    "closed_warnings": {
        "class": "text-warning",
        "icon": "mdi:alert-box",
        "title": "complete with warnings",
    },
    "canceled": {
        "class": "text-danger",
        "icon": "mdi:close-thick",
        "title": "canceled confirmed",
    },
    "skipped": {
        "class": "text-muted",
        "icon": "mdi:minus-thick",
        "title": "skipped or N/A",
    },
}


@register.simple_tag
def count_barcode_reads(flow_cell):
    """Count number of barcode reads in the planned reads of ``flow_cell``."""
    try:
        return len(
            [op for op, count in bases_mask.split_bases_mask(flow_cell.planned_reads) if op == "B"]
        )
    except bases_mask.BaseMaskConfigException:
        return None


@register.simple_tag
def get_details_flowcells(project):
    """Return sequencers for the project details page"""
    return FlowCell.objects.filter(project=project)[:5]


REF_CHOICE_MAP = dict(REFERENCE_CHOICES)


@register.filter
def reference_label(reference):
    return REF_CHOICE_MAP.get(reference, "unknown")


@register.filter(name="pretty_range")
def _pretty_range(value):
    return pretty_range(value)


@register.filter
def divide(value, arg):
    """Divides the value; argument is the divisor. Returns empty string on any error."""
    try:
        value = float(value)
        arg = float(arg)
        if not arg:
            if value:
                return "x/0"
            else:
                return "0.0"
        if arg:
            return value / arg
    except ValueError:
        pass
    return ""


@register.filter
def multiply(value, arg):
    """Multiply the value"""
    try:
        return float(value) * float(arg)
    except ValueError:
        pass
    return ""


@register.simple_tag
def get_lane_index_errors(flowcell, lane):
    result = []
    for (err_lane, _, _), val in flowcell.get_index_errors().items():
        if lane == err_lane:
            result.append(val)
    return result


@register.simple_tag
def get_index_error_lanes(flowcell, ignore_suppressions=False):
    if ignore_suppressions:
        result = list(flowcell.lanes_suppress_no_sample_found_for_observed_index_warning)
    else:
        result = []
    for (lane, _, _), _ in flowcell.get_index_errors().items():
        if (
            ignore_suppressions
            or lane not in flowcell.lanes_suppress_no_sample_found_for_observed_index_warning
        ):
            result.append(lane)
    return list(sorted(set(result)))


@register.simple_tag
def get_index_errors(flowcell, lane, index_read_no, sequence):
    return flowcell.get_index_errors().get((lane, index_read_no, sequence))


@register.simple_tag
def get_reverse_index_errors(flowcell, library_uuid):
    return flowcell.get_reverse_index_errors().get(
        str(library_uuid), {"barcode": [], "barcode2": []}
    )


@register.simple_tag
def get_sheet_name_errors(flowcell, entry):
    return flowcell.get_sample_sheet_errors().get(str(entry.sodar_uuid), {}).get("name")


@register.simple_tag
def get_sheet_lane_errors(flowcell, entry):
    return flowcell.get_sample_sheet_errors().get(str(entry.sodar_uuid), {}).get("lane")


@register.simple_tag
def get_sheet_barcode_errors(flowcell, entry):
    return flowcell.get_sample_sheet_errors().get(str(entry.sodar_uuid), {}).get("barcode")


@register.simple_tag
def get_sheet_barcode2_errors(flowcell, entry):
    return flowcell.get_sample_sheet_errors().get(str(entry.sodar_uuid), {}).get("barcode2")


@register.filter
def all_n(seq):
    return all(s == "N" for s in seq)


@register.filter(name="max")
def max_value(iter):
    return max(iter)


@register.filter
def chain(lhs, rhs):
    return itertools.chain(lhs or (), rhs or ())


@register.simple_tag
def get_known_contaminations(flowcell):
    return flowcell.get_known_contaminations()


@register.simple_tag
def has_sheet_for_lane(flowcell, lane):
    return flowcell.has_sheet_for_lane(lane)


@register.simple_tag
def get_libraries_with_suppressed_reverse_index_errors(flowcell):
    """Return libraries of flowcell with suppressed reversed index errors"""
    return flowcell.libraries.filter(
        Q(suppress_barcode1_not_observed_error=True) | Q(suppress_barcode2_not_observed_error=True)
    )


@register.simple_tag
def get_lanes_with_missing_sheets(flowcell, ignore_suppressions=False):
    result = []
    for lane in range(1, flowcell.num_lanes + 1):
        if not flowcell.has_sheet_for_lane(lane) and (
            ignore_suppressions or lane not in flowcell.lanes_suppress_no_sample_sheet_warning
        ):
            result.append(lane)
    return result


@register.simple_tag
def get_contamination(contaminations, seq):
    return contaminations.get(seq)


@register.simple_tag
def get_status_class(status):
    return FLOWCELL_STATUS.get(status).get("class")


@register.simple_tag
def get_status_icon(status):
    return FLOWCELL_STATUS.get(status, {}).get("icon")


# TODO: This doesn't seem to be used anywhere?
@register.filter
def status_to_title(status):
    return FLOWCELL_STATUS.get(status, {}).get("title")


@register.simple_tag
def valid_status(attribute, value):
    if attribute == "status_sequencing":
        return value in dict(SEQUENCING_STATUS_CHOICES)
    elif attribute == "status_conversion":
        return value in dict(CONVERSION_STATUS_CHOICES)
    elif attribute == "status_delivery":
        return value in dict(DELIVERY_STATUS_CHOICES)
    else:
        return False


@register.simple_tag
def is_user_watching_flowcell(user, flowcell):
    """Wehther the ``user`` is watching ``flowcell``"""
    return flowcell.is_user_watching(user)


@register.filter(is_safe=True)
def format_basemask(x):
    if not x:
        return x
    try:
        split_result = bases_mask.split_bases_mask(x)
    except bases_mask.BaseMaskConfigException:
        return x
    safe = [(op if op.upper() in "BMTS" else "?", c) for op, c in split_result]
    return mark_safe(",".join("%d%s" % (c, op) for op, c in safe))


@register.simple_tag
def get_adapter_siblings(flowcell, seq):
    max_dist = 1
    seqs = flowcell.get_cached_adapter_seqs()
    result = []
    for s in seqs:
        if len([x for x, y in zip(seq, s) if x != y]) <= max_dist:
            result.append(s)
    return result
