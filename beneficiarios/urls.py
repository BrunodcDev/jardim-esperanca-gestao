from django.urls import path

from . import views

app_name = "beneficiarios"

urlpatterns = [
    path("", views.lista_beneficiarios, name="lista"),
    path("novo/", views.cadastrar_beneficiario, name="cadastrar"),
    path("<int:pk>/editar/", views.editar_beneficiario, name="editar"),
]
