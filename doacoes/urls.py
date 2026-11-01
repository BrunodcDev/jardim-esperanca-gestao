from django.urls import path

from . import views

app_name = "doacoes"

urlpatterns = [
    path("", views.lista_doacoes, name="lista"),
    path("nova/", views.registrar_doacao, name="nova"),
]
