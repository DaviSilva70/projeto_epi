from django.contrib import admin

from .models import Colaborador, EPI, RegistroEPI


@admin.register(EPI)
class EPIAdmin(admin.ModelAdmin):
    list_display = ("ca", "descricao", "created_at")
    search_fields = ("ca", "descricao")
    ordering = ("ca",)


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ("nome_completo", "matricula", "funcao", "setor", "created_at")
    search_fields = ("nome_completo", "matricula", "funcao", "setor")
    list_filter = ("setor", "funcao")
    ordering = ("nome_completo",)


@admin.register(RegistroEPI)
class RegistroEPIAdmin(admin.ModelAdmin):
    list_display = ("colaborador", "epi", "quantidade", "data_retirada")
    search_fields = (
        "colaborador__nome_completo",
        "colaborador__matricula",
        "epi__ca",
        "epi__descricao",
    )
    list_filter = ("data_retirada",)
    autocomplete_fields = ("colaborador", "epi")
    ordering = ("-data_retirada",)
