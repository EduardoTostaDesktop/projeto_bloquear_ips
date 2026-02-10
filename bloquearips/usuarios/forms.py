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
