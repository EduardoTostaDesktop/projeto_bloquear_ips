from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    TIPOS = [
        ("noc", "NOC"),
        ("engredes", "Engenharia de Redes"),
    ]

    tipo = models.CharField(
        max_length=10,
        choices=TIPOS,
        default="noc"
    )

    def is_noc(self):
        return self.tipo == "noc"

    def is_engredes(self):
        return self.tipo == "engredes"


class Solicitante(models.Model):
    nome = models.CharField(max_length=100)
    criador = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    descricao = models.TextField(null=True, blank=True)
    obs = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nome
