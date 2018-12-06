"""Share utility code."""

import json

from django.forms.models import model_to_dict as _model_to_dict
from django.core.serializers.json import DjangoJSONEncoder


def model_to_dict(*args, **kwargs):
    """Custom version that knows how to deal with the types used in Django models."""
    result = _model_to_dict(*args, **kwargs)
    # Round-trip through JSON using DjangoJSONEncode to get rid of problematic fields
    return json.loads(json.dumps(result, sort_keys=True, indent=1, cls=DjangoJSONEncoder))


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
