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
    """
    from django.utils import timezone
    from django.contrib.auth.models import User
    from .models import PerfilMedico

    limite = timezone.now() - timezone.timedelta(days=7)
    perfis_expirados = PerfilMedico.objects.filter(
        plano="trial",
        trial_inicio__lt=limite,
        user__is_active=True,
    ).select_related("user")

    total = 0
    for perfil in perfis_expirados:
        perfil.user.is_active = False
        perfil.user.save(update_fields=["is_active"])
        perfil.modulos_liberados.clear()
        total += 1

    return f"{total} conta(s) de trial desativada(s)."
