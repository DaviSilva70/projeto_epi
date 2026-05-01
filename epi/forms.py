from datetime import date

from django import forms
from django.core.validators import FileExtensionValidator
from .models import EPI, Colaborador, RegistroEPI, DevolucaoEPI


class EPIForm(forms.ModelForm):
    class Meta:
        model = EPI
        fields = ["ca", "descricao", "foto", "quantidade_em_estoque", "validade_ca"]
        widgets = {
            "ca": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: 12345"}
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descrição completa do EPI",
                }
            ),
            "foto": forms.FileInput(attrs={"class": "form-control"}),
            "quantidade_em_estoque": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "value": 0}
            ),
            "validade_ca": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def clean_validade_ca(self):
        validade = self.cleaned_data.get("validade_ca")
        if validade and validade < date.today():
            raise forms.ValidationError("A data de validade do CA não pode ser anterior a hoje.")
        return validade

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")
        if foto:
            allowed_extensions = ["jpg", "jpeg", "png", "webp"]
            validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
            try:
                validator(foto)
            except forms.ValidationError:
                raise forms.ValidationError(
                    "Formato não permitido. Use: jpg, jpeg, png ou webp"
                )

            max_size = 5 * 1024 * 1024
            if foto.size > max_size:
                raise forms.ValidationError("Arquivo muito grande (max 5MB)")

        return foto


class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ["nome_completo", "matricula", "funcao", "setor"]
        widgets = {
            "nome_completo": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nome completo"}
            ),
            "matricula": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Matrícula"}
            ),
            "funcao": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Função"}
            ),
            "setor": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Setor"}
            ),
        }


class RegistroEPIForm(forms.ModelForm):
    class Meta:
        model = RegistroEPI
        fields = ["colaborador", "epi", "quantidade"]
        widgets = {
            "colaborador": forms.Select(attrs={"class": "form-select"}),
            "epi": forms.Select(attrs={"class": "form-select"}),
            "quantidade": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "value": 1}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        epi = cleaned_data.get("epi")
        quantidade = cleaned_data.get("quantidade", 1)

        if epi:
            if not epi.is_ca_valido:
                raise forms.ValidationError(
                    f"O CA do EPI {epi.ca} está vencido em {epi.validade_ca.strftime('%d/%m/%Y')}. Não é possível registrar a retirada."
                )

            if epi.quantidade_em_estoque < quantidade:
                raise forms.ValidationError(
                    f"Estoque insuficiente. Disponível: {epi.quantidade_em_estoque} unidades."
                )

        return cleaned_data


class DevolucaoEPIForm(forms.ModelForm):
    class Meta:
        model = DevolucaoEPI
        fields = ["quantidade_devolvida", "observacao"]
        widgets = {
            "quantidade_devolvida": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "observacao": forms.Textarea(
                attrs={"class": "form-control", "rows": 2, "placeholder": "Observação opcional"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.registro = kwargs.pop("registro", None)
        super().__init__(*args, **kwargs)

    def clean_quantidade_devolvida(self):
        quantidade = self.cleaned_data.get("quantidade_devolvida", 1)
        if self.registro and quantidade > self.registro.quantidade:
            raise forms.ValidationError(
                f"A quantidade devolvida não pode exceder a quantidade retirada ({self.registro.quantidade})."
            )
        return quantidade
