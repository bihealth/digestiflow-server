"""Forms for the barcodes app."""

from uuid import UUID
import json

from django import forms

from .models import BarcodeSet


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class BarcodeSetForm(forms.ModelForm):
    """Form for creating and updating ``BarcodeSet`` records."""

    entries_json = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fill hidden field with JSON value based on the instance's objects.s
        initial_value = [
            {"uuid": entry.sodar_uuid, "name": entry.name, "sequence": entry.sequence}
            for entry in self.instance.entries.all()
        ]
        self.fields["entries_json"] = forms.CharField(
            widget=forms.HiddenInput(), initial=json.dumps(initial_value, cls=UUIDEncoder)
        )

    class Meta:
        model = BarcodeSet
        fields = ("name", "short_name", "description", "set_type", "entries_json")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
