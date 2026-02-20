from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class UsuarioCreateForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = (
            "nome",
            "username",
            "email",
            "tipo",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if email and Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Já existe um usuário cadastrado com este e-mail."
            )

        return email