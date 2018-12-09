from django import template
import pagerange

from ..models import FlowCell, REFERENCE_CHOICES

register = template.Library()


@register.simple_tag
def get_details_flowcells(project):
    """Return sequencers for the project details page"""
    return FlowCell.objects.filter(project=project)[:5]


REF_CHOICE_MAP = dict(REFERENCE_CHOICES)


@register.filter
def reference_label(reference):
    return REF_CHOICE_MAP.get(reference, "unknown")


@register.filter
def pretty_range(value):
    return pagerange.PageRange(value).range


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


@register.filter
def all_n(seq):
    return all(s == 'N' for s in seq)


@register.filter(name="max")
def max_value(iter):
    return max(iter)
