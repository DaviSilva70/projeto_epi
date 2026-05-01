from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ColaboradorForm, EPIForm, RegistroEPIForm
from .models import Colaborador, EPI, RegistroEPI, DevolucaoEPI


def _get_limite_mensal():
    return getattr(settings, "LIMITE_RETIRADAS_MENSAL", 10)


def _paginate_queryset(request, queryset):
    paginator = Paginator(queryset, settings.LIST_PAGE_SIZE)
    return paginator.get_page(request.GET.get("page"))


@login_required
def cadastrar_epi(request):
    if request.method == "POST":
        form = EPIForm(request.POST, request.FILES)
        if form.is_valid():
            epi = form.save(commit=False)
            epi.created_by = request.user
            epi.save()
            messages.success(request, "EPI cadastrado com sucesso!")
            return redirect("cadastrar_epi")
    else:
        form = EPIForm()

    query = request.GET.get("q")
    epis = EPI.objects.all().order_by("-created_at")
    if query:
        epis = epis.filter(Q(ca__icontains=query) | Q(descricao__icontains=query))

    page_obj = _paginate_queryset(request, epis)
    return render(
        request,
        "cadastrar_epi.html",
        {
            "form": form,
            "epis": page_obj,
            "page_obj": page_obj,
            "query_string": f"q={query}" if query else "",
        },
    )


@login_required
def cadastrar_colaborador(request):
    if request.method == "POST":
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            colaborador = form.save(commit=False)
            colaborador.created_by = request.user
            colaborador.save()
            messages.success(request, "Colaborador cadastrado com sucesso!")
            return redirect("cadastrar_colaborador")
    else:
        form = ColaboradorForm()

    colaboradores = Colaborador.objects.all().order_by("nome_completo")
    page_obj = _paginate_queryset(request, colaboradores)
    return render(
        request,
        "cadastrar_colaborador.html",
        {"form": form, "colaboradores": page_obj, "page_obj": page_obj},
    )


@login_required
def editar_colaborador(request, id):
    colaborador = get_object_or_404(Colaborador, id=id)
    if request.method == "POST":
        form = ColaboradorForm(request.POST, instance=colaborador)
        if form.is_valid():
            form.save()
            messages.success(request, "Colaborador atualizado com sucesso!")
            return redirect("cadastrar_colaborador")
    else:
        form = ColaboradorForm(instance=colaborador)

    return render(
        request, "editar_colaborador.html", {"form": form, "colaborador": colaborador}
    )


@login_required
def deletar_colaborador(request, id):
    colaborador = get_object_or_404(Colaborador, id=id)
    if request.method == "POST":
        RegistroEPI.objects.filter(colaborador=colaborador).delete()
        colaborador.delete()
        messages.success(request, "Colaborador excluído com sucesso!")
        return redirect("cadastrar_colaborador")
    return render(request, "confirmar_delete.html", {"colaborador": colaborador})


@login_required
def registrar_retirada(request):
    if request.method == "POST":
        form = RegistroEPIForm(request.POST)
        if form.is_valid():
            epi = form.cleaned_data["epi"]
            quantidade = form.cleaned_data["quantidade"]
            colaborador = form.cleaned_data["colaborador"]

            limite_mensal = _get_limite_mensal()

            total_mes_atual = RegistroEPI.objects.filter(
                colaborador=colaborador,
                data_retirada__month=timezone.now().month,
                data_retirada__year=timezone.now().year,
            ).aggregate(total=Sum("quantidade"))["total"] or 0

            if total_mes_atual + quantidade > limite_mensal:
                messages.error(
                    request,
                    f"Limite de {limite_mensal} EPIs por mês excedido. "
                    f"Você já retirou {total_mes_atual} este mês.",
                )
            else:
                registro = form.save(commit=False)
                registro.created_by = request.user
                registro.save()

                epi.quantidade_em_estoque -= quantidade
                epi.save()

                messages.success(request, "Retirada registrada com sucesso!")
            return redirect("registrar_retirada")
    else:
        form = RegistroEPIForm()

    registros = (
        RegistroEPI.objects.select_related("colaborador", "epi")
        .prefetch_related("devolucao")
        .order_by("-data_retirada")
    )
    page_obj = _paginate_queryset(request, registros)
    return render(
        request,
        "registrar_retirada.html",
        {"form": form, "registros": page_obj, "page_obj": page_obj},
    )


@login_required
def registrar_devolucao(request, registro_id):
    from .forms import DevolucaoEPIForm

    registro = get_object_or_404(RegistroEPI, id=registro_id)

    if hasattr(registro, "devolucao"):
        messages.error(request, "Esta retirada já possui uma devolução registrada.")
        return redirect("registrar_retirada")

    if request.method == "POST":
        form = DevolucaoEPIForm(request.POST, registro=registro)
        if form.is_valid():
            devolucao = form.save(commit=False)
            devolucao.registro = registro
            devolucao.created_by = request.user
            devolucao.save()

            registro.epi.quantidade_em_estoque += devolucao.quantidade_devolvida
            registro.epi.save()

            messages.success(request, "Devolução registrada com sucesso!")
            return redirect("registrar_retirada")
    else:
        form = DevolucaoEPIForm(registro=registro)

    return render(request, "registrar_devolucao.html", {"form": form, "registro": registro, "quantidade_retirada": registro.quantidade})
