from django.contrib import admin

from .models import ItemEstoque, MovimentacaoEstoque


@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    list_display = ("nome_item", "saldo", "minimo")
    search_fields = ("nome_item",)


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "data_movimentacao",
        "tipo",
        "item",
        "quantidade",
        "saldo_apos",
        "beneficiario",
    )
    list_filter = ("tipo",)
    search_fields = ("item__nome_item",)
    readonly_fields = ("saldo_apos",)
