import datetime

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from beneficiarios.models import Beneficiario
from doacoes.models import Doacao
from estoque.models import ItemEstoque, MovimentacaoEstoque


@pytest.mark.django_db
def test_doacao_aumenta_saldo():
    """RF02: registrar uma doação cria o item e aumenta o saldo."""
    usuario = get_user_model().objects.create_user(username="voluntaria", password="senha123")

    doacao = Doacao.objects.create(
        item="Leite em pó",
        quantidade=12,
        unidade="lata",
        data_doacao=datetime.date(2026, 3, 10),
        doador="Supermercado Bom",
        registrado_por=usuario,
    )

    # Item ainda não existe no estoque: é criado com saldo 0 e depois somado.
    item, criado = ItemEstoque.objects.get_or_create(
        nome_item=doacao.item, defaults={"saldo": 0}
    )
    MovimentacaoEstoque.objects.create(
        tipo="entrada",
        item=item,
        quantidade=doacao.quantidade,
        doacao=doacao,
    )

    item.refresh_from_db()
    assert criado is True
    assert item.saldo == 12


@pytest.mark.django_db
def test_saida_maior_que_saldo_levanta_erro_e_nao_altera_saldo():
    """RF03: saída acima do saldo levanta ValidationError e não altera o saldo."""
    item = ItemEstoque.objects.create(nome_item="Leite em pó", saldo=12, minimo=5)
    beneficiario = Beneficiario.objects.create(
        nome="Ana P.", bairro="Centro", qtd_pessoas=4
    )

    with pytest.raises(ValidationError, match="Quantidade maior que o saldo disponível"):
        MovimentacaoEstoque.objects.create(
            tipo="saida",
            item=item,
            quantidade=20,
            beneficiario=beneficiario,
        )

    item.refresh_from_db()
    assert item.saldo == 12  # saldo inalterado


@pytest.mark.django_db
def test_abaixo_do_minimo():
    """Item com saldo abaixo do mínimo é sinalizado (RF06)."""
    item = ItemEstoque.objects.create(nome_item="Cesta básica", saldo=3, minimo=5)
    assert item.abaixo_do_minimo() is True
