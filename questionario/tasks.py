from celery import shared_task


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_email_notificacao(self, paciente_id, tipo, link):
    """Envia e-mail de notificação ao terapeuta quando uma avaliação é concluída."""
    from django.core.mail import send_mail
    from django.template.loader import render_to_string

    from .models import Paciente

    _NOMES = {
        "sensorial":       "Perfil Sensorial",
        "vineland":        "Escala Vineland",
        "escolar":         "Sensorial Escolar",
        "bebe":            "Perfil Sensorial Bebê",
        "spm":             "SPM",
        "spm_p":           "SPM-P Casa",
        "spm_casa":        "SPM Casa",
        "pedi":            "PEDI",
        "vineland3":       "Vineland-3",
        "portage":         "Guia Portage",
        "sdq":             "SDQ",
        "snap_iv":         "SNAP-IV",
        "mchat":           "M-CHAT-R",
        "cars":            "CARS-2",
        "linguagem":       "Avaliação de Linguagem",
        "alimentacao":     "Triagem de Alimentação Seletiva",
        "desenvolvimento": "Marcos de Desenvolvimento",
        "sono":            "Avaliação de Sono Infantil",
        "habilidades":     "Habilidades Adaptativas",
        "comportamento":   "Comportamento Funcional",
        "cognitivo":       "Rastreio Cognitivo",
        "psicopedagogica": "Avaliação Psicopedagógica",
    }

    try:
        paciente = Paciente.objects.select_related('medico').get(pk=paciente_id)
        terapeuta = paciente.medico

        if not terapeuta.email:
            return

        nome_tipo = _NOMES.get(tipo, tipo.replace("_", " ").title())
        nome_terapeuta = terapeuta.get_full_name() or terapeuta.username

        html = render_to_string("questionario/emails/email_notificacao_terapeuta.html", {
            "nome_terapeuta": nome_terapeuta,
            "paciente": paciente,
            "nome_tipo": nome_tipo,
            "link": link,
        })
        send_mail(
            subject=f"IntegraMente — Avaliação concluída: {paciente.nome}",
            message=(
                f"Olá, {nome_terapeuta}!\n\n"
                f"O responsável de {paciente.nome} concluiu o questionário de {nome_tipo}.\n"
                f"Acesse o sistema para visualizar os resultados: {link}"
            ),
            from_email=None,
            recipient_list=[terapeuta.email],
            html_message=html,
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def desativar_trials_expirados():
    """
    Executa diariamente via Celery Beat.
    Desativa contas cujo trial de 7 dias já encerrou:
      - Define user.is_active = False
      - Remove os módulos liberados (limpeza)
      - Envia e-mail ao admin com resumo dos trials expirados
      - Envia e-mail ao usuário avisando que o trial expirou
    """
    from django.conf import settings
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.utils import timezone
    from .models import PerfilMedico

    limite = timezone.now() - timezone.timedelta(days=7)
    perfis_expirados = PerfilMedico.objects.filter(
        plano="trial",
        trial_inicio__lt=limite,
        user__is_active=True,
    ).select_related("user")

    expirados = []
    for perfil in perfis_expirados:
        perfil.user.is_active = False
        perfil.user.save(update_fields=["is_active"])
        perfil.modulos_liberados.clear()
        expirados.append(perfil)

        # Avisa o usuário que o trial expirou
        if perfil.user.email:
            try:
                html = render_to_string("questionario/emails/email_trial_expirado.html", {
                    "nome": perfil.user.first_name or perfil.user.username,
                    "url_planos": "https://integramente.pro/planos/",
                })
                send_mail(
                    subject="IntegraMente — Seu período de teste encerrou",
                    message=f"Olá! Seu trial de 7 dias encerrou. Escolha um plano em: https://integramente.pro/planos/",
                    from_email=None,
                    recipient_list=[perfil.user.email],
                    html_message=html,
                    fail_silently=True,
                )
            except Exception:
                pass

    total = len(expirados)

    # Notifica o admin com resumo dos trials expirados
    if total > 0:
        try:
            admin_email = getattr(settings, "ADMIN_NOTIFY_EMAIL", None) or settings.EMAIL_HOST_USER
            if admin_email:
                linhas = "\n".join(
                    f"- {p.user.get_full_name() or p.user.username} <{p.user.email}>"
                    for p in expirados
                )
                html = render_to_string("questionario/emails/email_trials_expirados_admin.html", {
                    "expirados": expirados,
                    "total": total,
                    "painel_url": "https://integramente.pro/admin/questionario/solicitacaoplano/painel/",
                })
                send_mail(
                    subject=f"[IntegraMente] {total} trial(s) expirado(s) hoje",
                    message=f"{total} trial(s) expirado(s):\n{linhas}",
                    from_email=None,
                    recipient_list=[admin_email],
                    html_message=html,
                    fail_silently=True,
                )
        except Exception:
            pass

    return f"{total} conta(s) de trial desativada(s)."


@shared_task
def verificar_planos_expirando():
    """
    Executa diariamente via Celery Beat.
    1) Avisa usuários e admin sobre planos vencendo em 3 dias
    2) Desativa planos vencidos (bloqueia acesso e limpa módulos)
    3) Envia e-mail ao admin com resumo do dia
    """
    from django.conf import settings
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.utils import timezone
    from .models import PerfilMedico

    agora     = timezone.now()
    em_3_dias = agora + timezone.timedelta(days=3)

    # ── 1) Alertar planos que vencem em exatamente 3 dias ──────────────────────
    prestes_a_vencer = PerfilMedico.objects.filter(
        plano__in=("start", "plus", "elite"),
        plano_expiracao__date=em_3_dias.date(),
        user__is_active=True,
    ).select_related("user")

    for perfil in prestes_a_vencer:
        if perfil.user.email:
            try:
                html = render_to_string("questionario/emails/email_plano_vencendo.html", {
                    "nome": perfil.user.first_name or perfil.user.username,
                    "plano": perfil.get_plano_display(),
                    "expiracao": perfil.plano_expiracao,
                    "url_renovar": "https://integramente.pro/planos/",
                })
                send_mail(
                    subject=f"IntegraMente — Seu plano {perfil.get_plano_display()} vence em 3 dias",
                    message=f"Seu plano vence em {perfil.plano_expiracao.strftime('%d/%m/%Y')}. Renove em: https://integramente.pro/planos/",
                    from_email=None,
                    recipient_list=[perfil.user.email],
                    html_message=html,
                    fail_silently=True,
                )
            except Exception:
                pass

    # ── 2) Desativar planos vencidos ───────────────────────────────────────────
    vencidos = PerfilMedico.objects.filter(
        plano__in=("start", "plus", "elite"),
        plano_expiracao__lt=agora,
        user__is_active=True,
    ).select_related("user")

    desativados = []
    for perfil in vencidos:
        perfil.user.is_active = False
        perfil.user.save(update_fields=["is_active"])
        perfil.modulos_liberados.clear()
        desativados.append(perfil)

        # Avisa o usuário
        if perfil.user.email:
            try:
                html = render_to_string("questionario/emails/email_plano_vencido.html", {
                    "nome": perfil.user.first_name or perfil.user.username,
                    "plano": perfil.get_plano_display(),
                    "url_renovar": "https://integramente.pro/planos/",
                })
                send_mail(
                    subject=f"IntegraMente — Seu plano {perfil.get_plano_display()} venceu",
                    message=f"Seu plano venceu. Renove em: https://integramente.pro/planos/",
                    from_email=None,
                    recipient_list=[perfil.user.email],
                    html_message=html,
                    fail_silently=True,
                )
            except Exception:
                pass

    # ── 3) Resumo para o admin ─────────────────────────────────────────────────
    if prestes_a_vencer.count() > 0 or len(desativados) > 0:
        try:
            admin_email = getattr(settings, "ADMIN_NOTIFY_EMAIL", None) or settings.EMAIL_HOST_USER
            if admin_email:
                html = render_to_string("questionario/emails/email_planos_resumo_admin.html", {
                    "vencendo": list(prestes_a_vencer),
                    "vencidos": desativados,
                    "painel_url": "https://integramente.pro/admin/questionario/solicitacaoplano/painel/",
                })
                send_mail(
                    subject=f"[IntegraMente] Resumo de planos — {agora.strftime('%d/%m/%Y')}",
                    message=f"Vencendo em 3 dias: {prestes_a_vencer.count()} | Vencidos hoje: {len(desativados)}",
                    from_email=None,
                    recipient_list=[admin_email],
                    html_message=html,
                    fail_silently=True,
                )
        except Exception:
            pass

    return f"Alertas: {prestes_a_vencer.count()} | Desativados: {len(desativados)}"
