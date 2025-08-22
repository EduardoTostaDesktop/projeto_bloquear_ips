from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from usuarios.decorators import allowed_roles
from .models import Solicitacao
from listas.models import Lista
from solicitantes.models import Solicitante
from enderecos.models import Endereco
import openpyxl

@allowed_roles(['admin', 'engredes'])
def listar_solicitacoes(request):
    solicitacoes = Solicitacao.objects.all().order_by('-data_criacao')
    return render(request, 'solicitacoes/listar_solicitacoes.html', {'solicitacoes': solicitacoes})

@allowed_roles(['admin', 'engredes'])
def detalhar_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id)
    return render(request, 'solicitacoes/detalhar_solicitacao.html', {'solicitacao': solicitacao})

@allowed_roles(['admin', 'engredes'])
def criar_solicitacao(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')  # "BLOQUEIO" ou "DESBLOQUEIO"
        solicitante_id = request.POST.get('solicitante')
        lista_existente_id = request.POST.get('lista_existente')
        nome_lista = request.POST.get('nome_lista')
        arquivo = request.FILES.get('arquivo_csv')
        desc = request.POST.get('desc')
        obs = request.POST.get('obs')
        usuario = request.user

        if not solicitante_id:
            messages.error(request, "Selecione um solicitante válido.")
            return redirect('solicitacoes:criar_solicitacao')

        # Escolher lista existente ou criar nova lista
        if lista_existente_id:
            lista = Lista.objects.get(id=lista_existente_id)
        elif nome_lista and arquivo:
            lista = Lista.objects.create(
                nome=nome_lista,
                solicitante_id=solicitante_id,
                desc=desc,
                obs=obs,
                criado_por=usuario
            )
            try:
                wb = openpyxl.load_workbook(arquivo)
                ws = wb.active
                for row in ws.iter_rows(min_row=1, values_only=True):
                    if not row or not row[0]:
                        continue
                    endereco_text = str(row[0]).strip()
                    if endereco_text:
                        endereco_obj, created = Endereco.objects.get_or_create(endereco=endereco_text)
                        lista.enderecos.add(endereco_obj)
            except Exception as e:
                messages.error(request, f"Erro ao processar o arquivo Excel: {e}")
                return redirect('solicitacoes:criar_solicitacao')
        else:
            messages.error(request, "Informe uma lista existente ou forneça nome e arquivo para nova lista.")
            return redirect('solicitacoes:criar_solicitacao')

        # Cria a solicitação
        Solicitacao.objects.create(
            lista=lista,
            tipo=tipo,
            solicitante_id=solicitante_id,
            desc=desc,
            obs=obs,
            criado_por=usuario
        )

        messages.success(request, "Solicitação criada com sucesso!")
        return redirect('solicitacoes:listar_solicitacoes')

    # GET
    solicitantes = Solicitante.objects.all()
    listas = Lista.objects.all()
    return render(request, 'solicitacoes/criar_solicitacao.html', {
        'solicitantes': solicitantes,
        'listas': listas
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
