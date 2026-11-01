from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from estoque.models import ItemEstoque, MovimentacaoEstoque

from .forms import DoacaoForm
from .models import Doacao


@login_required
def lista_doacoes(request):
    doacoes = Doacao.objects.select_related("registrado_por")
    return render(request, "doacoes/lista.html", {"doacoes": doacoes})


@login_required
def registrar_doacao(request):
    """Registra a doação, cria a entrada de estoque e atualiza o saldo (RF02)."""
    if request.method == "POST":
        form = DoacaoForm(request.POST)
        if form.is_valid():
            doacao = form.save(commit=False)
            doacao.registrado_por = request.user
            with transaction.atomic():
                doacao.save()
                item, _ = ItemEstoque.objects.get_or_create(
                    nome_item=doacao.item, defaults={"saldo": 0}
                )
                MovimentacaoEstoque.objects.create(
                    tipo="entrada",
                    item=item,
                    quantidade=doacao.quantidade,
                    doacao=doacao,
                )
            messages.success(request, "Doação registrada e estoque atualizado.")
            return redirect("doacoes:lista")
    else:
        form = DoacaoForm()

    return render(
        request,
        "doacoes/form.html",
        {"form": form, "titulo": "Registrar Doação"},
    )
