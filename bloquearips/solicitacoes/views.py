from django.http import HttpResponse
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
from django.template.loader import render_to_string
from .utils import parse_data_post, aplicar_status_endereco




@allowed_roles(['admin', 'engredes'])
def listar_solicitacoes(request):
    solicitacoes = Solicitacao.objects.all().order_by("-id")
    
    # Gera listas únicas para os filtros
    lista_nomes = Lista.objects.values_list('nome', flat=True).distinct()
    solicitantes = Lista.objects.values_list('solicitante__nome', flat=True).distinct()
    criadores = Lista.objects.values_list('criador__username', flat=True).distinct()

    return render(request, "solicitacoes/listar_solicitacoes.html", {
        "solicitacoes": solicitacoes,
        "lista_nomes": lista_nomes,
        "solicitantes": solicitantes,
        "criadores": criadores,
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
        novo_solicitante_nome = request.POST.get("nome_solicitante")
        novo_solicitante_contato = request.POST.get("contato_solicitante")
        lista_existente_id = request.POST.get("lista_existente")
        nome_lista = request.POST.get("nome_lista")
        enderecos_ids = request.POST.getlist("enderecos")
        data_prevista_desbloqueio = parse_data_post(
            request,
            "data_prevista_desbloqueio",
            "Data prevista de desbloqueio"
        )

        data_prevista_renovacao = parse_data_post(
            request,
            "data_prevista_renovacao",
            "Data prevista de renovação"
        )

        desc = request.POST.get("desc")
        obs = request.POST.get("obs")
        arquivo = request.FILES.get("arquivo")

        # --- Seleciona ou cria solicitante ---
        if novo_solicitante_nome and novo_solicitante_nome.strip() != "":
            solicitante, created = Solicitante.objects.get_or_create(
                nome=novo_solicitante_nome.strip(),
                defaults={"contato": novo_solicitante_contato.strip() if novo_solicitante_contato else ""}
            )
            if created:
                messages.success(request, f"Novo solicitante '{novo_solicitante_nome}' cadastrado com sucesso!")
        elif solicitante_id and solicitante_id.strip() != "":
            solicitante = get_object_or_404(Solicitante, id=solicitante_id)
        else:
            messages.error(request, "Você deve selecionar um solicitante ou cadastrar um novo.")
            return redirect("solicitacoes:criar_solicitacao")

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
                data_prevista_desbloqueio=data_prevista_desbloqueio

            )

        # --- Monta os endereços que farão parte da solicitação ---
        enderecos_solicitacao = []

        if enderecos_ids:
            enderecos_selecionados = Endereco.objects.filter(id__in=enderecos_ids)
            lista.enderecos.add(*enderecos_selecionados)
            enderecos_solicitacao.extend(enderecos_selecionados)

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

        if not enderecos_solicitacao and lista.enderecos.exists():
            enderecos_solicitacao = list(lista.enderecos.all())

        if not enderecos_solicitacao:
            messages.error(request, "Nenhum endereço válido foi selecionado ou encontrado.")
            return redirect("solicitacoes:criar_solicitacao")

        # --- Cria a solicitação ---
        data_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        nome_solicitacao = f"{solicitante.nome} - {lista.nome} - {data_str}"

        solicitacao = Solicitacao.objects.create(
            nome=nome_solicitacao,
            lista=lista,
            tipo=tipo,
            solicitante=solicitante,
            data_prevista_desbloqueio=data_prevista_desbloqueio,
            data_prevista_renovacao=data_prevista_renovacao,
            desc=desc,
            obs=obs,
            criado_por=request.user,
        )

        
        # 🔹 Atualiza também a lista com a nova data, se houver
        if data_prevista_desbloqueio:
            lista.data_prevista_desbloqueio = data_prevista_desbloqueio
            lista.save()

        # --- Atualiza status dos endereços ---
        novo_status = "bloqueado" if tipo == "BLOQUEIO" else "desbloqueado"

        alterados = 0

        for endereco in enderecos_solicitacao:
            aplicar_status_endereco(
                endereco=endereco,
                tipo=tipo,
                data_desbloqueio=data_prevista_desbloqueio,
                data_renovacao=data_prevista_renovacao
            )
            alterados += 1


        if alterados:
            messages.success(
                request,
                f"{alterados} endereço(s) "
                f"{'bloqueado(s)' if novo_status == 'bloqueado' else 'desbloqueado(s)'}"
                "com sucesso!"
            )
        else:
            messages.warning(
                request,
                "Todos os endereços selecionados já estavam "
                f"{'bloqueados' if novo_status == 'bloqueado' else 'desbloqueados'}."
            )

        return redirect("solicitacoes:listar_solicitacoes")
    
    return render(request, "solicitacoes/criar_solicitacao.html", {
    "solicitantes": solicitantes,
    "listas": listas,
    "enderecos": enderecos,
})




@allowed_roles(['admin', 'engredes'])
def editar_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id)

    if request.method == "POST":
        # Campos que podem ser editados
        solicitacao.obs = request.POST.get("obs", solicitacao.obs)
        solicitacao.desc = request.POST.get("desc", solicitacao.desc)

        data_prevista_desbloqueio = request.POST.get("data_prevista_desbloqueio")
        if data_prevista_desbloqueio:
            try:
                # Converte a data para objeto datetime com timezone
                data_prevista_desbloqueio = timezone.make_aware(
                    datetime.strptime(data_prevista_desbloqueio, "%Y-%m-%d")
                )


                # --- VALIDAÇÃO ---
                if data_prevista_desbloqueio < solicitacao.data_criacao:
                    messages.error(
                        request,
                        "A data prevista não pode ser anterior à data de criação da solicitação!"
                    )
                    return redirect("solicitacoes:editar_solicitacao", solicitacao_id=solicitacao.id)

                # Atualiza a solicitação
                solicitacao.data_prevista_desbloqueio = data_prevista_desbloqueio

                # Atualiza também a lista associada
                if solicitacao.lista:
                    solicitacao.lista.data_prevista_desbloqueio = data_prevista_desbloqueio
                    solicitacao.lista.save()


                    # ✅ ATUALIZA TODOS OS ENDEREÇOS DESSA LISTA
                    for endereco in solicitacao.lista.enderecos.all():
                        aplicar_status_endereco(
                            endereco=endereco,
                            tipo=solicitacao.tipo,
                            data_desbloqueio=data_prevista_desbloqueio,
                            data_renovacao=solicitacao.data_prevista_renovacao
                        )



            except ValueError:
                messages.error(request, "Formato de data inválido. Use o formato AAAA-MM-DD.")
                return redirect("solicitacoes:editar_solicitacao", solicitacao_id=solicitacao.id)

        solicitacao.save()
        messages.success(request, "Solicitação, lista e endereços atualizados com sucesso!")
        return redirect("solicitacoes:detalhar_solicitacao", solicitacao_id=solicitacao.id)

    return render(request, "solicitacoes/editar_solicitacao.html", {
        "solicitacao": solicitacao
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


@allowed_roles(['admin', 'engredes'])
def gerar_script(request, solicitacao_id):
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id)

    template = (
        "solicitacoes/scripts/bloqueio.txt"
        if solicitacao.tipo == "BLOQUEIO"
        else "solicitacoes/scripts/desbloqueio.txt"
    )


    content = render_to_string(template, {
        "solicitacao": solicitacao,
        "enderecos": solicitacao.lista.enderecos.all(),
        "data": timezone.localtime().strftime("%d/%m/%Y %H:%M"),
    })

    response = HttpResponse(content, content_type="text/plain")
    response["Content-Disposition"] = (
        f'attachment; filename="solicitacao_{solicitacao.id}.txt"'
    )

    return response
