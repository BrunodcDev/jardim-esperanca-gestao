from django import forms

from .models import Doacao


class DoacaoForm(forms.ModelForm):
    data_doacao = forms.DateField(
        label="Data da doação",
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    class Meta:
        model = Doacao
        fields = ["item", "quantidade", "unidade", "data_doacao", "doador"]
        widgets = {
            "item": forms.TextInput(attrs={"class": "form-control"}),
            "quantidade": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "unidade": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "kg, lata, unidade"}
            ),
            "doador": forms.TextInput(attrs={"class": "form-control"}),
        }
