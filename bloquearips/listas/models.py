from django.db import models
from django.conf import settings

class Lista(models.Model):
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, null=True)

    # Data padrão de desbloqueio da lista (opcional).
    # Se um endereço não trouxer sua própria data, herdará esta.
    data_desbloqueio_padrao = models.DateField(blank=True, null=True)

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='listas_criadas'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
