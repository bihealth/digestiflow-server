"""Forms for the fileboxes app."""

from django import forms

from digestiflow.utils import HorizontalFormHelper
from .models import FileBox


class FileBoxForm(forms.ModelForm):
    """Form for creating and updating ``FileBox`` records."""

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project")
        super().__init__(*args, **kwargs)
        # Setup crispy-forms helper
        self.helper = HorizontalFormHelper()

    class Meta:
        model = FileBox
        fields = ("title", "description", "state_meta", "date_frozen", "date_expiry")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class FileBoxGrantForm(forms.Form):
    """Form for granting access to projects"""

    users = forms.CharField(
        min_length=3,
        label="Account(s)",
        help_text="Account names or email addresses of users to grant access.",
    )

    def __init__(self, *args, **kwargs):
        if "instance" in kwargs:
            self.instance = kwargs.pop("instance")
        super().__init__(*args, **kwargs)
        # Setup crispy-forms helper
        self.helper = HorizontalFormHelper()


class FileBoxRevokeForm(forms.Form):
    """Form for revoking access from projects."""

    def __init__(self, *args, **kwargs):
        if "instance" in kwargs:
            self.instance = kwargs.pop("instance")
        super().__init__(*args, **kwargs)
