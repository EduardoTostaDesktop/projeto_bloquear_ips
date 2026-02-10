from datetime import date, datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
import openpyxl
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
        solicitante = request.POST.get('solicitante')
        novo_solicitante_nome = request.POST.get("nome_solicitante")
        novo_solicitante_contato = request.POST.get("contato_solicitante")
        desc = request.POST.get('desc')
        obs = request.POST.get('obs')
        data_prevista_desbloqueio = request.POST.get('data_prevista_desbloqueio')
        arquivo = request.FILES.get('arquivo_csv')
        criador = request.user

        # --- Seleciona ou cria solicitante ---
        if novo_solicitante_nome and novo_solicitante_nome.strip() != "":
            solicitante, created = Solicitante.objects.get_or_create(
                nome=novo_solicitante_nome.strip(),
                defaults={"contato": novo_solicitante_contato.strip() if novo_solicitante_contato else ""}
            )
            if created:
                messages.success(request, f"Novo solicitante '{novo_solicitante_nome}' cadastrado com sucesso!")
        elif solicitante and solicitante.strip() != "":
            solicitante = get_object_or_404(Solicitante, id=solicitante)
        else:
            messages.error(request, "Você deve selecionar um solicitante ou cadastrar um novo.")
            return redirect("listas:criar_lista")

        from datetime import datetime
        if data_prevista_desbloqueio:
            try:
                data_prevista_desbloqueio = datetime.strptime(data_prevista_desbloqueio, "%Y-%m-%d")
            except ValueError:
                messages.error(request, "Formato de data inválido. Use YYYY-MM-DD.")
                return redirect('listas:criar_lista')
        else:
            data_prevista_desbloqueio = None

        lista = Lista.objects.create(
            nome=nome,
            solicitante=solicitante,
            desc=desc,
            obs=obs,
            criador=criador,
            data_prevista_desbloqueio=data_prevista_desbloqueio
        )

        # Processa arquivo Excel **dentro do POST**
        if arquivo:
            try:
                import openpyxl
                wb = openpyxl.load_workbook(arquivo)
                ws = wb.active

                for row in ws.iter_rows(min_row=1, values_only=True):
                    if not row or not row[0]:
                        continue
                    endereco_text = str(row[0]).strip()
                    if endereco_text:
                        endereco_obj, created = Endereco.objects.get_or_create(
                            endereco=endereco_text
                        )
                        lista.enderecos.add(endereco_obj)

            except Exception as e:
                messages.error(request, f"Erro ao processar o arquivo Excel: {e}")

        messages.success(request, "Lista criada com sucesso!")
        return redirect('listas:listar_listas')

    # GET
    solicitantes = Solicitante.objects.all()
    return render(request, 'listas/criar_lista.html', {'solicitantes': solicitantes})

from datetime import datetime, date
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from usuarios.decorators import allowed_roles
from .models import Lista
from solicitantes.models import Solicitante


@allowed_roles(['admin', 'engredes'])
def editar_lista(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id)

    if request.method == 'POST':
        lista.nome = request.POST.get('nome')
        lista.desc = request.POST.get('desc')
        lista.obs = request.POST.get('obs')

        # 🔹 Solicitan​te (FK)
        solicitante_id = request.POST.get('solicitante')
        if solicitante_id:
            lista.solicitante = get_object_or_404(Solicitante, id=solicitante_id)
        else:
            messages.error(request, "Solicitante é obrigatório.")
            return redirect('listas:editar_lista', lista_id=lista.id)

        # 🔹 Data prevista de desbloqueio
        data_prevista = request.POST.get('data_prevista_desbloqueio')

        if data_prevista:
            try:
                data_convertida = datetime.strptime(
                    data_prevista, "%Y-%m-%d"
                ).date()

                if data_convertida < date.today():
                    messages.error(
                        request,
                        "A data prevista de desbloqueio não pode ser anterior à data atual."
                    )
                    return redirect('listas:editar_lista', lista_id=lista.id)

                lista.data_prevista_desbloqueio = data_convertida

            except ValueError:
                messages.error(request, "Formato de data inválido. Use YYYY-MM-DD.")
                return redirect('listas:editar_lista', lista_id=lista.id)
        else:
            lista.data_prevista_desbloqueio = None

        lista.save()
        messages.success(request, "Lista atualizada com sucesso!")
        return redirect('listas:detalhar_lista', lista_id=lista.id)

    # GET
    solicitantes = Solicitante.objects.all()
    return render(
        request,
        'listas/editar_lista.html',
        {
            'lista': lista,
            'solicitantes': solicitantes
        }
    )



@allowed_roles(['admin', 'engredes'])
def excluir_lista(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id)

    # Verifica se existem solicitações para essa lista
    if lista.solicitacoes.exists():
        messages.error(
            request,
            f'A lista "{lista.nome}" não pode ser excluída, pois possui solicitações vinculadas.'
        )
        return redirect('listas:listar_listas')

    lista.delete()
    messages.success(request, f'Lista "{lista.nome}" excluída com sucesso!')
    return redirect('listas:listar_listas')


@allowed_roles(['admin', 'engredes'])
def excluir_listas_massa(request):
    if request.method == "POST":
        ids = request.POST.getlist('ids')

        if ids:
            listas = Lista.objects.filter(id__in=ids)
            listas_com_solicitacoes = []
            listas_excluidas = []

            for lista in listas:
                if lista.solicitacoes.exists():
                    listas_com_solicitacoes.append(lista.nome)
                else:
                    lista.delete()
                    listas_excluidas.append(lista.nome)

            # Mensagens para feedback do usuário
            if listas_excluidas:
                messages.success(
                    request,
                    f'{len(listas_excluidas)} lista(s) excluída(s) com sucesso!'
                )

            if listas_com_solicitacoes:
                nomes = ", ".join(listas_com_solicitacoes)
                messages.warning(
                    request,
                    f"As seguintes listas não puderam ser excluídas pois possuem solicitações vinculadas: {nomes}"
                )
        else:
            messages.warning(request, "Nenhuma lista selecionada para exclusão.")

    return redirect('listas:listar_listas')




