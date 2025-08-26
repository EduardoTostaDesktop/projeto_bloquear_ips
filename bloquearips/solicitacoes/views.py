import csv
from io import TextIOWrapper
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from usuarios.decorators import allowed_roles
from .models import Solicitacao
from listas.models import Lista
from solicitantes.models import Solicitante
from enderecos.models import Endereco
from datetime import datetime
import openpyxl


@allowed_roles(['admin', 'engredes'])
def listar_solicitacoes(request):
    solicitacoes = Solicitacao.objects.all().order_by("-id")
    return render(request, "solicitacoes/listar_solicitacoes.html", {
        "solicitacoes": solicitacoes
    })


@allowed_roles(['admin', 'engredes'])
def detalhar_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id)
    return render(request, 'solicitacoes/detalhar_solicitacao.html', {
        'solicitacao': solicitacao
    })

@allowed_roles(['admin', 'engredes'])
def criar_solicitacao(request):
    solicitantes = Solicitante.objects.all()
    listas = Lista.objects.all()
    enderecos = Endereco.objects.all()

    if request.method == "POST":
        tipo = request.POST.get("tipo")
        solicitante_id = request.POST.get("solicitante")
        lista_existente_id = request.POST.get("lista_existente")
        nome_lista = request.POST.get("nome_lista")
        arquivo = request.FILES.get("arquivo")
        usuario = request.user
        desc = request.POST.get("desc")
        obs = request.POST.get("obs")
        data_prevista = request.POST.get("data_prevista") or None

        # Valida solicitante
        if not solicitante_id:
            messages.error(request, "Selecione um solicitante.")
            return redirect("solicitacoes:criar_solicitacao")
        solicitante = get_object_or_404(Solicitante, id=solicitante_id)

        # Seleciona ou cria lista
        if lista_existente_id:
            lista = get_object_or_404(Lista, id=lista_existente_id)
        else:
            if not nome_lista:
                messages.error(request, "Digite um nome para a nova lista.")
                return redirect("solicitacoes:criar_solicitacao")
            lista = Lista.objects.create(
                nome=nome_lista,
                solicitante=solicitante,
                criado_por=usuario
            )
            # Processa arquivo Excel/CSV se houver
            if arquivo:
                try:
                    import csv
                    from io import TextIOWrapper
                    csv_file = TextIOWrapper(arquivo.file, encoding="utf-8")
                    reader = csv.reader(csv_file)
                    for row in reader:
                        endereco_texto = row[0].strip()
                        if endereco_texto:
                            endereco_obj, created = Endereco.objects.get_or_create(endereco=endereco_texto)
                            lista.enderecos.add(endereco_obj)
                except Exception as e:
                    messages.warning(request, f"Erro ao processar o arquivo: {e}")

        # Bloqueia ou desbloqueia todos os endereços da lista
        if tipo == "BLOQUEIO":
            lista.enderecos.update(status=True)
        elif tipo == "DESBLOQUEIO":
            lista.enderecos.update(status=False)

        # Cria a solicitação
        Solicitacao.objects.create(
            lista=lista,
            tipo=tipo,
            solicitante=solicitante,
            data_prevista=data_prevista,
            desc=desc,
            obs=obs,
            criado_por=usuario
        )

        messages.success(request, "Solicitação criada e endereços atualizados com sucesso!")
        return redirect("solicitacoes:listar_solicitacoes")

    # GET
    return render(request, "solicitacoes/criar_solicitacao.html", {
        "solicitantes": solicitantes,
        "listas": listas,
        "enderecos": enderecos
    })


@allowed_roles(['admin', 'engredes'])
def excluir_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id)
    solicitacao.delete()
    messages.success(request, f'Solicitação "{solicitacao.lista.nome}" excluída com sucesso!')
    return redirect('solicitacoes:listar_solicitacoes')


@allowed_roles(['admin', 'engredes'])
def excluir_solicitacoes_massa(request):
    if request.method == "POST":
        ids = request.POST.getlist('ids')
        if ids:
            Solicitacao.objects.filter(id__in=ids).delete()
            messages.success(request, f"{len(ids)} solicitação(ões) excluída(s) com sucesso!")
        else:
            messages.warning(request, "Nenhuma solicitação selecionada para exclusão.")
    return redirect('solicitacoes:listar_solicitacoes')
