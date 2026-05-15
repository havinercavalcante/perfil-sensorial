from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from ..models import PerfilMedico, Especialidade


def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get("next", "index"))
        messages.error(request, "Usuário ou senha incorretos.")
    return render(request, "questionario/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def registrar_view(request):
    especialidades = Especialidade.objects.all().order_by("nome")

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        registro_profissional = request.POST.get("registro_profissional", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        especialidades_ids = request.POST.getlist("especialidades")

        erros = []
        if not nome or not username or not password:
            erros.append("Preencha todos os campos obrigatórios.")
        if password != password2:
            erros.append("As senhas não coincidem.")
        if len(password) < 6:
            erros.append("A senha deve ter pelo menos 6 caracteres.")
        if User.objects.filter(username=username).exists():
            erros.append("Este nome de usuário já está em uso.")
        if email and User.objects.filter(email=email).exists():
            erros.append("Este e-mail já está cadastrado.")

        if erros:
            for e in erros:
                messages.error(request, e)
            return render(request, "questionario/registrar.html", {
                "post": request.POST,
                "especialidades": especialidades,
                "especialidades_selecionadas": especialidades_ids,
            })

        partes = nome.strip().split(" ", 1)
        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=partes[0], last_name=partes[1] if len(partes) > 1 else ""
        )
        perfil = PerfilMedico.objects.create(
            user=user,
            registro_profissional=registro_profissional,
            telefone=telefone,
        )
        if especialidades_ids:
            perfil.especialidades.set(Especialidade.objects.filter(id__in=especialidades_ids))
        login(request, user)
        messages.success(request, f"Bem-vindo(a), {user.first_name}! Conta criada com sucesso.")
        return redirect("index")

    return render(request, "questionario/registrar.html", {
        "especialidades": especialidades,
        "especialidades_selecionadas": [],
    })


@login_required
def meu_perfil(request):
    perfil, _ = PerfilMedico.objects.get_or_create(user=request.user)
    especialidades = Especialidade.objects.all().order_by("nome")

    if request.method == "POST":
        u = request.user
        nome = request.POST.get("nome", "").strip().split(" ", 1)
        u.first_name = nome[0]
        u.last_name = nome[1] if len(nome) > 1 else ""
        u.email = request.POST.get("email", "").strip()
        u.save()
        perfil.registro_profissional = request.POST.get("registro_profissional", "").strip()
        perfil.telefone = request.POST.get("telefone", "").strip()
        perfil.save()

        especialidades_ids = request.POST.getlist("especialidades")
        perfil.especialidades.set(Especialidade.objects.filter(id__in=especialidades_ids))

        # Trocar senha, se preenchida
        nova_senha = request.POST.get("nova_senha", "")
        if nova_senha:
            if nova_senha == request.POST.get("nova_senha2", ""):
                if len(nova_senha) >= 6:
                    u.set_password(nova_senha)
                    u.save()
                    update_session_auth_hash(request, u)
                    messages.success(request, "Senha alterada com sucesso.")
                else:
                    messages.error(request, "A nova senha deve ter pelo menos 6 caracteres.")
            else:
                messages.error(request, "As novas senhas não coincidem.")

        messages.success(request, "Perfil atualizado com sucesso.")
        return redirect("meu_perfil")

    especialidades_selecionadas = list(perfil.especialidades.values_list("id", flat=True))
    return render(request, "questionario/meu_perfil.html", {
        "perfil": perfil,
        "especialidades": especialidades,
        "especialidades_selecionadas": especialidades_selecionadas,
    })
