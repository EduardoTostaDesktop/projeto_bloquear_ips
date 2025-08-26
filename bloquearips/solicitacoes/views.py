import openpyxl
import datetime
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

        # Cria ou pega a lista
        if lista_existente_id:
            lista = get_object_or_404(Lista, id=lista_existente_id)
        else:
            if not nome_lista:
                messages.error(request, "Você deve informar um nome para a nova lista.")
                return redirect("solicitacoes:criar_solicitacao")

            data_prevista = request.POST.get("data_prevista")
            if data_prevista:
                # Converte para datetime às 00:00 do dia selecionado
                data_prevista_obj = datetime.strptime(data_prevista, "%Y-%m-%d")
            else:
                data_prevista_obj = None

            # Criando nova lista
            lista = Lista.objects.create(
                nome=nome_lista,
                solicitante=solicitante,
                criador=request.user,
                data_prevista_desbloqueio=data_prevista_obj
            )

        # Lista de endereços que serão afetados nesta solicitação
        enderecos_solicitacao = []

        # Adiciona endereços selecionados manualmente
        if enderecos_ids:
            enderecos_selecionados = Endereco.objects.filter(id__in=enderecos_ids)
            lista.enderecos.add(*enderecos_selecionados)
            enderecos_solicitacao.extend(enderecos_selecionados)

        # Processa arquivo xlsx de endereços, se enviado
        if arquivo:
            try:
                wb = openpyxl.load_workbook(arquivo)
                sheet = wb.active
                for row in sheet.iter_rows(values_only=True):
                    endereco_texto = str(row[0]).strip()
                    if endereco_texto:
                        endereco_obj, created = Endereco.objects.get_or_create(endereco=endereco_texto)
                        lista.enderecos.add(endereco_obj)
                        enderecos_solicitacao.append(endereco_obj)
            except Exception as e:
                messages.error(request, f"Erro ao processar o arquivo: {e}")
                return redirect("solicitacoes:criar_solicitacao")

        # Gera o nome da solicitação
        data_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        nome_solicitacao = f"{solicitante.nome} - {lista.nome} - {data_str}"

        # Cria a solicitação
        solicitacao = Solicitacao.objects.create(
            lista=lista,
            tipo=tipo,
            solicitante=solicitante,
            data_prevista=data_prevista if data_prevista else None,
            desc=desc,
            obs=obs,
            criado_por=request.user,
            nome=nome_solicitacao
        )

        # Atualiza o status apenas dos endereços afetados
        novo_status = True if tipo == "BLOQUEIO" else False
        for endereco in lista.enderecos.all():
            endereco.status = novo_status
            endereco.save()


        messages.success(request, "Solicitação criada com sucesso!")
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
