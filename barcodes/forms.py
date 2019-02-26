"""Forms for the barcodes app."""

# TODO: add validation for entries JSON?

import json

from django import forms

from digestiflow.utils import model_to_dict, HorizontalFormHelper
from .models import BarcodeSet


class BarcodeSetForm(forms.ModelForm):
    """Form for creating and updating ``BarcodeSet`` records."""

    entries_json = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fill hidden field with JSON value based on the instance's objects.s
        initial_value = []
        for entry in self.instance.entries.all():
            val = model_to_dict(entry, exclude=("pk",), rename={"sodar_uuid": "uuid"})
            val["aliases"] = ",".join(val["aliases"])
            initial_value.append(val)
        self.fields["entries_json"] = forms.CharField(
            widget=forms.HiddenInput(), initial=json.dumps(initial_value)
        )
        # Setup crispy-forms helper
        self.helper = HorizontalFormHelper()

    class Meta:
        model = BarcodeSet
        fields = ("name", "short_name", "description", "set_type", "entries_json")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
