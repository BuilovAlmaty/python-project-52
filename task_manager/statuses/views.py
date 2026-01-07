from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from task_manager.statuses.models import TaskStatus

from .forms import StatusCreateForm


# Create your views here.
class StatusesListView(ListView):
    model = TaskStatus
    template_name = 'statuses/index.html'
    context_object_name = 'statuses'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('-created_at')


class StatusesCreateView(CreateView):
    model = TaskStatus
    form_class = StatusCreateForm
    template_name = 'statuses/create.html'
    success_url = reverse_lazy('statuses:index')

    def form_valid(self, form):
        messages.success(
            self.request,
            _('Status has been created successfully.')
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Status not created.'))
        return super().form_invalid(form)


class StatusesUpdateView(UpdateView):
    model = TaskStatus
    form_class = StatusCreateForm
    template_name = "statuses/update.html"
    success_url = reverse_lazy("statuses:index")

    def form_valid(self, form):
        messages.success(
            self.request,
            _('Status has been updated successfully.')
        )
        return super().form_valid(form)


class StatusesDeleteView(DeleteView):
    model = TaskStatus
    template_name = "statuses/delete.html"
    success_url = reverse_lazy("statuses:index")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {
                "name": self.object.name,
            },
        )

    def post(self, request, *args, **kwargs):
        try:
            self.object.delete()
            messages.success(
                request,
                _("Status has been deleted successfully.")
            )
        except ProtectedError:
            ms = "Cannot delete status because they are used in other objects."
            messages.error(
                request,
                _(ms)
            )
        return redirect("statuses:index")

