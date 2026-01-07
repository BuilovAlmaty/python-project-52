from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Label


class LabelCreateForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = [
            "name",
        ]
        labels = {
            'name': _('Name'),
        }
        error_messages = {
            "title": {
                "unique": _("Label with this name already exists."),
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
