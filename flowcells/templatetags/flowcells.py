import itertools

from django import template

from ..models import (
    FlowCell,
    KnownIndexContamination,
    REFERENCE_CHOICES,
    pretty_range,
    SEQUENCING_STATUS_CHOICES,
    CONVERSION_STATUS_CHOICES,
    DELIVERY_STATUS_CHOICES,
)

register = template.Library()


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
def get_details_flowcells(project):
    """Return error messages for the given barcode seq"""
    return FlowCell.objects.filter(project=project)[:5]


@register.simple_tag
def get_index_errors(flowcell, lane, index_read_no, sequence):
    return flowcell.get_index_errors().get((lane, index_read_no, sequence))


@register.simple_tag
def get_reverse_index_errors(flowcell, library_uuid):
    return flowcell.get_reverse_index_errors().get(library_uuid)


@register.simple_tag
def get_sheet_name_errors(flowcell, entry):
    return flowcell.get_sample_sheet_errors().get(entry.sodar_uuid, {}).get("name")


@register.simple_tag
def get_sheet_lane_errors(flowcell, entry):
    return flowcell.get_sample_sheet_errors().get(entry.sodar_uuid, {}).get("lane")


@register.simple_tag
def get_sheet_barcode_errors(flowcell, entry):
    return flowcell.get_sample_sheet_errors().get(entry.sodar_uuid, {}).get("barcode")


@register.simple_tag
def get_sheet_barcode2_errors(flowcell, entry):
    return flowcell.get_sample_sheet_errors().get(entry.sodar_uuid, {}).get("barcode2")


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
def sheet_missing_for_any_lane(flowcell):
    for lane in range(1, flowcell.num_lanes):
        if not flowcell.has_sheet_for_lane(lane):
            return True
    return False


@register.simple_tag
def get_contamination(contaminations, seq):
    return contaminations.get(seq)


@register.filter
def status_to_icon(status):
    return {
        "initial": "fa fc-fw fa-asterisk text-muted fc-super-muted",
        "ready": "fa fc-fw fa-hourglass-1 text-info",
        "in_progress": "fc-fw fa fa-hourglass-half",
        "complete": "fa fc-fw fa-hourglass-end text-success",
        "complete_warnings": "fa fc-fw fa-warning -end text-warning",
        "failed": "fa fc-fw fa-hourglass-end text-danger",
        "closed": "fa fc-fw fa-check text-success",
        "closed_warnings": "fa fc-fw fa-warning text-warning",
        "canceled": "fa fc-fw fa-close text-danger",
        "skipped": "fa fc-fw fa-minus text-muted",
    }.get(status)


@register.filter
def status_to_title(status):
    return {
        "initial": "not started",
        "ready": "ready to start",
        "in_progress": "in progress",
        "complete": "complete (but unconfirmed)",
        "complete_warnings": "complete with warnings",
        "failed": "failed / canceled",
        "closed": "released confirmed",
        "closed_warnings": "complete with warnings",
        "canceled": "canceled confirmed",
        "skipped": "skipped or N/A",
    }.get(status)


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
