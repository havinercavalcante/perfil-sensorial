from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone

from ..models import PerfilMedico, Especialidade, HistoricoLogin, ModuloAvaliacao, _parse_dispositivo


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
    return render(request, "questionario/auth/login.html")


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
        plano = request.POST.get("plano", "trial").strip()
        if plano not in ("trial", "start", "plus", "elite"):
            plano = "trial"
        especialidades_ids = request.POST.getlist("especialidades")

        consentimento = request.POST.get("consentimento", "")

        erros = []
        if not nome or not username or not password or not email:
            erros.append("Preencha todos os campos obrigatórios.")
        if password != password2:
            erros.append("As senhas não coincidem.")
        if len(password) < 8:
            erros.append("A senha deve ter pelo menos 8 caracteres.")
        if User.objects.filter(username=username).exists():
            erros.append("Este nome de usuário já está em uso.")
        if email and User.objects.filter(email=email).exists():
            erros.append("Este e-mail já está cadastrado.")
        if not consentimento:
            erros.append("É necessário aceitar a Política de Privacidade para criar uma conta.")

        if erros:
            for e in erros:
                messages.error(request, e)
            return render(request, "questionario/auth/registrar.html", {
                "post": request.POST,
                "especialidades": especialidades,
                "especialidades_selecionadas": especialidades_ids,
                "plano_selecionado": plano,
            })

        partes = nome.strip().split(" ", 1)
        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=partes[0], last_name=partes[1] if len(partes) > 1 else "",
            is_active=False,
        )
        perfil = PerfilMedico.objects.create(
            user=user,
            registro_profissional=registro_profissional,
            telefone=telefone,
            plano=plano,
            trial_inicio=timezone.now() if plano == "trial" else None,
        )
        if especialidades_ids:
            perfil.especialidades.set(Especialidade.objects.filter(id__in=especialidades_ids))
        if plano == "trial":
            modulos_trial = ModuloAvaliacao.objects.filter(codigo__in=PerfilMedico.MODULOS_TRIAL)
            perfil.modulos_liberados.set(modulos_trial)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        link = request.build_absolute_uri(f"/confirmar-email/{uid}/{token}/")
        html = render_to_string("questionario/emails/email_confirmacao_conta.html", {
            "nome": user.first_name,
            "link": link,
        })
        send_mail(
            subject="IntegraMente — Confirme seu e-mail",
            message=f"Olá, {user.first_name}!\n\nConfirme seu e-mail acessando: {link}",
            from_email=None,
            recipient_list=[email],
            html_message=html,
            fail_silently=True,
        )
        return render(request, "questionario/auth/registrar.html", {
            "especialidades": especialidades,
            "especialidades_selecionadas": [],
            "aguardando_confirmacao": True,
            "email_destino": email,
        })

    plano_inicial = request.GET.get("plano", "")
    if plano_inicial not in ("trial", "start", "plus", "elite"):
        plano_inicial = ""
    return render(request, "questionario/auth/registrar.html", {
        "especialidades": especialidades,
        "especialidades_selecionadas": [],
        "plano_selecionado": plano_inicial,
    })


def confirmar_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        perfil, _ = PerfilMedico.objects.get_or_create(user=user)
        if perfil.session_key:
            Session.objects.filter(session_key=perfil.session_key).delete()
        login(request, user)
        request.session.save()
        perfil.session_key = request.session.session_key or ""
        perfil.save(update_fields=["session_key"])
        messages.success(request, f"Bem-vindo(a), {user.first_name}! Sua conta foi confirmada com sucesso.")
        return redirect("index")

    return render(request, "questionario/auth/registrar.html", {
        "especialidades": Especialidade.objects.all().order_by("nome"),
        "especialidades_selecionadas": [],
        "link_invalido": True,
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
                if len(nova_senha) >= 8:
                    u.set_password(nova_senha)
                    u.save()
                    update_session_auth_hash(request, u)
                    messages.success(request, "Senha alterada com sucesso.")
                else:
                    messages.error(request, "A nova senha deve ter pelo menos 8 caracteres.")
            else:
                messages.error(request, "As novas senhas não coincidem.")

        messages.success(request, "Perfil atualizado com sucesso.")
        return redirect("meu_perfil")

    especialidades_selecionadas = list(perfil.especialidades.values_list("id", flat=True))
    return render(request, "questionario/auth/meu_perfil.html", {
        "perfil": perfil,
        "especialidades": especialidades,
        "especialidades_selecionadas": especialidades_selecionadas,
    })


def politica_privacidade(request):
    return render(request, "questionario/auth/politica_privacidade.html")


@login_required
def trial_expirado(request):
    return render(request, "questionario/auth/trial_expirado.html")
