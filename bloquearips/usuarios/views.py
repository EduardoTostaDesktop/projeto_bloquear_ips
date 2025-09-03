from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Usuario
from .forms import UsuarioCreateForm
from .decorators import admin_required, engredes_required

# Apenas administradores podem cadastrar usuários

@admin_required
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

@admin_required
def excluir_usuarios_massa(request):
    """Exclui vários usuários de uma só vez"""
    ids = request.POST.getlist("ids")  # Pega todos os IDs selecionados
    if not ids:
        messages.warning(request, "Nenhum usuário selecionado para exclusão.")
        return redirect("lista_usuarios")

    # Proteção extra: evita deletar a própria conta
    if str(request.user.id) in ids:
        ids.remove(str(request.user.id))
        messages.warning(request, "Você não pode excluir o próprio usuário logado!")

    # Se ainda restarem IDs, faz a exclusão
    if ids:
        usuarios_excluidos = Usuario.objects.filter(id__in=ids)
        nomes_excluidos = [u.username for u in usuarios_excluidos]
        quantidade = usuarios_excluidos.count()
        usuarios_excluidos.delete()
        messages.success(request, f"{quantidade} usuário(s) excluído(s): {', '.join(nomes_excluidos)}")
    else:
        messages.info(request, "Nenhum usuário válido para exclusão.")

    return redirect("lista_usuarios")