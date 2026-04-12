from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf.pisa import pisaDocument
from .models import EPI, Colaborador, RegistroEPI
from .forms import EPIForm, ColaboradorForm, RegistroEPIForm
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
import csv


def logout_view(request):
    logout(request)
    return redirect("login")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            login(request, user)
            messages.success(
                request, f"Conta criada com sucesso! Bem-vindo, {username}!"
            )
            return redirect("home")
        else:
            for msg in form.error_messages:
                messages.error(request, form.error_messages[msg])
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


@login_required
def home(request):
    total_epis = EPI.objects.count()
    total_colaboradores = Colaborador.objects.count()
    total_retiradas = RegistroEPI.objects.filter(
        data_retirada__date=timezone.now().date()
    ).count()
    total_buscados = RegistroEPI.objects.count()

    from django.db.models import Count, Sum

    top_epis = (
        RegistroEPI.objects.values("epi__descricao")
        .annotate(total=Sum("quantidade"))
        .order_by("-total")[:5]
    )

    epis_por_setor = (
        Colaborador.objects.values("setor")
        .annotate(total=Count("id"))
        .order_by("-total")
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


@login_required
def cadastrar_epi(request):
    if request.method == "POST":
        form = EPIForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "EPI cadastrado com sucesso!")
            return redirect("cadastrar_epi")
    else:
        form = EPIForm()

    query = request.GET.get("q")
    epis = EPI.objects.all()
    if query:
        epis = epis.filter(Q(ca__icontains=query) | Q(descricao__icontains=query))

    return render(request, "cadastrar_epi.html", {"form": form, "epis": epis})


@login_required
def cadastrar_colaborador(request):
    if request.method == "POST":
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Colaborador cadastrado com sucesso!")
            return redirect("cadastrar_colaborador")
    else:
        form = ColaboradorForm()

    colaboradores = Colaborador.objects.all()
    return render(
        request,
        "cadastrar_colaborador.html",
        {"form": form, "colaboradores": colaboradores},
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
            form.save()
            messages.success(request, "Retirada registrada com sucesso!")
            return redirect("registrar_retirada")
    else:
        form = RegistroEPIForm()

    registros = RegistroEPI.objects.select_related("colaborador", "epi").order_by(
        "-data_retirada"
    )
    return render(
        request, "registrar_retirada.html", {"form": form, "registros": registros}
    )


@login_required
def buscar_epis_colaborador(request):
    matricula = request.GET.get("matricula")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    epis = None
    colaborador = None

    if matricula:
        try:
            colaborador = Colaborador.objects.get(matricula=matricula)
            registros = RegistroEPI.objects.filter(
                colaborador=colaborador
            ).select_related("epi")

            if data_inicio:
                registros = registros.filter(
                    data_retirada__date__gte=datetime.strptime(
                        data_inicio, "%Y-%m-%d"
                    ).date()
                )
            if data_fim:
                registros = registros.filter(
                    data_retirada__date__lte=datetime.strptime(
                        data_fim, "%Y-%m-%d"
                    ).date()
                )

            epis = [
                {"epi": r.epi, "quantidade": r.quantidade, "data": r.data_retirada}
                for r in registros
            ]
        except Colaborador.DoesNotExist:
            messages.error(request, "Colaborador não encontrado!")

    return render(
        request,
        "buscar_epis.html",
        {"matricula": matricula, "colaborador": colaborador, "epis": epis},
    )


@login_required
def gerar_pdf(request):
    matricula = request.GET.get("matricula")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    if not matricula:
        return HttpResponse("Matrícula não fornecida", status=400)

    try:
        colaborador = Colaborador.objects.get(matricula=matricula)
        registros = RegistroEPI.objects.filter(colaborador=colaborador).select_related(
            "epi"
        )

        if data_inicio:
            registros = registros.filter(
                data_retirada__date__gte=datetime.strptime(
                    data_inicio, "%Y-%m-%d"
                ).date()
            )
        if data_fim:
            registros = registros.filter(
                data_retirada__date__lte=datetime.strptime(data_fim, "%Y-%m-%d").date()
            )

        html = render_to_string(
            "pdf_template.html", {"colaborador": colaborador, "registros": registros}
        )

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'filename="epis_{matricula}.pdf"'

        pisaDocument(html, dest=response)
        return response
    except Colaborador.DoesNotExist:
        return HttpResponse("Colaborador não encontrado", status=404)


@login_required
def exportar_excel(request):
    matricula = request.GET.get("matricula")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    if not matricula:
        return HttpResponse("Matrícula não fornecida", status=400)

    try:
        colaborador = Colaborador.objects.get(matricula=matricula)
        registros = RegistroEPI.objects.filter(colaborador=colaborador).select_related(
            "epi"
        )

        if data_inicio:
            registros = registros.filter(
                data_retirada__date__gte=datetime.strptime(
                    data_inicio, "%Y-%m-%d"
                ).date()
            )
        if data_fim:
            registros = registros.filter(
                data_retirada__date__lte=datetime.strptime(data_fim, "%Y-%m-%d").date()
            )

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
    except Colaborador.DoesNotExist:
        return HttpResponse("Colaborador não encontrado", status=404)
