"""Share utility code."""

from django.forms.models import model_to_dict as _model_to_dict


def model_to_dict(*args, **kwargs):
    """Custom version that knows how to deal with UUID fields.

    Serializes them to strings so they can be stored as JSON.
    """
    result = _model_to_dict(*args, **kwargs)
    if "sodar_uuid" in result:
        result["sodar_uuid"] = str(result["sodar_uuid"])
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
