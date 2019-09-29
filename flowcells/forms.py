"""Forms for the flowcells app."""

import datetime
import json
import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from . import bases_mask
from digestiflow.utils import model_to_dict, HorizontalFormHelper
from sequencers.models import SequencingMachine
from .models import (
    FlowCell,
    Message,
    SEQUENCING_STATUS_CHOICES,
    CONVERSION_STATUS_CHOICES,
    DELIVERY_STATUS_CHOICES,
    Library,
)


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
    libraries_json = forms.CharField(widget=forms.HiddenInput(), initial="{}")

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project")
        super().__init__(*args, **kwargs)
        if self.instance:
            try:
                self.fields["name"].initial = self.instance.get_full_name()
            except SequencingMachine.DoesNotExist:
                pass  # swallow
        # Fill hidden field with JSON value based on the instance's objects.
        initial_value = [
            {
                **model_to_dict(entry, exclude=("pk",), rename={"sodar_uuid": "uuid"}),
                "barcode": str(entry.barcode.sodar_uuid) if entry.barcode else None,
                "barcode2": str(entry.barcode2.sodar_uuid) if entry.barcode2 else None,
            }
            for entry in self.instance.libraries.all()
        ]
        self.fields["libraries_json"] = forms.CharField(
            widget=forms.HiddenInput(), initial=json.dumps(initial_value)
        )
        # Setup crispy-forms helper
        self.helper = HorizontalFormHelper()

    def clean(self):
        if "name" not in self.cleaned_data:
            return self.cleaned_data  # give up, wrong format
        name_dict = re.match(FLOW_CELL_NAME_RE, self.cleaned_data.pop("name")).groupdict()
        self.cleaned_data["run_date"] = datetime.datetime.strptime(
            name_dict["date"], "%y%m%d"
        ).date()
        self.cleaned_data["sequencing_machine"] = get_object_or_none(
            SequencingMachine.objects.filter(project=self.project),
            vendor_id=name_dict["machine_name"],
        )
        if self.cleaned_data["sequencing_machine"] is None:
            self.add_error("name", "Unknown sequencing machine")
        self.cleaned_data["run_number"] = int(name_dict["run_no"])
        self.cleaned_data["slot"] = name_dict["slot"]
        self.cleaned_data["vendor_id"] = name_dict["vendor_id"]
        self.cleaned_data["label"] = name_dict["label"]

        # Check compatibility between demux reads (if given) and plannned reads.
        if self.cleaned_data["demux_reads"]:
            try:
                len1 = bases_mask.bases_mask_length(self.cleaned_data["planned_reads"])
                len2 = bases_mask.bases_mask_length(self.cleaned_data["demux_reads"])
                if len1 != len2:
                    raise ValidationError(
                        "Demultiplexing reads is incompatible to planned reads (%d vs. %d)."
                        % (len1, len2)
                    )
            except bases_mask.BaseMaskConfigException:
                raise ValidationError("Invalid bases mask")

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
            "demux_reads",
            "create_fastq_for_index_reads",
            "minimum_trimmed_read_length",
            "mask_short_adapter_reads",
        )
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class FlowCellUpdateStatusForm(forms.ModelForm):
    """Helper form for updating the status."""

    def __init__(self, *args, **kwargs):
        self.attribute = kwargs.pop("attribute")
        super().__init__(*args, **kwargs)
        choices = {
            "sequencing": SEQUENCING_STATUS_CHOICES,
            "conversion": CONVERSION_STATUS_CHOICES,
            "delivery": DELIVERY_STATUS_CHOICES,
        }
        for attribute in choices.keys():
            field_name = "status_%s" % attribute
            field = forms.ChoiceField(
                required=True,
                choices=choices[attribute],
                initial=getattr(self.instance, field_name),
                widget=forms.HiddenInput(),
            )
            field.valid_choices = {key for key, _ in choices[attribute]}
            self.fields[field_name] = field

    class Meta:
        model = FlowCell
        fields = ("status_sequencing", "status_conversion", "status_delivery")


class IntegerMultipleChoiceField(forms.MultipleChoiceField):
    """Helper that casts its values to ``int``."""

    def to_python(self, value):
        result = []
        for val in value:
            result += list(map(int, val.split(",")))
        return result


class FlowCellSuppressWarningForm(forms.ModelForm):
    """Helper form for suppressing warnings on flow cells.

    This form can be used for updating the warning suppression lane list fields that are stored in the ``FlowCell`
    model itself ("no sample sheet information for lane" and "adapter found in BCL but not in sample sheet").
    """

    def __init__(self, *args, **kwargs):
        self.warning = kwargs.pop("warning")
        assert self.warning in ("no_sample_found_for_observed_index", "no_sample_sheet")
        super().__init__(*args, **kwargs)
        self.field_name = "lanes_suppress_%s_warning" % self.warning
        field = IntegerMultipleChoiceField(
            required=False,
            choices=tuple((str(lane), str(lane)) for lane in range(1, self.instance.num_lanes + 1)),
            initial=getattr(self.instance, self.field_name),
            # widget=forms.HiddenInput(),
        )
        self.fields[self.field_name] = field

    class Meta:
        model = FlowCell
        fields = (
            "lanes_suppress_no_sample_found_for_observed_index_warning",
            "lanes_suppress_no_sample_sheet_warning",
        )


class FlowCellToggleWatchingForm(forms.ModelForm):
    class Meta:
        model = FlowCell
        fields = ()


class LibrarySuppressWarningForm(forms.ModelForm):
    """Helper form for suppressing warnings on libraries.

    This form can be used for updating the per-library warning suppression fields.
    """

    class Meta:
        model = Library
        fields = ("suppress_barcode1_not_observed_error", "suppress_barcode2_not_observed_error")


class MessageForm(forms.ModelForm):
    """Form for editing messages."""

    submit = forms.ChoiceField(
        widget=forms.HiddenInput,
        choices=(("discard", "discard"), ("save", "save"), ("send", "send")),
    )

    attachment1 = forms.FileField(label="Attach File #1", required=False)
    attachment2 = forms.FileField(label="Attach File #2", required=False)
    attachment3 = forms.FileField(
        label="Attach File #3",
        required=False,
        help_text='Click "Save as Draft" to upload more files.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add fields for removing the attachments.
        for attachment in self.instance.get_attachment_files():
            self.fields["del_attachment_%s" % attachment.sodar_uuid] = forms.BooleanField(
                label="Remove %s" % attachment.name,
                help_text="Tick the checkbox if you want to remove the attachment when saving/sending",
                required=False,
            )
        # Central formatting of forms.
        self.helper = HorizontalFormHelper()

    class Meta:
        model = Message
        fields = (
            "subject",
            "body_format",
            "body",
            "submit",
            "attachment1",
            "attachment2",
            "attachment3",
        )
        widgets = {"body": forms.Textarea(attrs={"rows": 3})}
