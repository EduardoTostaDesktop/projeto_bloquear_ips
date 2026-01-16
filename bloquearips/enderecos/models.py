from django.db import models
from django.core.validators import URLValidator
import ipaddress

class Endereco(models.Model):
    TIPOS = [
        ("ipv4", "IPv4"),
        ("ipv6", "IPv6"),
        ("url", "URL"),
    ]
    STATUS_CHOICES = [
        ("bloqueado", "Bloqueado"),
        ("desbloqueado", "Desbloqueado"),
        ("excluido", "Excluído"),
    ]

    endereco = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=10, choices=TIPOS, editable=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="desbloqueado"
    )  
    nome = models.CharField(max_length=100, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    obs = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_desbloqueio = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Detectar tipo automaticamente
        try:
            ip_obj = ipaddress.ip_address(self.endereco)
            self.tipo = "ipv4" if ip_obj.version == 4 else "ipv6"
        except ValueError:
            validator = URLValidator()
            try:
                validator(self.endereco)
                self.tipo = "url"
            except:
                self.tipo = "url"  # Caso não seja IP válido, assume URL

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.endereco} ({self.tipo}) - {self.get_status_display()}"
