"""Rotas principais do projeto Jardim Esperança."""

from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", views.dashboard, name="dashboard"),
    path("beneficiarios/", include("beneficiarios.urls")),
    path("doacoes/", include("doacoes.urls")),
    path("estoque/", include("estoque.urls")),
    path("relatorios/", include("relatorios.urls")),
]
