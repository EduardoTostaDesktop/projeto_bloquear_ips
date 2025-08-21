import ipaddress
from django.contrib import messages
from urllib.parse import urlparse
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404, redirect, render

from enderecos.forms import EnderecoForm
from enderecos.models import Endereco

@login_required
def painel_enderecos(request):
    return render(request, "enderecos/painel_enderecos.html")


@login_required
def perfil_endereco(request, endereco_id):
    endereco = get_object_or_404(Endereco, id=endereco_id)
    return render(request, "enderecos/perfil_endereco.html", {"endereco": endereco})


def detectar_tipo(endereco):
    try:
        ip = ipaddress.ip_address(endereco)
        if ip.version == 4:
            return "IPv4"
        else:
            return "IPv6"
    except ValueError:
        # Se não for IP, vamos tentar considerar como URL
        try:
            result = urlparse(endereco)
            if result.scheme and result.netloc:
                return "URL"
        except:
            pass
    # Padrão se não for nem IP nem URL
    return "DESCONHECIDO"


def cadastrar_endereco(request):
    if request.method == "POST":
        form = EnderecoForm(request.POST)
        if form.is_valid():
            endereco_obj = form.save(commit=False)
            endereco_obj.tipo = detectar_tipo(endereco_obj.endereco)
            endereco_obj.save()
            messages.success(request, "Endereço cadastrado com sucesso!")
            return redirect("listar_enderecos")
    else:
        form = EnderecoForm()
    return render(request, "enderecos/form_endereco.html", {"form": form, "titulo": "Cadastrar Endereço"})


def editar_endereco(request, endereco_id):
    endereco = get_object_or_404(Endereco, id=endereco_id)
    if request.method == "POST":
        form = EnderecoForm(request.POST, instance=endereco)
        if form.is_valid():
            endereco_obj = form.save(commit=False)
            endereco_obj.tipo = detectar_tipo(endereco_obj.endereco)
            endereco_obj.save()
            messages.success(request, "Endereço atualizado com sucesso!")
            return redirect("listar_enderecos")
    else:
        form = EnderecoForm(instance=endereco)
    return render(request, "enderecos/form_endereco.html", {"form": form, "titulo": "Editar Endereço"})



from django.db.models import Q

@login_required
def listar_enderecos(request):
    search_query = request.GET.get("search", "")
    tipo_filter = request.GET.get("tipo", "")
    status_filter = request.GET.get("status", "")

    enderecos = Endereco.objects.all()

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

    context = {
        "enderecos": enderecos,
        "search_query": search_query,
        "tipo_filter": tipo_filter,
        "status_filter": status_filter,
    }
    return render(request, "enderecos/listar_enderecos.html", context)


def excluir_endereco(request, endereco_id):
    endereco = get_object_or_404(Endereco, id=endereco_id)
    endereco.delete()
    messages.success(request, "Endereço excluído com sucesso!")
    return redirect("listar_enderecos")

