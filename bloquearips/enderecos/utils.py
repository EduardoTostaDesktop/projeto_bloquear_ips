from enderecos.models import Endereco

def contar_ips_bloqueados():
    """
    Conta IPv4 e IPv6 com status bloqueado
    """
    return Endereco.objects.filter(
        status="bloqueado",
        tipo__in=["ipv4", "ipv6"]
    ).count()


def contar_urls_bloqueadas():
    """
    Conta URLs bloqueadas
    """
    return Endereco.objects.filter(
        status="bloqueado",
        tipo="url"
    ).count()
