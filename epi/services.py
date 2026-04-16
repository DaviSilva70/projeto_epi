from datetime import datetime

from django.core.exceptions import ValidationError

from .models import Colaborador, RegistroEPI


DATE_INPUT_FORMAT = "%Y-%m-%d"


def parse_date_or_none(value, field_name):
    if not value:
        return None

    try:
        return datetime.strptime(value, DATE_INPUT_FORMAT).date()
    except ValueError as exc:
        raise ValidationError({field_name: "Informe uma data válida no formato AAAA-MM-DD."}) from exc


def get_colaborador_by_matricula(matricula):
    if not matricula:
        raise Colaborador.DoesNotExist
    return Colaborador.objects.get(matricula=matricula)


def get_registros_filtrados(colaborador, data_inicio=None, data_fim=None):
    inicio = parse_date_or_none(data_inicio, "data_inicio")
    fim = parse_date_or_none(data_fim, "data_fim")

    if inicio and fim and inicio > fim:
        raise ValidationError("A data inicial não pode ser maior que a data final.")

    registros = RegistroEPI.objects.filter(colaborador=colaborador).select_related("epi")

    if inicio:
        registros = registros.filter(data_retirada__date__gte=inicio)
    if fim:
        registros = registros.filter(data_retirada__date__lte=fim)

    return registros.order_by("-data_retirada")
