from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
import csv

from usuarios.decorators import allowed_roles

from .models import Lista
from enderecos.models import Endereco
from solicitantes.models import Solicitante

@allowed_roles(['admin', 'engredes'])
def listar_listas(request):
    listas = Lista.objects.all().order_by('-data_registro')
    return render(request, 'listas/listar_listas.html', {'listas': listas})

@allowed_roles(['admin', 'engredes'])
def detalhar_lista(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id)
    return render(request, 'listas/detalhar_lista.html', {'lista': lista})

@allowed_roles(['admin', 'engredes'])
def criar_lista(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        solicitante_id = request.POST.get('solicitante')
        desc = request.POST.get('desc')
        obs = request.POST.get('obs')
        data_prevista_desbloqueio = request.POST.get('data_prevista_desbloqueio')
        arquivo = request.FILES.get('arquivo_csv')
        criador = request.user

        lista = Lista.objects.create(
            nome=nome,
            solicitante_id=solicitante_id,
            desc=desc,
            obs=obs,
            criador=criador,
            data_prevista_desbloqueio=data_prevista_desbloqueio or None
        )

        if arquivo:
            decoded_file = arquivo.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            for row in reader:
                endereco_text = row[0].strip()
                if endereco_text and not Endereco.objects.filter(endereco=endereco_text).exists():
                    Endereco.objects.create(endereco=endereco_text, lista=lista)

        messages.success(request, "Lista criada com sucesso!")
        return redirect('listas:listar_listas')

    # GET
    solicitantes = Solicitante.objects.all()
    return render(request, 'listas/criar_lista.html', {'solicitantes': solicitantes})

@allowed_roles(['admin', 'engredes'])
def editar_lista(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id)

    if request.method == 'POST':
        lista.nome = request.POST.get('nome')
        lista.solicitante_id = request.POST.get('solicitante')
        lista.desc = request.POST.get('desc')
        lista.obs = request.POST.get('obs')
        lista.data_prevista_desbloqueio = request.POST.get('data_prevista_desbloqueio') or None
        lista.save()

        messages.success(request, "Lista atualizada com sucesso!")
        return redirect('listas:detalhar_lista', lista_id=lista.id)

    # GET
    solicitantes = Solicitante.objects.all()
    return render(request, 'listas/editar_lista.html', {'lista': lista, 'solicitantes': solicitantes})
