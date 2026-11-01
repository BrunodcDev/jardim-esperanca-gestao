from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Doacao(models.Model):
    """Doação recebida pela associação."""

    item = models.CharField("Item", max_length=200)
    quantidade = models.IntegerField("Quantidade", validators=[MinValueValidator(1)])
    unidade = models.CharField("Unidade", max_length=50)
    data_doacao = models.DateField("Data da doação")
    doador = models.CharField("Doador", max_length=200, blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Registrado por",
        on_delete=models.PROTECT,
        related_name="doacoes",
    )

    class Meta:
        verbose_name = "Doação"
        verbose_name_plural = "Doações"
        ordering = ["-data_doacao"]

    def __str__(self):
        return f"{self.item} — {self.quantidade} {self.unidade}"
