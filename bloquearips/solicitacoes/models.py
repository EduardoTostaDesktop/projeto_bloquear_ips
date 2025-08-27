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

    lista = models.ForeignKey(Lista, on_delete=models.CASCADE, related_name='solicitacoes')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='BLOQUEIO')
    nome = models.CharField(max_length=255, blank=True)  # Novo campo nome
    data_prevista = models.DateTimeField(null=True, blank=True)
    desc = models.TextField(blank=True, null=True)
    obs = models.TextField(blank=True, null=True)
    solicitante = models.ForeignKey(Solicitante, on_delete=models.PROTECT)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Gera o nome automaticamente se estiver vazio
        if not self.nome:
            data_str = timezone.now().strftime("%d/%m/%Y %H:%M")
            self.nome = f"{self.solicitante.nome} - {self.lista.nome} - {data_str}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
