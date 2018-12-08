"""Forms for the flowcells app."""

import datetime
import json
import re

from django import forms
from django.core.validators import RegexValidator

from digestiflow.utils import model_to_dict
from sequencers.models import SequencingMachine
from .models import FlowCell


def get_object_or_none(klass, *args, **kwargs):
    """Helper function"""
    if hasattr(klass, "_default_manager"):
        queryset = klass._default_manager.all()
    else:
        queryset = klass
    try:
        return queryset.get(*args, **kwargs)
    except AttributeError:
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        tpl = "First argument to get_object_or_none() must be a Model, Manager, or QuerySet, not '%s'."
        raise ValueError(tpl % klass__name)
    except queryset.model.DoesNotExist:
        return None


#: Regular expression for flow cell names
FLOW_CELL_NAME_RE = (
    r"^(?P<date>\d{6,6})"
    r"_(?P<machine_name>[^_]+)"
    r"_(?P<run_no>\d+)"
    r"_(?P<slot>\w)"
    r"_(?P<vendor_id>[^_]+)"
    r"(_(?P<label>.+))?$"
)


class FlowCellForm(forms.ModelForm):
    """Form for creating and updating ``FlowCell`` records."""

    #: Special field with the flow cell name.  The different tokens will be extracted in the form's logic
    name = forms.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                FLOW_CELL_NAME_RE,
                message=(
                    "Invalid flow cell name. Did you forgot the underscore between the slot and the vendor ID?"
                ),
            )
        ],
        help_text="The full flow cell name, e.g., 160303_ST-K12345_0815_A_BCDEFGHIXX_LABEL",
    )

    #: The libraries will be transmitted serialized as JSON in a hidden input that is updated from the Vue.js
    #: component in the front-end.
    libraries_json = forms.CharField(widget=forms.HiddenInput(), initial='{}')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields["name"].initial = self.instance.get_full_name()
        # Fill hidden field with JSON value based on the instance's objects.s
        initial_value = [
            {
                **model_to_dict(entry, exclude=('pk',), rename={'sodar_uuid': 'uuid'}),
                'barcode': str(entry.barcode.sodar_uuid),
                'barcode2': str(entry.barcode2.sodar_uuid),
            }
            for entry in self.instance.libraries.all()
        ]
        self.fields["libraries_json"] = forms.CharField(
            widget=forms.HiddenInput(), initial=json.dumps(initial_value)
        )

    def clean(self):
        if "name" not in self.cleaned_data:
            return self.cleaned_data  # give up, wrong format
        name_dict = re.match(FLOW_CELL_NAME_RE, self.cleaned_data.pop("name")).groupdict()
        self.cleaned_data["run_date"] = datetime.datetime.strptime(
            name_dict["date"], "%y%m%d"
        ).date()
        self.cleaned_data["sequencing_machine"] = get_object_or_none(
            SequencingMachine, vendor_id=name_dict["machine_name"]
        )
        if self.cleaned_data["sequencing_machine"] is None:
            self.add_error("name", "Unknown sequencing machine")
        self.cleaned_data["run_number"] = int(name_dict["run_no"])
        self.cleaned_data["slot"] = name_dict["slot"]
        self.cleaned_data["vendor_id"] = name_dict["vendor_id"]
        self.cleaned_data["label"] = name_dict["label"]
        return self.cleaned_data

    def save(self, *args, **kwargs):
        for key in ("run_date", "sequencing_machine", "run_number", "slot", "vendor_id", "label"):
            setattr(self.instance, key, self.cleaned_data[key])
        return super().save(*args, **kwargs)

    class Meta:
        model = FlowCell
        fields = (
            "name",
            "manual_label",
            "description",
            "num_lanes",
            "operator",
            "demux_operator",
            "rta_version",
            "status_sequencing",
            "status_conversion",
            "status_delivery",
            "delivery_type",
            "barcode_mismatches",
            "planned_reads",
            "current_reads",
        )
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
