from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("epi/", views.cadastrar_epi, name="cadastrar_epi"),
    path("colaborador/", views.cadastrar_colaborador, name="cadastrar_colaborador"),
    path(
        "colaborador/editar/<int:id>/",
        views.editar_colaborador,
        name="editar_colaborador",
    ),
    path(
        "colaborador/deletar/<int:id>/",
        views.deletar_colaborador,
        name="deletar_colaborador",
    ),
    path("registrar/", views.registrar_retirada, name="registrar_retirada"),
    path("buscar/", views.buscar_epis_colaborador, name="buscar_epis"),
    path("pdf/", views.gerar_pdf, name="gerar_pdf"),
    path("exportar/excel/", views.exportar_excel, name="exportar_excel"),
]
