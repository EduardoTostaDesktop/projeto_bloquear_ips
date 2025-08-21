from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Usuario
from .forms import UsuarioCreateForm
from .decorators import admin_required, engredes_required

# Somente administradores podem acessar o painel de usuários
@admin_required
def painel_usuarios(request):
    return render(request, 'usuarios/painel_usuarios.html')

# Apenas administradores podem cadastrar usuários

def cadastrar_usuario(request):
    if request.method == "POST":
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário cadastrado com sucesso!")
            return redirect("lista_usuarios")
    else:
        form = UsuarioCreateForm()
    return render(request, "usuarios/cadastrar_usuario.html", {"form": form})

# Lista todos os usuários — restrito para administradores
@admin_required
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, "usuarios/lista_usuarios.html", {"usuarios": usuarios})

# Editar usuário — apenas administradores
@admin_required
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == "POST":
        usuario.username = request.POST.get('username')
        usuario.email = request.POST.get('email')
        usuario.tipo = request.POST.get('tipo')
        usuario.save()
        messages.success(request, "Usuário atualizado com sucesso!")
        return redirect('lista_usuarios')

    return render(request, 'usuarios/editar_usuario.html', {
        'usuario': usuario,
        'Usuario': Usuario,
    })

# Excluir usuário — só administradores
@admin_required
def excluir_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    usuario.delete()
    messages.success(request, "Usuário excluído com sucesso!")
    return redirect('lista_usuarios')
