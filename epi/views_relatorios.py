import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from xhtml2pdf.pisa import pisaDocument

from .models import Colaborador
from .services import get_colaborador_by_matricula, get_registros_filtrados


@login_required
def buscar_epis_colaborador(request):
    matricula = request.GET.get("matricula")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    epis = None
    colaborador = None

    if matricula:
        try:
            colaborador = get_colaborador_by_matricula(matricula)
            registros = get_registros_filtrados(colaborador, data_inicio, data_fim)
            epis = [
                {"epi": registro.epi, "quantidade": registro.quantidade, "data": registro.data_retirada}
                for registro in registros
            ]
        except Colaborador.DoesNotExist:
            messages.error(request, "Colaborador não encontrado!")
        except ValidationError as exc:
            for error in exc.messages:
                messages.error(request, error)

    return render(
        request,
        "buscar_epis.html",
        {"matricula": matricula, "colaborador": colaborador, "epis": epis},
    )


def _get_colaborador_e_registros(matricula, data_inicio, data_fim):
    if not matricula:
        return None, HttpResponse("Matrícula não fornecida", status=400)

    try:
        colaborador = get_colaborador_by_matricula(matricula)
        registros = get_registros_filtrados(colaborador, data_inicio, data_fim)
        return (colaborador, registros), None
    except Colaborador.DoesNotExist:
        return None, HttpResponse("Colaborador não encontrado", status=404)
    except ValidationError as exc:
        return None, HttpResponse("; ".join(exc.messages), status=400)


@login_required
def gerar_pdf(request):
    matricula = request.GET.get("matricula")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")

    resultado, error_response = _get_colaborador_e_registros(
        matricula, data_inicio, data_fim
    )
    if error_response:
        return error_response

    colaborador, registros = resultado
    html = render_to_string(
        "pdf_template.html", {"colaborador": colaborador, "registros": registros}
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="epis_{matricula}.pdf"'
    pisaDocument(html, dest=response)
    return response


@login_required
def exportar_excel(request):
    matricula = request.GET.get("matricula")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")

    resultado, error_response = _get_colaborador_e_registros(
        matricula, data_inicio, data_fim
    )
    if error_response:
        return error_response

    colaborador, registros = resultado
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="epis_{matricula}.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["EPI", "CA", "Quantidade", "Data Retirada", "Colaborador", "Matrícula"]
    )

    for reg in registros:
        writer.writerow(
            [
                reg.epi.descricao,
                reg.epi.ca,
                reg.quantidade,
                reg.data_retirada.strftime("%d/%m/%Y %H:%M"),
                colaborador.nome_completo,
                colaborador.matricula,
            ]
        )

    return response
