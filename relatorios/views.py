import csv
import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render

from accounts.decorators import coordenadora_required
from beneficiarios.models import Beneficiario
from doacoes.models import Doacao
from estoque.models import MovimentacaoEstoque


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


@coordenadora_required
def relatorio(request):
    """Relatório por período com totais e exportação CSV (RF04)."""
    data_inicio = _parse_date(request.GET.get("data_inicio"))
    data_fim = _parse_date(request.GET.get("data_fim"))

    movimentacoes = MovimentacaoEstoque.objects.select_related(
        "item", "beneficiario", "doacao"
    ).order_by("-data_movimentacao")
    doacoes = Doacao.objects.all()

    if data_inicio:
        movimentacoes = movimentacoes.filter(data_movimentacao__date__gte=data_inicio)
        doacoes = doacoes.filter(data_doacao__gte=data_inicio)
    if data_fim:
        movimentacoes = movimentacoes.filter(data_movimentacao__date__lte=data_fim)
        doacoes = doacoes.filter(data_doacao__lte=data_fim)

    total_beneficiarios_ativos = Beneficiario.objects.filter(situacao="ativa").count()
    total_doacoes = doacoes.count()
    total_entradas = movimentacoes.filter(tipo="entrada").aggregate(
        total=Sum("quantidade")
    )["total"] or 0
    total_saidas = movimentacoes.filter(tipo="saida").aggregate(
        total=Sum("quantidade")
    )["total"] or 0

    if request.GET.get("export") == "csv":
        return _exportar_csv(movimentacoes)

    context = {
        "data_inicio": request.GET.get("data_inicio", ""),
        "data_fim": request.GET.get("data_fim", ""),
        "total_beneficiarios_ativos": total_beneficiarios_ativos,
        "total_doacoes": total_doacoes,
        "total_entradas": total_entradas,
        "total_saidas": total_saidas,
        "movimentacoes": movimentacoes,
    }
    return render(request, "relatorios/relatorio.html", context)


def _exportar_csv(movimentacoes):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="relatorio_estoque.csv"'
    response.write("\ufeff")  # BOM para o Excel reconhecer UTF-8

    writer = csv.writer(response)
    writer.writerow(["Data", "Tipo", "Item", "Quantidade", "Saldo após", "Origem/Destino"])

    for m in movimentacoes:
        if m.tipo == "entrada" and m.doacao:
            origem = m.doacao.doador or "Doação"
        elif m.tipo == "saida" and m.beneficiario:
            origem = m.beneficiario.nome
        else:
            origem = ""
        writer.writerow(
            [
                m.data_movimentacao.strftime("%d/%m/%Y %H:%M"),
                m.get_tipo_display(),
                m.item.nome_item,
                m.quantidade,
                m.saldo_apos,
                origem,
            ]
        )

    return response
