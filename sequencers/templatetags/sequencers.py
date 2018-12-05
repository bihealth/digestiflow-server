from django import template

from ..models import SequencingMachine

register = template.Library()


@register.simple_tag
def get_details_sequencers(project):
    """Return sequencers for the project details page"""
    return SequencingMachine.objects.filter(project=project)[:5]
