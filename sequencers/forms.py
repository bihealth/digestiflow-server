"""Forms for the sequencers app."""

from django import forms

from digestiflow.utils import HorizontalFormHelper
from .models import SequencingMachine


class SequencingMachineForm(forms.ModelForm):
    """Form for creating and updating ``SequencingMachine`` records."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Setup crispy-forms helper
        self.helper = HorizontalFormHelper()

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
