"""Views de pagamento manual — solicitação de plano e painel admin."""
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from ..models import (
    Indicacao,
    ModuloAvaliacao,
    MODULOS_POR_PLANO,
    PerfilMedico,
    SolicitacaoPlano,
    get_modulos_para_plano,
)


# ─────────────────────────────────────────────────────────────────────────────
#  Usuário solicita upgrade de plano
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def solicitar_plano(request):
    """
    Exibe página com instruções de pagamento PIX e permite ao usuário
    enviar a solicitação de upgrade.
    """
    perfil, _ = PerfilMedico.objects.get_or_create(user=request.user)
    plano_param = request.GET.get("plano", "")
    if plano_param not in ("start", "plus", "elite"):
        plano_param = ""

    # Solicitação já em aberto?
    solicitacao_pendente = SolicitacaoPlano.objects.filter(
        user=request.user, status="pendente"
    ).order_by("-criado_em").first()

    if request.method == "POST":
        plano = request.POST.get("plano", "").strip()

        if plano not in ("start", "plus", "elite"):
            messages.error(request, "Plano inválido.")
            return redirect("solicitar_plano")

        # Impede duplicata
        if SolicitacaoPlano.objects.filter(user=request.user, status="pendente").exists():
            messages.warning(request, "Você já tem uma solicitação pendente. Aguarde a confirmação.")
            return redirect("solicitar_plano")

        sol = SolicitacaoPlano.objects.create(
            user=request.user,
            plano=plano,
        )

        # Notifica admin por e-mail
        _notificar_admin_nova_solicitacao(sol, request)

        messages.success(
            request,
            "✅ Solicitação enviada! Assim que confirmarmos seu pagamento, seu acesso será liberado."
        )
        return redirect("solicitar_plano")

    # Histórico de pagamentos aprovados
    historico_pagamentos = SolicitacaoPlano.objects.filter(
        user=request.user, status="aprovado"
    ).order_by("-aprovado_em")

    ctx = {
        "perfil": perfil,
        "plano_param": plano_param,
        "solicitacao_pendente": solicitacao_pendente,
        "historico_pagamentos": historico_pagamentos,
        "total_meses_pagos": historico_pagamentos.count(),
        "pix_key": settings.PIX_KEY,
        "pix_beneficiario": settings.PIX_BENEFICIARIO,
        "pix_banco": settings.PIX_BANCO,
    }
    return render(request, "questionario/pagamentos/solicitar_plano.html", ctx)


# ─────────────────────────────────────────────────────────────────────────────
#  Painel admin — gerenciar solicitações
# ─────────────────────────────────────────────────────────────────────────────

@staff_member_required
def painel_pagamentos(request):
    """Painel para o admin ver e aprovar/rejeitar solicitações de plano."""
    from django.contrib.auth.models import User

    pendentes  = SolicitacaoPlano.objects.filter(status="pendente").select_related("user", "user__perfil")
    historico  = SolicitacaoPlano.objects.exclude(status="pendente").select_related("user", "user__perfil", "aprovado_por").order_by("-aprovado_em")[:50]

    # Assinantes ativos com plano pago — ordenados por quem vence mais cedo
    assinantes = (
        PerfilMedico.objects
        .filter(plano__in=("start", "plus", "elite"), user__is_active=True)
        .select_related("user")
        .order_by("plano_expiracao")
    )

    return render(request, "questionario/pagamentos/painel_pagamentos.html", {
        "pendentes":  pendentes,
        "historico":  historico,
        "assinantes": assinantes,
    })


