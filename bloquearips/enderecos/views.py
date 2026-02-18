import ipaddress
from django.contrib import messages
from urllib.parse import urlparse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from usuarios.decorators import allowed_roles
from enderecos.forms import EnderecoForm
from enderecos.models import Endereco
from django.db.models import Prefetch
from solicitacoes.models import Solicitacao
from django.utils import timezone
from solicitacoes.utils import aplicar_status_endereco


@login_required
def perfil_endereco(request, endereco_id):
    endereco = get_object_or_404(Endereco, id=endereco_id)

    solicitacoes = (
        Solicitacao.objects
        .filter(lista__enderecos=endereco)
        .select_related("lista", "solicitante")
        .order_by("-data_criacao")
    )

    return render(
        request,
        "enderecos/perfil_endereco.html",
        {
            "endereco": endereco,
            "solicitacoes": solicitacoes,
        }
    )

from enderecos.utils import (
    contar_ips_bloqueados,
    contar_urls_bloqueadas
)

@login_required
def listar_enderecos(request):
    search_query = request.GET.get("search", "")
    tipo_filter = request.GET.get("tipo", "")
    status_filter = request.GET.get("status", "")

    enderecos = Endereco.objects.exclude(status="excluido")

    if search_query:
        enderecos = enderecos.filter(
            Q(endereco__icontains=search_query) |
            Q(nome__icontains=search_query) |
            Q(desc__icontains=search_query) |
            Q(obs__icontains=search_query)
        )

    if tipo_filter:
        enderecos = enderecos.filter(tipo=tipo_filter)

    if status_filter:
        enderecos = enderecos.filter(status=status_filter == "bloqueado")

    # 🔢 CONTADORES
    dominios_bloqueados = Endereco.objects.filter(
        tipo="url",
        status="bloqueado"
    ).count()

    ips_bloqueados = Endereco.objects.filter(
        tipo__in=["ipv4", "ipv6"],
        status="bloqueado"
    ).count()

    context = {
        "enderecos": enderecos,
        "dominios_bloqueados": dominios_bloqueados,
        "ips_bloqueados": ips_bloqueados,
    }


    return render(request, "enderecos/listar_enderecos.html", context)



def detectar_tipo(endereco):
    try:
        ip = ipaddress.ip_address(endereco)
        return "ipv4" if ip.version == 4 else "ipv6"
    except ValueError:
        try:
            result = urlparse(endereco)
            if result.scheme and result.netloc:
                return "url"
        except:
            pass
    return "desconhecido"



@allowed_roles(['admin', 'engredes'])
def massa_enderecos(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids')
        acao = request.POST.get('acao')

        if not ids:
            messages.warning(request, "Nenhum endereço selecionado para ação.")
            return redirect('listar_enderecos')

        enderecos = Endereco.objects.filter(id__in=ids)

        for endereco in enderecos:
            if acao == 'bloquear':
                aplicar_status_endereco(
                    endereco=endereco,
                    tipo="BLOQUEIO",
                    data_desbloqueio=endereco.data_desbloqueio,
                    data_renovacao=endereco.data_renovacao
                )

            elif acao == 'desbloquear':
                aplicar_status_endereco(
                    endereco=endereco,
                    tipo="DESBLOQUEIO",
                    data_desbloqueio=None,
                    data_renovacao=None
                )

            elif acao == 'excluir':
                endereco.status = "excluido"
                endereco.save()

        messages.success(request, f'Ação "{acao}" realizada com sucesso!')

    return redirect('enderecos:listar_enderecos')



@allowed_roles(['admin', 'engredes'])
def cadastrar_endereco(request):
    if request.method == "POST":
        form = EnderecoForm(request.POST)
        if form.is_valid():
            endereco_obj = form.save(commit=False)
            endereco_obj.tipo = detectar_tipo(endereco_obj.endereco)
            endereco_obj.save()
            messages.success(request, "Endereço cadastrado com sucesso!")
            return redirect("enderecos:listar_enderecos")
    else:
        form = EnderecoForm()
    return render(request, "enderecos/form_endereco.html", {"form": form, "titulo": "Cadastrar Endereço"})

@allowed_roles(['admin', 'engredes'])
def editar_endereco(request, endereco_id):
    endereco = get_object_or_404(Endereco, id=endereco_id)

    if request.method == "POST":
        form = EnderecoForm(request.POST, instance=endereco)

        if form.is_valid():
            endereco_obj = form.save(commit=False)
            endereco_obj.tipo = detectar_tipo(endereco_obj.endereco)
            endereco_obj.save()

            messages.success(request, "Endereço atualizado com sucesso!")
            return redirect("enderecos:listar_enderecos")
        else:
            print("❌ FORM INVÁLIDO")
            print(form.errors)  # 🔥 ISSO É O MAIS IMPORTANTE
    else:
        form = EnderecoForm(instance=endereco)

    return render(
        request,
        "enderecos/form_endereco.html",
        {"form": form, "titulo": "Editar Endereço"}
    )



@allowed_roles(['admin', 'engredes'])
def excluir_endereco(request, endereco_id):
    endereco = get_object_or_404(Endereco, id=endereco_id)
    endereco.status = "excluido"
    endereco.save()
    messages.success(request, "Endereço excluído com sucesso!")
    return redirect("enderecos:listar_enderecos")

