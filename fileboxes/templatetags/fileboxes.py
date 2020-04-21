from django import template

from ..models import FileBox

register = template.Library()


@register.simple_tag
def get_details_fileboxes(project):
    """Return sequencers for the project details page"""
    return FileBox.objects.filter(project=project)[:5]
