from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django import forms
from django.core.exceptions import ValidationError


HELP_TEXTS = {
    "username": _("Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_."),
    "password1": _("Обязательное поле. Используйте хотя бы 8 символов."),
    "password2": _("Введите пароль ещё раз для подтверждения."),
    "first_name": _("Обязательное поле. Только буквы."),
    "last_name": _("Обязательное поле. Только буквы."),
    "pass_error": _("Введите оба пароля.")
}


class CreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
            field.help_text = HELP_TEXTS.get(field_name, "")


class UserUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_("Пароль"),
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "readonly": True}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 or p2:
            if p1 != p2:
                raise ValidationError(_("Пароли не совпадают"))
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class UserSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = False
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
            field.help_text = HELP_TEXTS.get(field_name, "")

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if not password1 and not password2:
            self._skip_password = True
            return cleaned_data

        if not password1 or not password2:
            raise ValidationError(HELP_TEXTS["pass_error"])

        self._skip_password = False
        return cleaned_data

    def save(self, commit=True):
        if getattr(self, "_skip_password", False):
            return self.user

        return super().save(commit=commit)
