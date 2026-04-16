from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


def register(request):
    if not settings.ALLOW_SELF_REGISTRATION:
        messages.error(
            request, "O cadastro público está desativado. Procure um administrador."
        )
        return redirect("login")

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

        for msg in form.error_messages:
            messages.error(request, form.error_messages[msg])
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})
