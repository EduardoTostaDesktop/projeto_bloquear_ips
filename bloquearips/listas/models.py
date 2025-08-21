from django.db import models
from django.conf import settings  # Para referenciar o model de usuários

class Lista(models.Model):
    nome = models.CharField(max_length=100)
    solicitante = models.ForeignKey(
        'solicitantes.Solicitante',  # Supondo que você tenha um app "solicitantes"
        on_delete=models.PROTECT
    )
    data_registro = models.DateTimeField(auto_now_add=True)
    desc = models.TextField(blank=True, null=True)
    obs = models.TextField(blank=True, null=True)
    criador = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Para relacionar com o usuário do Django
        on_delete=models.PROTECT
    )
    data_prevista_desbloqueio = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.solicitante})"
