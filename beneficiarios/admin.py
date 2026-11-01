from django.contrib import admin

from .models import Beneficiario


@admin.register(Beneficiario)
class BeneficiarioAdmin(admin.ModelAdmin):
    list_display = ("nome", "bairro", "qtd_pessoas", "situacao", "data_cadastro")
    list_filter = ("situacao", "bairro")
    search_fields = ("nome", "bairro")
