from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .models import Label
from .forms import LabelCreateForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.db.models.deletion import ProtectedError


# Create your views here.
class LabelsListView(ListView):
    model = Label
    template_name = 'labels/index.html'
    context_object_name = 'labels'


class LabelsCreateView(CreateView):
    model = Label
    template_name = 'labels/create.html'
    form_class = LabelCreateForm
    success_url = reverse_lazy('labels:index')

    def form_valid(self, form):
        messages.success(self.request, _('Label has been created successfully.'))
        return super().form_valid(form)


class LabelsUpdateView(UpdateView):
    model = Label
    template_name = 'labels/update.html'
    form_class = LabelCreateForm
    success_url = reverse_lazy('labels:index')

    def form_valid(self, form):
        messages.success(self.request, _('Label has been updated successfully.'))
        return super().form_valid(form)


class LabelsDeleteView(DeleteView):
    model = Label
    template_name = "labels/delete.html"
    success_url = reverse_lazy("labels:index")

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
            messages.success(request, _("Label has been deleted successfully."))
        except ProtectedError:
            messages.error(
                request,
                _("Cannot delete label because they are used in other objects.")
            )
        return redirect("labels:index")
