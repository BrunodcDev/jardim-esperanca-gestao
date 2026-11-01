from django import forms

from .models import ItemEstoque, MovimentacaoEstoque


class SaidaEstoqueForm(forms.ModelForm):
    item = forms.ModelChoiceField(
        label="Item",
        queryset=ItemEstoque.objects.all(),
        empty_label="Selecione um item",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = MovimentacaoEstoque
        fields = ["beneficiario", "item", "quantidade"]
        widgets = {
            "beneficiario": forms.Select(attrs={"class": "form-select"}),
            "quantidade": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].label_from_instance = (
            lambda obj: f"{obj.nome_item} (saldo: {obj.saldo})"
        )
