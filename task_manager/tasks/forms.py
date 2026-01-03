from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from .models import Task
from django import forms
from task_manager.labels.models import Label

HELP_TEXTS = {
    "title": _("Required field"),
}


class TaskCreateForm(forms.ModelForm):
    executor = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_('Executor'),
        widget=forms.Select(attrs={'class': 'form-control', 'data-placeholder': 'Выберите исполнителя'})
    )
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        required=False,
        label=_('Labels'),
        widget=forms.SelectMultiple(
            attrs={'class': 'form-select', 'size': 6}
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['executor'].label_from_instance = (
            lambda user: f"{user.first_name} {user.last_name}".strip()
        )
        for field_name, field in self.fields.items():
            if field_name != 'labels':
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.label
                field.help_text = HELP_TEXTS.get(field_name, "")

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "current_state",
            "executor",
            "labels",
        ]
        labels = {
            'title': _('Name'),
            'description': _('Description'),
            'current_state': _('Status'),
        }
        error_messages = {
            "title": {
                "unique": _("Task with this title already exists."),
            }
        }
