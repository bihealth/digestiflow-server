"""Share utility code."""

import json

from crispy_forms.helper import FormHelper
from django.forms.models import model_to_dict as _model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from projectroles.models import Project


class HorizontalFormHelper(FormHelper):
    form_class = "form-horizontal"
    template_pack = "bootstrap4"
    label_class = "px-0 col-12 col-md-3 col-xl-2 col-form-label font-weight-bold"
    field_class = "px-0 col-12 col-md-9 col-xl-10"
    # We write our own form tags in the HTML.
    form_tag = False


def model_to_dict(*args, rename={}, **kwargs):
    """Custom version that knows how to deal with the types used in Django models."""
    result = _model_to_dict(*args, **kwargs)
    # Round-trip through JSON using DjangoJSONEncode to get rid of problematic fields
    result = json.loads(json.dumps(result, sort_keys=True, indent=1, cls=DjangoJSONEncoder))
    # Rename fields if any.
    for from_, to in rename.items():
        result[to] = result[from_]
        del result[from_]
    return result


def _humanize(value):
    """Return "humanized" version of ``value``."""
    if isinstance(value, dict):
        return "{...}"  # abbreviation
    elif isinstance(value, list):
        return "(...)"  # abbreviation
    else:
        return repr(value)


def humanize_dict(value):
    """Return "humanized" dict, list of key/value pairs."""
    return ", ".join("%s: %s" % (x[0], _humanize(x[1])) for x in sorted(value.items()))


class ProjectMixin:
    """Mixin for DRF views.

    Makes the project available in an API view through ``get_project()``.
    """

    #: The ``Project`` model to use.
    project_class = Project

    def get_project(self):
        """Return the project object."""
        return self.project_class.objects.get(sodar_uuid=self.kwargs["project"])


def revcomp(s):
    """Reverse complement function"""
    comp_map = {"A": "T", "a": "t", "C": "G", "c": "g", "g": "c", "G": "C", "T": "A", "t": "a"}
    return "".join(reversed([comp_map.get(x, x) for x in s]))
