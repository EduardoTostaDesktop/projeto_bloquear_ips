from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    TIPOS = [
        ("noc", "NOC"),
        ("engredes", "Engenharia de Redes"),
        ("admin", "Administrador"),
    ]

    tipo = models.CharField(
        max_length=10,
        choices=TIPOS,
        default="noc"
    )

    def save(self, *args, **kwargs):
        if self.tipo == "admin":
            self.is_staff = True
        super().save(*args, **kwargs)

    def is_noc(self):
        return self.tipo == "noc"

    def is_engredes(self):
        return self.tipo == "engredes"
