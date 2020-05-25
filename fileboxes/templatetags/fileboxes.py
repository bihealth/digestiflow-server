from django import template

from ..models import FileBox

register = template.Library()


@register.simple_tag
def get_details_fileboxes(project):
    """Return sequencers for the project details page"""
    return FileBox.objects.filter(project=project)[:5]


@register.filter
def filebox_state_to_color(state):
    return {
        "ACTIVE": "success",
        "INACTIVE": "secondary",
        "DELETING": "danger",
        "DELETED": "dark",
    }.get(state)


@register.filter
def filebox_state_to_label(state):
    return {
        "ACTIVE": "active",
        "INACTIVE": "inactive",
        "DELETING": "deleting",
        "DELETED": "deleted",
    }.get(state)
