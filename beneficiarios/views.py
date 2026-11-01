from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BeneficiarioForm
from .models import Beneficiario


@login_required
def lista_beneficiarios(request):
    query = request.GET.get("q", "").strip()
    beneficiarios = Beneficiario.objects.all()
    if query:
        beneficiarios = beneficiarios.filter(nome__icontains=query)

    return render(
        request,
        "beneficiarios/lista.html",
        {"beneficiarios": beneficiarios, "query": query},
    )


@login_required
def cadastrar_beneficiario(request):
    if request.method == "POST":
        form = BeneficiarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Beneficiário cadastrado com sucesso.")
            return redirect("beneficiarios:lista")
    else:
        form = BeneficiarioForm()

    return render(
        request,
        "beneficiarios/form.html",
        {"form": form, "titulo": "Cadastrar Beneficiário"},
    )


@login_required
def editar_beneficiario(request, pk):
    beneficiario = get_object_or_404(Beneficiario, pk=pk)
    if request.method == "POST":
        form = BeneficiarioForm(request.POST, instance=beneficiario)
        if form.is_valid():
            form.save()
            messages.success(request, "Beneficiário atualizado com sucesso.")
            return redirect("beneficiarios:lista")
    else:
        form = BeneficiarioForm(instance=beneficiario)

    return render(
        request,
        "beneficiarios/form.html",
        {"form": form, "titulo": "Editar Beneficiário"},
    )
