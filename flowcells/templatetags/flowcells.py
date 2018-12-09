from django import template

from ..models import FlowCell, REFERENCE_CHOICES, pretty_range

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
def status_to_icon(status):
    return {
        "initial": "fa fc-fw fa-hourglass-1 text-muted fc-super-muted",
        "in_progress": "fc-fw fa fa-hourglass-half",
        "complete": "fa fc-fw fa-hourglass-end text-success",
        "failed": "fa fc-fw fa-hourglass-end text-danger",
        "closed": "fa fc-fw fa-check text-success",
        "canceled": "fa fc-fw fa-close text-danger",
        "skipped": "fa fc-fw fa-minus text-muted",
    }.get(status)


@register.filter
def status_to_title(status):
    return {
        "initial": "not started",
        "in_progress": "in progress",
        "complete": "complete (but unconfirmed)",
        "failed": "failed / canceled",
        "closed": "released confirmed",
        "canceled": "canceled confirmed",
        "skipped": "skipped or N/A",
    }.get(status)
