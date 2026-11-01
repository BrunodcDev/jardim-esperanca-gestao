from django import forms

from .models import Beneficiario


class BeneficiarioForm(forms.ModelForm):
    class Meta:
        model = Beneficiario
        fields = ["nome", "bairro", "qtd_pessoas", "situacao"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "bairro": forms.TextInput(attrs={"class": "form-control"}),
            "qtd_pessoas": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "situacao": forms.Select(attrs={"class": "form-select"}),
        }
