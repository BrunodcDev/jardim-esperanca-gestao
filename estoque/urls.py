from django.urls import path

from . import views

app_name = "estoque"

urlpatterns = [
    path("", views.lista_estoque, name="lista"),
    path("saida/", views.registrar_saida, name="saida"),
    path("historico/", views.historico, name="historico"),
]
