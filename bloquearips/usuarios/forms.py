from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario

class UsuarioCreateForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ("username", "email", "tipo", "password1", "password2")

class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ("username", "email", "tipo")
