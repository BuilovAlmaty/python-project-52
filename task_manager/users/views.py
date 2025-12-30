from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .forms import CreateForm, UserUpdateForm
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.db.models.deletion import ProtectedError


# Create your views here.
class UserListView(ListView):
    model = User
    template_name = 'users/index.html'
    context_object_name = 'users'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('-date_joined')


class UsersCreateView(CreateView):
    model = User
    form_class = CreateForm
    template_name = 'users/create.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('User has been created successfully.'))
        return response

    def form_invalid(self, form):
        messages.error(self.request, _('User not created.'))
        return super().form_invalid(form)


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    success_url = reverse_lazy('')

    def form_valid(self, form):
        messages.success(self.request, _('You have successfully logged in.'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Invalid username or password."))
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.info(self.request, _('You are logged out.'))
        return super().dispatch(request, *args, **kwargs)


class UserUpdateView(View):
    template_name = "users/update.html"

    def dispatch(self, request, *args, **kwargs):
        self.user_obj = get_object_or_404(User, pk=kwargs["pk"])

        if request.user != self.user_obj:
            messages.error(request, _("You cannot edit another user's profile."))
            return redirect("users:index")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = UserUpdateForm(instance=self.user_obj)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = UserUpdateForm(request.POST, instance=self.user_obj)

        if form.is_valid():
            form.save()
            messages.success(request, _("User has been updated successfully."))
            return redirect("users:index")

        return render(request, self.template_name, {"form": form})


class UserDeleteView(View):
    template_name = "users/delete.html"

    def dispatch(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs["pk"])
        if user != request.user:
            messages.error(request, _("You cannot edit another user's profile."))
            return redirect("users:index")
        self.del_user = user
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {
                "name": self.del_user.username,
            },
        )

    def post(self, request, *args, **kwargs):
        try:
            self.del_user.delete()
            messages.success(request, _("User has been deleted successfully."))
        except ProtectedError:
            messages.error(
                request,
                _("Cannot delete user because they are used in other objects.")
            )
        return redirect("users:index")
