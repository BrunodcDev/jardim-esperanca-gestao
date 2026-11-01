from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from .forms import SaidaEstoqueForm
from .models import ItemEstoque, MovimentacaoEstoque


@login_required
def lista_estoque(request):
    itens = ItemEstoque.objects.all()
    return render(request, "estoque/lista.html", {"itens": itens})


@login_required
def historico(request):
    """Histórico de movimentações: para quem o item foi e de onde veio."""
    movimentacoes = MovimentacaoEstoque.objects.select_related(
        "item", "beneficiario", "doacao"
    )
    return render(request, "estoque/historico.html", {"movimentacoes": movimentacoes})


@login_required
def registrar_saida(request):
    """Registra a saída de estoque e valida se a quantidade não excede o saldo (RF03)."""
    if request.method == "POST":
        form = SaidaEstoqueForm(request.POST)
        if form.is_valid():
            beneficiario = form.cleaned_data["beneficiario"]
            item = form.cleaned_data["item"]
            quantidade = form.cleaned_data["quantidade"]
            try:
                MovimentacaoEstoque.objects.create(
                    tipo="saida",
                    item=item,
                    quantidade=quantidade,
                    beneficiario=beneficiario,
                )
            except ValidationError as e:
                form.add_error("quantidade", e)
            else:
                messages.success(request, "Saída registrada e estoque atualizado.")
                return redirect("estoque:lista")
    else:
        form = SaidaEstoqueForm()

    return render(
        request,
        "estoque/saida.html",
        {"form": form, "titulo": "Registrar Saída de Estoque"},
    )
