import uuid

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone

from ..models import PerfilMedico, Especialidade, HistoricoLogin, ModuloAvaliacao, Indicacao, _parse_dispositivo


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


def _gerar_username(email):
    """Gera username único baseado na parte local do e-mail."""
    import re
    base = re.sub(r"[^a-z0-9._-]", "", email.split("@")[0].lower())[:30] or "usuario"
    username = base
    contador = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}{contador}"
        contador += 1
    return username


_PLANOS_VALIDOS = ("trial", "start", "plus", "elite")


def registrar_view(request):
    ref_code = (request.POST.get("ref") or request.GET.get("ref") or "").strip()

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        consentimento = request.POST.get("consentimento", "")
        plano = request.POST.get("plano", "trial").strip()
        if plano not in _PLANOS_VALIDOS:
            plano = "trial"

        erros = []
        if not nome or not email or not username or not password:
            erros.append("Preencha todos os campos obrigatórios.")
        if password != password2:
            erros.append("As senhas não coincidem.")
        if len(password) < 8:
            erros.append("A senha deve ter pelo menos 8 caracteres.")
        if username and User.objects.filter(username=username).exists():
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
                "plano_selecionado": plano,
                "ref_code": ref_code,
            })

        partes = nome.strip().split(" ", 1)
        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=partes[0], last_name=partes[1] if len(partes) > 1 else "",
            is_active=False,
        )
        perfil = PerfilMedico.objects.create(
            user=user,
            plano=plano,
            trial_inicio=timezone.now() if plano == "trial" else None,
        )
        modulos_trial = ModuloAvaliacao.objects.filter(codigo__in=PerfilMedico.MODULOS_TRIAL)
        perfil.modulos_liberados.set(modulos_trial)

        # Registra indicação, se o cadastro veio por um link de indicação válido (código UUID)
        if ref_code:
            try:
                codigo_uuid = uuid.UUID(ref_code)
            except (ValueError, AttributeError):
                codigo_uuid = None
            if codigo_uuid:
                indicador_perfil = PerfilMedico.objects.filter(
                    codigo_indicacao=codigo_uuid, user__is_active=True
                ).exclude(user=user).select_related("user").first()
                if indicador_perfil:
                    Indicacao.objects.create(indicador=indicador_perfil.user, indicado=user)

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
            "aguardando_confirmacao": True,
            "email_destino": email,
        })

    plano_inicial = request.GET.get("plano", "trial").strip()
    if plano_inicial not in _PLANOS_VALIDOS:
        plano_inicial = "trial"
    return render(request, "questionario/auth/registrar.html", {
        "plano_selecionado": plano_inicial,
        "ref_code": ref_code,
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
        return redirect("/completar-cadastro/?novo=1")

    return render(request, "questionario/auth/registrar.html", {
        "link_invalido": True,
    })


@login_required
def indicacoes(request):
    """Painel de indicação: link pessoal do profissional e status das indicações feitas."""
    perfil, _ = PerfilMedico.objects.get_or_create(user=request.user)
    link_indicacao = request.build_absolute_uri(f"/registrar/?ref={perfil.codigo_indicacao}")
    feitas = (
        Indicacao.objects
        .filter(indicador=request.user)
        .select_related("indicado")
        .order_by("-criado_em")
    )

    mensagem_padrao = (
        f"Olá! Estou usando o IntegraMente para aplicar avaliações clínicas com pontuação "
        f"automática e queria te indicar — você ganha 7 dias grátis para testar: {link_indicacao}"
    )

    return render(request, "questionario/auth/indicacoes.html", {
        "link_indicacao": link_indicacao,
        "mensagem_padrao": mensagem_padrao,
        "indicacoes_feitas": feitas,
        "recompensa_dias": Indicacao.RECOMPENSA_DIAS,
    })


@login_required
def enviar_indicacao_email(request):
    """Envia o link de indicação do profissional para o e-mail de um colega (via modal/AJAX)."""
    if request.method != "POST":
        return JsonResponse({"ok": False, "message": "Método não permitido."}, status=405)

    destino = request.POST.get("email_destino", "").strip()
    if not destino:
        return JsonResponse({"ok": False, "message": "Informe um e-mail."})

    try:
        validate_email(destino)
    except ValidationError:
        return JsonResponse({"ok": False, "message": "E-mail inválido."})

    perfil, _ = PerfilMedico.objects.get_or_create(user=request.user)
    link_indicacao = request.build_absolute_uri(f"/registrar/?ref={perfil.codigo_indicacao}")
    nome_indicador = request.user.get_full_name() or request.user.username
    html = render_to_string("questionario/emails/email_indicacao.html", {
        "nome_indicador": nome_indicador,
        "link": link_indicacao,
    })
    send_mail(
        subject=f"{nome_indicador} te convidou para experimentar o IntegraMente",
        message=(
            f"{nome_indicador} usa o IntegraMente para aplicar avaliações clínicas "
            f"com pontuação automática e quer te apresentar a plataforma.\n\n"
            f"Teste grátis por 7 dias: {link_indicacao}"
        ),
        from_email=None,
        recipient_list=[destino],
        html_message=html,
        fail_silently=True,
    )
    return JsonResponse({"ok": True, "message": f"Convite enviado para {destino}!"})


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


@login_required
def completar_cadastro(request):
    perfil, _ = PerfilMedico.objects.get_or_create(user=request.user)
    especialidades = Especialidade.objects.all().order_by("nome")

    if request.method == "POST":
        telefone = request.POST.get("telefone", "").strip()
        registro_profissional = request.POST.get("registro_profissional", "").strip()
        especialidades_ids = request.POST.getlist("especialidades")

        erros = {}
        if not telefone:
            erros["telefone"] = True
        if not especialidades_ids:
            erros["especialidade"] = True

        if erros:
            return render(request, "questionario/auth/completar_cadastro.html", {
                "perfil": perfil,
                "especialidades": especialidades,
                "especialidades_selecionadas": especialidades_ids,
                "erro_telefone": erros.get("telefone"),
                "erro_especialidade": erros.get("especialidade"),
                "post": request.POST,
            })

        perfil.registro_profissional = registro_profissional
        perfil.telefone = telefone
        perfil.save(update_fields=["registro_profissional", "telefone"])
        perfil.especialidades.set(Especialidade.objects.filter(id__in=especialidades_ids))
        return redirect("index")

    especialidades_selecionadas = list(perfil.especialidades.values_list("id", flat=True))
    return render(request, "questionario/auth/completar_cadastro.html", {
        "perfil": perfil,
        "especialidades": especialidades,
        "especialidades_selecionadas": especialidades_selecionadas,
    })


def politica_privacidade(request):
    return render(request, "questionario/auth/politica_privacidade.html")


