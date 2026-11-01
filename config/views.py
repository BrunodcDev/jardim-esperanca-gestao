from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render

from beneficiarios.models import Beneficiario
from doacoes.models import Doacao
from estoque.models import ItemEstoque


@login_required
def dashboard(request):
    """Página inicial pós-login com alerta de estoque baixo (RF06)."""
    itens_baixos = ItemEstoque.objects.filter(saldo__lt=F("minimo")).order_by("nome_item")

    context = {
        "itens_baixos": itens_baixos,
        "itens_falta": itens_baixos.count(),
        "total_beneficiarios_ativos": Beneficiario.objects.filter(situacao="ativa").count(),
        "total_doacoes": Doacao.objects.count(),
    }
    return render(request, "dashboard.html", context)
