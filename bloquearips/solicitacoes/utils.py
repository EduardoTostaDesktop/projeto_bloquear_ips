from datetime import datetime, date, timezone
from django.contrib import messages

class DataInvalidaError(Exception):
    pass


def parse_data_post(
    request,
    campo_post,
    nome_campo_exibicao,
    permitir_passado=False
):
    data_str = request.POST.get(campo_post, "")
    data_str = data_str.strip() if data_str else ""

    if not data_str:
        return None

    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, f"{nome_campo_exibicao} inválida.")
        raise DataInvalidaError()

    if not permitir_passado and data_obj < date.today():
        messages.error(
            request,
            f"{nome_campo_exibicao} não pode ser anterior à data atual."
        )
        raise DataInvalidaError()

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
