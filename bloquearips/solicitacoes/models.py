from django.db import models
from django.conf import settings
from listas.models import Lista
from solicitantes.models import Solicitante
from django.utils import timezone

class Solicitacao(models.Model):
    TIPO_CHOICES = [
        ('BLOQUEIO', 'Bloqueio'),
        ('DESBLOQUEIO', 'Desbloqueio'),
    ]

    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EM_ANDAMENTO', 'Em andamento'),
        ('CONCLUIDA', 'Concluída'),
    ]

    lista = models.ForeignKey(Lista, on_delete=models.CASCADE, related_name='solicitacoes')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='BLOQUEIO')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    enderecos = models.ManyToManyField('enderecos.Endereco', blank=True, related_name='solicitacoes')
    data_prevista = models.DateTimeField(null=True, blank=True)
    data_execucao = models.DateTimeField(null=True, blank=True)
    desc = models.TextField(blank=True, null=True)
    obs = models.TextField(blank=True, null=True)
    solicitante = models.ForeignKey(Solicitante, on_delete=models.PROTECT)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.lista.nome} ({self.status})"
