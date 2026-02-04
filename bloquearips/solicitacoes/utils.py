from datetime import datetime, date
from django.contrib import messages
from django.utils import timezone


def parse_data_post(
    request,
    campo_post,
    nome_campo_exibicao,
    permitir_passado=False
):
    """
    Lê uma data do POST, valida e retorna datetime.date ou None.
    """
    data_str = request.POST.get(campo_post, "")
    data_str = data_str.strip() if data_str else ""

    if not data_str:
        return None

    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, f"{nome_campo_exibicao} inválida.")
        return None

    if not permitir_passado and data_obj < date.today():
        messages.error(
            request,
            f"{nome_campo_exibicao} não pode ser anterior à data atual."
        )
        return None

    return data_obj

def aplicar_status_endereco(endereco, tipo, data_desbloqueio, data_renovacao):
    endereco.status = "bloqueado" if tipo == "BLOQUEIO" else "desbloqueado"
    endereco.data_ultima_solicitacao = timezone.now()

    if tipo == "BLOQUEIO":
        endereco.data_desbloqueio = data_desbloqueio
        endereco.data_renovacao = data_renovacao
    else:
        endereco.data_desbloqueio = None
        endereco.data_renovacao = None

    endereco.save()
