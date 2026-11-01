from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction


class ItemEstoque(models.Model):
    """Item controlado no estoque da associação."""

    nome_item = models.CharField("Nome do item", max_length=200, unique=True)
    saldo = models.IntegerField("Saldo", default=0)
    minimo = models.IntegerField("Estoque mínimo", default=5)

    class Meta:
        verbose_name = "Item de estoque"
        verbose_name_plural = "Itens de estoque"
        ordering = ["nome_item"]

    def abaixo_do_minimo(self):
        return self.saldo < self.minimo

    def __str__(self):
        return self.nome_item


class MovimentacaoEstoque(models.Model):
    """Entrada ou saída de estoque."""

    TIPO_CHOICES = [
        ("entrada", "Entrada"),
        ("saida", "Saída"),
    ]

    tipo = models.CharField("Tipo", max_length=10, choices=TIPO_CHOICES)
    item = models.ForeignKey(
        ItemEstoque,
        verbose_name="Item",
        on_delete=models.CASCADE,
        related_name="movimentacoes",
    )
    quantidade = models.IntegerField("Quantidade", validators=[MinValueValidator(1)])
    data_movimentacao = models.DateTimeField("Data da movimentação", auto_now_add=True)
    doacao = models.ForeignKey(
        "doacoes.Doacao",
        verbose_name="Doação",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes",
    )
    beneficiario = models.ForeignKey(
        "beneficiarios.Beneficiario",
        verbose_name="Beneficiário",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes",
    )
    saldo_apos = models.IntegerField("Saldo após a movimentação", default=0)

    class Meta:
        verbose_name = "Movimentação de estoque"
        verbose_name_plural = "Movimentações de estoque"
        ordering = ["-data_movimentacao"]

    def clean(self):
        if self.tipo == "entrada" and not self.doacao_id:
            raise ValidationError("Doação é obrigatória para uma entrada de estoque.")
        if self.tipo == "saida" and not self.beneficiario_id:
            raise ValidationError("Beneficiário é obrigatório para uma saída de estoque.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.clean()
            item = self.item
            if self.tipo == "entrada":
                item.saldo += self.quantidade
            elif self.tipo == "saida":
                if self.quantidade > item.saldo:
                    raise ValidationError(
                        f"Quantidade maior que o saldo disponível. "
                        f"Informe um valor até {item.saldo}."
                    )
                item.saldo -= self.quantidade
            item.save(update_fields=["saldo"])
            self.saldo_apos = item.saldo
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.item} ({self.quantidade})"
