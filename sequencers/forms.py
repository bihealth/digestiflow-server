"""Forms for the sequencers app."""

from django import forms

from .models import SequencingMachine


class SequencingMachineForm(forms.ModelForm):
    """Form for creating and updating ``SequencingMachine`` records."""

    class Meta:
        model = SequencingMachine
        fields = (
            "vendor_id",
            "label",
            "description",
            "machine_model",
            "slot_count",
            "dual_index_workflow",
        )
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
