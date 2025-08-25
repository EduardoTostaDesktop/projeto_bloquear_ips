from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from usuarios.decorators import allowed_roles
from .models import Solicitacao
from listas.models import Lista
from solicitantes.models import Solicitante
from enderecos.models import Endereco
import openpyxl
from datetime import datetime
from django.utils import timezone



@allowed_roles(['admin', 'engredes'])
def listar_solicitacoes(request):
    solicitacoes = Solicitacao.objects.all().order_by("-id")  # 🔹 pega todas as solicitações
    return render(request, "solicitacoes/listar_solicitacoes.html", {
        "solicitacoes": solicitacoes
    })

@allowed_roles(['admin', 'engredes'])
def detalhar_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id)
    return render(request, 'solicitacoes/detalhar_solicitacao.html', {'solicitacao': solicitacao})

@allowed_roles(['admin', 'engredes'])
def criar_solicitacao(request):
    if request.method == "POST":
        tipo = request.POST.get("tipo") or "BLOQUEIO"
        status = "PENDENTE"
        solicitante_id = request.POST.get("solicitante")
        desc = request.POST.get("desc")
        obs = request.POST.get("obs")
        data_prevista = request.POST.get("data_prevista") or None

        # Valida solicitante
        if not solicitante_id:
            messages.error(request, "Selecione um solicitante válido.")
            return redirect("solicitacoes:criar_solicitacao")
        solicitante = get_object_or_404(Solicitante, id=solicitante_id)

        lista = None
        enderecos_ids = request.POST.getlist("enderecos")  # IDs de endereços individuais
        enderecos_individuais = Endereco.objects.filter(id__in=enderecos_ids) if enderecos_ids else []

        arquivo = request.FILES.get("arquivo_csv")
        lista_existente_id = request.POST.get("lista_existente")

        # Criar nova lista a partir do arquivo
        if arquivo:
            lista_nome = f"Lista Solicitação {tipo} - {datetime.now().strftime('%d%m%Y_%H%M')}"
            lista = Lista.objects.create(
                nome=lista_nome,
                solicitante=solicitante,
                desc=desc,
                obs=obs,
                criador=request.user
            )
            try:
                import openpyxl
                wb = openpyxl.load_workbook(arquivo)
                ws = wb.active
                for row in ws.iter_rows(min_row=1, values_only=True):
                    if row and row[0]:
                        endereco_text = str(row[0]).strip()
                        endereco_obj, _ = Endereco.objects.get_or_create(endereco=endereco_text)
                        lista.enderecos.add(endereco_obj)
            except Exception as e:
                messages.error(request, f"Erro ao processar o arquivo Excel: {e}")
                lista.delete()
                return redirect("solicitacoes:criar_solicitacao")

        # Selecionar lista existente
        elif lista_existente_id:
            lista = get_object_or_404(Lista, id=lista_existente_id)

        # Cria a solicitação
        solicitacao = Solicitacao.objects.create(
            lista=lista,
            tipo=tipo,
            status=status,
            solicitante=solicitante,
            desc=desc,
            obs=obs,
            data_prevista=data_prevista,
            criado_por=request.user
        )

        # Adiciona endereços individuais selecionados
        if enderecos_individuais:
            solicitacao.enderecos.add(*enderecos_individuais)

        # Executa bloqueio/desbloqueio para todos os endereços da solicitação
        todos_enderecos = list(enderecos_individuais)
        if lista:
            todos_enderecos += list(lista.enderecos.all())

        for endereco in todos_enderecos:
            endereco.status = True if tipo == "BLOQUEIO" else False
            endereco.save()

        # Atualiza data_execucao e status da solicitação
        solicitacao.data_execucao = timezone.now()
        solicitacao.status = "CONCLUIDA"
        solicitacao.save()

        messages.success(request, "Solicitação criada e endereços atualizados com sucesso!")
        return redirect("solicitacoes:listar_solicitacoes")

    # GET
    solicitantes = Solicitante.objects.all()
    listas = Lista.objects.all()
    enderecos = Endereco.objects.all()
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
