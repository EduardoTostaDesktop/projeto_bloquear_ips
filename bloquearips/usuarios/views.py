# usuarios/views.py
from django.shortcuts import render, redirect
from .forms import UsuarioCreateForm
from django.contrib.auth.decorators import login_required, user_passes_test

def engredes_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_engredes())(view_func)

@engredes_required
def cadastrar_usuario(request):
    if request.method == "POST":
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_usuarios")
    else:
        form = UsuarioCreateForm()
    return render(request, "usuarios/cadastrar_usuario.html", {"form": form})

@engredes_required
def lista_usuarios(request):
    from .models import Usuario
    usuarios = Usuario.objects.all()
    return render(request, "usuarios/lista_usuarios.html", {"usuarios": usuarios})
