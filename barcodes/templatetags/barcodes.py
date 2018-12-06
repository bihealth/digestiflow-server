from django import template

from ..models import BarcodeSet

register = template.Library()


@register.simple_tag
def get_details_barcodesets(project):
    """Return sequencers for the project details page"""
    return BarcodeSet.objects.filter(project=project)[:5]
