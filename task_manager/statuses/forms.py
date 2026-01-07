from django import forms
from django.utils.translation import gettext_lazy as _

from .models import TaskStatus

HELP_TEXTS = {
    "name": _("Required field"),
}


class StatusCreateForm(forms.ModelForm):
    class Meta:
        model = TaskStatus
        fields = [
            "name",
        ]
        labels = {
            "name": _("Name"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
            field.help_text = HELP_TEXTS.get(field_name, "")

