import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_voluntario_nao_acessa_relatorios(client):
    """RNF01: voluntário não deve acessar os relatórios."""
    User.objects.create_user(
        username="voluntaria", password="senha123", perfil="voluntario"
    )
    client.login(username="voluntaria", password="senha123")

    response = client.get(reverse("relatorios:relatorio"))

    assert response.status_code == 302
    assert response.url == reverse("dashboard")


@pytest.mark.django_db
def test_coordenadora_acessa_relatorios(client):
    """RNF01: coordenadora tem acesso aos relatórios."""
    User.objects.create_user(
        username="coordenadora", password="senha123", perfil="coordenadora"
    )
    client.login(username="coordenadora", password="senha123")

    response = client.get(reverse("relatorios:relatorio"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_voluntario_acessa_historico_estoque(client):
    """Voluntário precisa ver o histórico de saídas (para quem o item foi)."""
    User.objects.create_user(
        username="voluntaria", password="senha123", perfil="voluntario"
    )
    client.login(username="voluntaria", password="senha123")

    response = client.get(reverse("estoque:historico"))

    assert response.status_code == 200
