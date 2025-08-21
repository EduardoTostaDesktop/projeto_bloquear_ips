from django.db import models

# Create your models here.
from django.db import models

class Solicitante(models.Model):
    nome = models.CharField(max_length=100)
    contato = models.CharField(max_length=100, blank=True, null=True)  # e-mail, telefone, etc.
    obs = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome
