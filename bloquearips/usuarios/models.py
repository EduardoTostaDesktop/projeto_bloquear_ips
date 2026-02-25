from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    TIPOS = [
        ("noc", "NOC"),
        ("engredes", "Engenharia de Redes"),
        ("admin", "Administrador"),
    ]

    nome = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nome completo"
    )

    email = models.EmailField(
        max_length=50,
        unique=True,
        verbose_name="E-mail"
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPOS,
        default="noc"
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.tipo == "admin":
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome or self.username

    def is_noc(self):
        return self.tipo == "noc"

    def is_engredes(self):
        return self.tipo == "engredes"
