from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from task_manager.tasks.models import Task, TaskMembership, TaskStateHistory
from .forms import TaskCreateForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import OuterRef, Subquery, Value
from django.db.models.functions import Concat
from django.db import transaction, IntegrityError
from .services.permissions import has_permission
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect, render
from .filter import TaskFilter


# Create your views here.
class TasksListView(ListView):
    model = Task
    template_name = 'tasks/index.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        #получаем исполнителя в виде строки
        executor_sq = TaskMembership.objects.filter(
            task=OuterRef('pk'),
            role='executor'
        ).annotate(
            full_name=Concat(
                'user__first_name',
                Value(' '),
                'user__last_name'
            )
        ).values('full_name')[:1]
        qs = (
            Task.objects
            .select_related('author', 'current_state')
            #.annotate(executor_name=Subquery(executor_sq)) 999
            .annotate(executor=Subquery(executor_sq))
        )
        self.filterset = TaskFilter(
            self.request.GET or None,
            queryset=qs,
            request=self.request,
            user=self.request.user
        )
        return self.filterset.qs.distinct().order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context


class TasksCreateView(CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = 'tasks/create.html'
    success_url = reverse_lazy('tasks:index')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                executor = form.cleaned_data.get('executor')
                task = form.save(commit=False)
                task.author = self.request.user
                task.executor = executor
                task.save()
                form.save_m2m()

                TaskMembership.objects.create(
                    user=self.request.user,
                    task=task,
                    role='creator'
                )

                if executor:
                    TaskMembership.objects.get_or_create(
                        user=executor,
                        task=task,
                        role='executor'
                    )

                TaskStateHistory.objects.create(
                    task=task,
                    state=task.current_state,
                    edited_by=self.request.user
                )
                self.object = task
        except IntegrityError:
            form.add_error(None, "Task save error.")
            return self.form_invalid(form)

        messages.success(self.request, _('Task has been created successfully.'))
        return redirect(self.get_success_url())
        #return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Task not created.'))
        return super().form_invalid(form)


class TasksUpdateView(UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "tasks/update.html"
    success_url = reverse_lazy("tasks:index")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not has_permission(request.user, self.object, 'edit_task'):
            messages.error(request, _("You cannot edit this task."))
            return redirect(self.get_success_url())

        executor_membership = TaskMembership.objects.filter(
            task=self.object,
            role="executor"
        ).first()
        self.executor = executor_membership.user if executor_membership else None

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial["executor"] = self.executor
        return initial

    def form_valid(self, form):
        try:
            with transaction.atomic():
                task = form.save(commit=False)
                new_executor = form.cleaned_data.get("executor")

                old_executor_membership = TaskMembership.objects.filter(
                    task=task,
                    role="executor"
                ).first()

                old_executor = old_executor_membership.user if old_executor_membership else None

                if new_executor != old_executor:
                    if old_executor_membership:
                        old_executor_membership.delete()

                    if new_executor:
                        TaskMembership.objects.get_or_create(
                            user=new_executor,
                            task=task,
                            role="executor"
                        )

                TaskStateHistory.objects.create(
                    task=task,
                    state=form.cleaned_data["current_state"],
                    edited_by=self.request.user
                )

                task.save()
                form.save_m2m()
                self.object = task
        except IntegrityError:
            form.add_error(None, _("Task save error."))
            return self.form_invalid(form)

        messages.success(self.request, _("Task has been updated successfully."))
        return super().form_valid(form)


class TasksDeleteView(DeleteView):
    model = Task
    template_name = "tasks/delete.html"
    success_url = reverse_lazy("tasks:index")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not has_permission(request.user, self.object, 'delete_task'):
            messages.error(request, _("Only author can delete the task."))
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {
                "name": self.object.title,
            },
        )

    def post(self, request, *args, **kwargs):
        task = self.object
        try:
            with transaction.atomic():
                task.delete()
                messages.success(request, _("Task has been deleted successfully."))
        except ProtectedError as e:
            messages.error(
                request,
                _("Cannot delete task because they are used in other objects.")
            )
        return redirect(self.success_url)


class TasksDetailView(DetailView):
    model = Task
    template_name = "tasks/show.html"
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        executor = (
            TaskMembership.objects
            .filter(task=self.object, role="executor")
            .select_related("user")
            .first()
        )
        context["executor"] = (
            executor.user.get_full_name()
            if executor and executor.user.get_full_name()
            else executor.user.username if executor else ""
        )
        return context
