import openpyxl
from datetime import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from usuarios.decorators import allowed_roles
from .models import Solicitacao
from listas.models import Lista
from solicitantes.models import Solicitante
from enderecos.models import Endereco


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
        enderecos_ids = request.POST.getlist("enderecos")
        data_prevista = request.POST.get("data_prevista")
        desc = request.POST.get("desc")
        obs = request.POST.get("obs")
        arquivo = request.FILES.get("arquivo")

        solicitante = get_object_or_404(Solicitante, id=solicitante_id)

        # Converte data prevista para timezone-aware
        data_prevista_obj = timezone.make_aware(datetime.strptime(data_prevista, "%Y-%m-%d")) if data_prevista else None

        # --- Seleciona lista existente ou cria nova ---
        if lista_existente_id:
            lista = get_object_or_404(Lista, id=lista_existente_id)
        else:
            if not nome_lista:
                messages.error(request, "Você deve informar um nome para a nova lista.")
                return redirect("solicitacoes:criar_solicitacao")

            lista = Lista.objects.create(
                nome=nome_lista,
                solicitante=solicitante,
                criador=request.user,
                data_prevista_desbloqueio=data_prevista_obj
            )

        # --- Monta os endereços que farão parte da solicitação ---
        enderecos_solicitacao = []

        # Adiciona endereços selecionados manualmente
        if enderecos_ids:
            enderecos_selecionados = Endereco.objects.filter(id__in=enderecos_ids)
            lista.enderecos.add(*enderecos_selecionados)
            enderecos_solicitacao.extend(enderecos_selecionados)

        # Processa arquivo XLSX, se enviado
        if arquivo:
            try:
                wb = openpyxl.load_workbook(arquivo)
                sheet = wb.active
                for row in sheet.iter_rows(values_only=True):
                    endereco_texto = str(row[0]).strip()
                    if endereco_texto:
                        endereco_obj, _ = Endereco.objects.get_or_create(endereco=endereco_texto)
                        lista.enderecos.add(endereco_obj)
                        enderecos_solicitacao.append(endereco_obj)
            except Exception as e:
                messages.error(request, f"Erro ao processar o arquivo: {e}")
                return redirect("solicitacoes:criar_solicitacao")

        # Se nenhum endereço foi enviado manualmente ou via arquivo, usa os já existentes da lista
        if not enderecos_solicitacao and lista.enderecos.exists():
            enderecos_solicitacao = list(lista.enderecos.all())

        if not enderecos_solicitacao:
            messages.error(request, "Nenhum endereço válido foi selecionado ou encontrado.")
            return redirect("solicitacoes:criar_solicitacao")

        # Gera o nome da solicitação
        data_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        nome_solicitacao = f"{solicitante.nome} - {lista.nome} - {data_str}"

        # Cria a solicitação
        solicitacao = Solicitacao.objects.create(
            lista=lista,
            tipo=tipo,
            solicitante=solicitante,
            data_prevista=data_prevista_obj,
            desc=desc,
            obs=obs,
            criado_por=request.user,
            nome=nome_solicitacao
        )

        # --- Atualiza apenas os endereços que precisam de alteração ---
        novo_status = tipo == "BLOQUEIO"
        alterados = 0

        for endereco in enderecos_solicitacao:
            if endereco.status != novo_status:
                endereco.status = novo_status
                endereco.data_desbloqueio = data_prevista_obj if novo_status else None
                endereco.save()
                alterados += 1

        if alterados:
            messages.success(
                request,
                f"{alterados} endereço(s) {'bloqueado(s)' if novo_status else 'desbloqueado(s)'} com sucesso!"
            )
        else:
            messages.warning(
                request,
                f"Todos os endereços selecionados já estavam {'bloqueados' if novo_status else 'desbloqueados'}."
            )

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