@staff_member_required
def aprovar_solicitacao(request, sol_id):
    sol = get_object_or_404(SolicitacaoPlano, pk=sol_id)
    if request.method == "POST" and sol.status == "pendente":
        nota = request.POST.get("nota_admin", "").strip()
        sol.status      = "aprovado"
        sol.nota_admin  = nota
        sol.aprovado_por = request.user
        sol.aprovado_em = timezone.now()
        sol.save()

        # Atualiza perfil do usuário
        perfil, _ = PerfilMedico.objects.get_or_create(user=sol.user)
        perfil.plano = sol.plano
        # Renova ou define vencimento: +30 dias a partir de hoje
        # Se já tinha um plano ativo e não venceu, renova a partir da data atual de expiração
        agora = timezone.now()
        if perfil.plano_expiracao and perfil.plano_expiracao > agora:
            perfil.plano_expiracao = perfil.plano_expiracao + timezone.timedelta(days=30)
        else:
            perfil.plano_expiracao = agora + timezone.timedelta(days=30)
        # Garante que user está ativo
        if not perfil.user.is_active:
            perfil.user.is_active = True
            perfil.user.save(update_fields=["is_active"])
        perfil.save(update_fields=["plano", "plano_expiracao"])

        # Libera módulos do plano conforme especialidade
        esps = list(perfil.especialidades.values_list("codigo", flat=True))
        codigos = get_modulos_para_plano(esps, sol.plano)
        modulos = ModuloAvaliacao.objects.filter(codigo__in=codigos)
        perfil.modulos_liberados.set(modulos)

        # Programa de indicação: primeira conversão em plano pago concede dias extras a quem indicou
        indicacao = Indicacao.objects.filter(indicado=sol.user, recompensa_aplicada=False).select_related("indicador__perfil").first()
        if indicacao:
            perfil_indicador = getattr(indicacao.indicador, "perfil", None)
            if perfil_indicador:
                agora_recompensa = timezone.now()
                base = perfil_indicador.plano_expiracao if (perfil_indicador.plano_expiracao and perfil_indicador.plano_expiracao > agora_recompensa) else agora_recompensa
                perfil_indicador.plano_expiracao = base + timezone.timedelta(days=Indicacao.RECOMPENSA_DIAS)
                perfil_indicador.save(update_fields=["plano_expiracao"])
            indicacao.recompensa_aplicada = True
            indicacao.recompensa_aplicada_em = timezone.now()
            indicacao.save(update_fields=["recompensa_aplicada", "recompensa_aplicada_em"])

        # Notifica usuário
        _notificar_usuario_aprovado(sol, perfil.plano_expiracao)

        messages.success(
            request,
            f"✅ Plano {sol.get_plano_display()} ativado para "
            f"{sol.user.get_full_name() or sol.user.username} — "
            f"vence em {perfil.plano_expiracao.strftime('%d/%m/%Y')}."
        )
    return redirect("admin:pagamentos_painel")


@staff_member_required
def rejeitar_solicitacao(request, sol_id):
    sol = get_object_or_404(SolicitacaoPlano, pk=sol_id)
    if request.method == "POST" and sol.status == "pendente":
        nota = request.POST.get("nota_admin", "").strip()
        sol.status      = "rejeitado"
        sol.nota_admin  = nota
        sol.aprovado_por = request.user
        sol.aprovado_em = timezone.now()
        sol.save()

        # Notifica usuário
        _notificar_usuario_rejeitado(sol)

        messages.warning(request, f"Solicitação de {sol.user.get_full_name() or sol.user.username} rejeitada.")
    return redirect("admin:pagamentos_painel")


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers de e-mail
# ─────────────────────────────────────────────────────────────────────────────

def _notificar_admin_nova_solicitacao(sol: SolicitacaoPlano, request):
    """Envia e-mail ao admin quando uma nova solicitação chega."""
    painel_url = request.build_absolute_uri("/admin/questionario/solicitacaoplano/painel/")
    nome_user  = sol.user.get_full_name() or sol.user.username
    try:
        html = render_to_string("questionario/emails/email_solicitacao_admin.html", {
            "sol": sol,
            "nome_user": nome_user,
            "painel_url": painel_url,
        })
        send_mail(
            subject=f"[IntegraMente] Nova solicitação de plano — {nome_user} → {sol.get_plano_display()}",
            message=f"{nome_user} solicitou o plano {sol.get_plano_display()}.\nAcesse: {painel_url}",
            from_email=None,
            recipient_list=[settings.ADMIN_NOTIFY_EMAIL],
            html_message=html,
            fail_silently=True,
        )
    except Exception:
        pass


def _notificar_usuario_aprovado(sol: SolicitacaoPlano, expiracao=None):
    """Envia e-mail ao usuário quando o plano é aprovado."""
    if not sol.user.email:
        return
    nome = sol.user.first_name or sol.user.username
    try:
        html = render_to_string("questionario/emails/email_plano_aprovado.html", {
            "sol": sol,
            "nome": nome,
            "expiracao": expiracao,
        })
        send_mail(
            subject=f"IntegraMente — Seu plano {sol.get_plano_display()} foi ativado! 🎉",
            message=f"Olá {nome}! Seu plano {sol.get_plano_display()} foi ativado. Acesse https://integramente.pro/",
            from_email=None,
            recipient_list=[sol.user.email],
            html_message=html,
            fail_silently=True,
        )
    except Exception:
        pass


def _notificar_usuario_rejeitado(sol: SolicitacaoPlano):
    """Envia e-mail ao usuário quando a solicitação é rejeitada."""
    if not sol.user.email:
        return
    nome = sol.user.first_name or sol.user.username
    try:
        html = render_to_string("questionario/emails/email_plano_rejeitado.html", {
            "sol": sol,
            "nome": nome,
        })
        send_mail(
            subject="IntegraMente — Sobre sua solicitação de plano",
            message=f"Olá {nome}! Sua solicitação foi rejeitada. Motivo: {sol.nota_admin}",
            from_email=None,
            recipient_list=[sol.user.email],
            html_message=html,
            fail_silently=True,
        )
    except Exception:
        pass
