from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

from ..models import PerfilMedico, Especialidade, HistoricoLogin, _parse_dispositivo


def _get_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        ua = request.META.get("HTTP_USER_AGENT", "")
        ip = _get_ip(request)

        user = authenticate(request, username=username, password=password)
        if user:
            # Encerra sessão anterior (impede uso simultâneo da conta em outro dispositivo)
            perfil, _ = PerfilMedico.objects.get_or_create(user=user)
            if perfil.session_key:
                Session.objects.filter(session_key=perfil.session_key).delete()

            login(request, user)

            perfil.session_key = request.session.session_key
            perfil.save(update_fields=["session_key"])

            HistoricoLogin.objects.create(
                user=user,
                ip=ip,
                dispositivo=_parse_dispositivo(ua),
                user_agent=ua,
                sucesso=True,
            )

            return redirect(request.GET.get("next", "index"))

        # Registra tentativa falha — só se o usuário existir (para não expor enumeração)
        try:
            user_obj = User.objects.get(username=username)
            HistoricoLogin.objects.create(
                user=user_obj,
                ip=ip,
                dispositivo=_parse_dispositivo(ua),
                user_agent=ua,
                sucesso=False,
            )
        except User.DoesNotExist:
            pass

        messages.error(request, "Usuário ou senha incorretos.")
    return render(request, "questionario/login.html")


def logout_view(request):
    if request.user.is_authenticated:
        try:
            request.user.perfil.session_key = ""
            request.user.perfil.save(update_fields=["session_key"])
        except PerfilMedico.DoesNotExist:
            pass
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


def politica_privacidade(request):
    return render(request, "questionario/politica_privacidade.html")
