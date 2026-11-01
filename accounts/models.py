from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuário do sistema com perfil de acesso."""

    PERFIL_CHOICES = [
        ("coordenadora", "Coordenadora"),
        ("voluntario", "Voluntário"),
    ]

    perfil = models.CharField(
        "Perfil",
        max_length=20,
        choices=PERFIL_CHOICES,
        default="voluntario",
    )

    @property
    def is_coordenadora(self):
        """Coordenadoras (e superusuários) têm acesso amplo ao sistema."""
        return self.perfil == "coordenadora" or self.is_superuser

    def __str__(self):
        return self.get_full_name() or self.username
