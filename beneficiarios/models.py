from django.core.validators import MinValueValidator
from django.db import models


class Beneficiario(models.Model):
    """Família/beneficiário atendido pela associação."""

    SITUACAO_CHOICES = [
        ("ativa", "Ativa"),
        ("inativa", "Inativa"),
    ]

    nome = models.CharField("Nome", max_length=200)
    bairro = models.CharField("Bairro", max_length=200)
    qtd_pessoas = models.IntegerField(
        "Quantidade de pessoas",
        validators=[MinValueValidator(1)],
    )
    situacao = models.CharField(
        "Situação",
        max_length=10,
        choices=SITUACAO_CHOICES,
        default="ativa",
    )
    data_cadastro = models.DateTimeField("Data de cadastro", auto_now_add=True)

    class Meta:
        verbose_name = "Beneficiário"
        verbose_name_plural = "Beneficiários"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
