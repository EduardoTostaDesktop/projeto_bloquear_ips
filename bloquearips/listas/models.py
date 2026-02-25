from django.db import models
from django.conf import settings  # Para referenciar o model de usuários
from enderecos.models import Endereco  # Importa o model de Endereco

class Lista(models.Model):
    nome = models.CharField(max_length=100)
    solicitante = models.ForeignKey(
        'solicitantes.Solicitante',
        on_delete=models.PROTECT
    )
    data_registro = models.DateTimeField(auto_now_add=True)
    desc = models.TextField(max_length=100,blank=True, null=True)
    obs = models.TextField(max_length=100, blank=True, null=True)
    criador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    data_prevista_desbloqueio = models.DateTimeField(blank=True, null=True)

    # Relação ManyToMany com Endereco
    enderecos = models.ManyToManyField(Endereco, related_name="listas", blank=True)

    def __str__(self):
        return f"{self.nome} ({self.solicitante})"
