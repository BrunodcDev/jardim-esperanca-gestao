from django.contrib import admin

from .models import Doacao


@admin.register(Doacao)
class DoacaoAdmin(admin.ModelAdmin):
    list_display = ("item", "quantidade", "unidade", "data_doacao", "doador", "registrado_por")
    list_filter = ("data_doacao",)
    search_fields = ("item", "doador")
