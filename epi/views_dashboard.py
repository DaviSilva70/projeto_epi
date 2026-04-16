from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from .models import Colaborador, EPI, RegistroEPI


@login_required
def home(request):
    total_epis = EPI.objects.count()
    total_colaboradores = Colaborador.objects.count()
    total_retiradas = RegistroEPI.objects.filter(
        data_retirada__date=timezone.now().date()
    ).count()
    total_buscados = RegistroEPI.objects.count()

    top_epis = (
        RegistroEPI.objects.values("epi__descricao")
        .annotate(total=Sum("quantidade"))
        .order_by("-total")[:5]
    )

    epis_por_setor = (
        Colaborador.objects.values("setor").annotate(total=Count("id")).order_by("-total")
    )

    retiradas_mes = RegistroEPI.objects.filter(
        data_retirada__month=timezone.now().month,
        data_retirada__year=timezone.now().year,
    ).count()

    return render(
        request,
        "home.html",
        {
            "total_epis": total_epis,
            "total_colaboradores": total_colaboradores,
            "total_retiradas": total_retiradas,
            "total_buscados": total_buscados,
            "top_epis": top_epis,
            "epis_por_setor": epis_por_setor,
            "retiradas_mes": retiradas_mes,
        },
    )
