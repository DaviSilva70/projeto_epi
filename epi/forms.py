from django import forms
from django.core.validators import FileExtensionValidator
from .models import EPI, Colaborador, RegistroEPI


class EPIForm(forms.ModelForm):
    class Meta:
        model = EPI
        fields = ["ca", "descricao", "foto"]
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
        }

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
