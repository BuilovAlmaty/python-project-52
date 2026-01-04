import django_filters
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Task, TaskMembership
from task_manager.statuses.models import TaskState
from task_manager.labels.models import Label


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        field_name='current_state',
        queryset=TaskState.objects.all(),
        label=_('Status'),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label=_('Executor'),
        method='filter_executor',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    labels = django_filters.ModelChoiceFilter(
        queryset=Label.objects.all(),
        label=_('Label'),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    user_tasks = django_filters.BooleanFilter(
        method='filter_user_tasks',
        label=_('Only your tasks'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = Task
        fields = ['status', 'executor', 'labels', 'user_tasks']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.form.fields['executor'].label_from_instance = (
            lambda u: u.get_full_name() or u.username
        )

    def filter_executor(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            id__in=TaskMembership.objects.filter(
                user=value,
                role='executor'
            ).values('task_id')
        )

    def filter_user_tasks(self, queryset, name, value):
        if not value:
            return queryset

        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            return queryset

        return queryset.filter(author=user)
