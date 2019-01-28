"""Share utility code."""

import json

from crispy_forms.helper import FormHelper
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict as _model_to_dict
from rest_framework.permissions import DjangoModelPermissions
from projectroles.models import Project
from projectroles.views import ProjectPermissionMixin as _ProjectPermissionMixin


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


class SodarObjectInProjectPermissions(DjangoModelPermissions):
    """DRF ``Permissions`` implementation for objects in SODAR ``projectroles.models.Project``s.

    Permissions can only be checked on models having a ``project`` attribute.  Access control is based on the
    convention action names (``${app_label}.${action}_${model_name}``) but based on roles on the containing
    ``Project``.
    """

    def __init__(self, *args, **kwargs):
        """Override to patch ``self.perms_map`` to set required permissions on ``GET`` et al."""
        super().__init__(*args, **kwargs)
        patch = {
            "GET": ["%(app_label)s.view_%(model_name)s"],
            "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
            "HEAD": ["%(app_label)s.view_%(model_name)s"],
        }
        self.perms_map = {**self.perms_map, **patch}

    def has_permission(self, request, view):
        """Override to base permission check on project only"""
        if getattr(view, "_ignore_model_permissions", False):
            return True

        if not request.user or (
            not request.user.is_authenticated and self.authenticated_users_only
        ):
            return False

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)

        return request.user.has_perms(perms, view.get_project())


class ProjectPermissionMixin(_ProjectPermissionMixin):
    """Mixin for providing a Project object for permission checking"""

    def get_queryset(self, *args, **kwargs):
        """Override ``get_query_set()`` to filter down to the currently selected object."""
        qs = super().get_queryset(*args, **kwargs)
        if hasattr(qs.model, "project"):
            return qs.filter(project=self.get_project(self.request, self.kwargs))
        elif hasattr(qs.model, "get_project_filter_key"):
            return qs.filter(
                **{qs.model.get_project_filter_key(): self.get_project(self.request, self.kwargs)}
            )
        else:
            raise AttributeError(
                'Model does not have "project" member or "get_project_filter_key()" function'
            )
