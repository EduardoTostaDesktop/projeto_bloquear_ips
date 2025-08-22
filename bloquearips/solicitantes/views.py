from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect

from usuarios.decorators import allowed_roles
from .models import Solicitante
from django.contrib.auth.decorators import login_required

@allowed_roles(['admin', 'engredes'])
def listar_solicitantes(request):
    solicitantes = Solicitante.objects.all().order_by('nome')
    return render(request, 'solicitantes/listar_solicitantes.html', {'solicitantes': solicitantes})

@allowed_roles(['admin', 'engredes'])
def detalhar_solicitante(request, solicitante_id):
    solicitante = get_object_or_404(Solicitante, id=solicitante_id)
    return render(request, 'solicitantes/detalhar_solicitante.html', {'solicitante': solicitante})

@allowed_roles(['admin', 'engredes'])
def cadastrar_solicitante(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        contato = request.POST.get('contato')
        obs = request.POST.get('obs')

        Solicitante.objects.create(
            nome=nome,
            contato=contato,
            obs=obs
        )
        messages.success(request, "Solicitante criado com sucesso!")
        return redirect('solicitantes:listar_solicitantes')

    return render(request, 'solicitantes/cadastrar_solicitante.html')

@allowed_roles(['admin', 'engredes'])
def editar_solicitante(request, solicitante_id):
    solicitante = get_object_or_404(Solicitante, id=solicitante_id)

    if request.method == 'POST':
        solicitante.nome = request.POST.get('nome')
        solicitante.contato = request.POST.get('contato')
        solicitante.obs = request.POST.get('obs')
        solicitante.save()
        messages.success(request, "Solicitante atualizado com sucesso!")
        return redirect('solicitantes:detalhar_solicitante', solicitante_id=solicitante.id)

    return render(request, 'solicitantes/editar_solicitante.html', {'solicitante': solicitante})
