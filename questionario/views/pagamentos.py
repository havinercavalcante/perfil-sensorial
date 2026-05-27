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
    ModuloAvaliacao,
    MODULOS_POR_PLANO,
    PerfilMedico,
    SolicitacaoPlano,
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

    ctx = {
        "perfil": perfil,
        "plano_param": plano_param,
        "solicitacao_pendente": solicitacao_pendente,
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
    pendentes  = SolicitacaoPlano.objects.filter(status="pendente").select_related("user", "user__perfil")
    historico  = SolicitacaoPlano.objects.exclude(status="pendente").select_related("user", "user__perfil", "aprovado_por").order_by("-aprovado_em")[:50]
    return render(request, "questionario/pagamentos/painel_pagamentos.html", {
        "pendentes": pendentes,
        "historico": historico,
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
        perfil.save(update_fields=["plano"])

        # Libera módulos do plano
        codigos = MODULOS_POR_PLANO.get(sol.plano, [])
        modulos = ModuloAvaliacao.objects.filter(codigo__in=codigos)
        perfil.modulos_liberados.set(modulos)

        # Notifica usuário
        _notificar_usuario_aprovado(sol)

        messages.success(request, f"✅ Plano {sol.get_plano_display()} ativado para {sol.user.get_full_name() or sol.user.username}.")
    return redirect("painel_pagamentos")


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
    return redirect("painel_pagamentos")


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers de e-mail
# ─────────────────────────────────────────────────────────────────────────────

def _notificar_admin_nova_solicitacao(sol: SolicitacaoPlano, request):
    """Envia e-mail ao admin quando uma nova solicitação chega."""
    painel_url = request.build_absolute_uri("/pagamentos/painel/")
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


def _notificar_usuario_aprovado(sol: SolicitacaoPlano):
    """Envia e-mail ao usuário quando o plano é aprovado."""
    if not sol.user.email:
        return
    nome = sol.user.first_name or sol.user.username
    try:
        html = render_to_string("questionario/emails/email_plano_aprovado.html", {
            "sol": sol,
            "nome": nome,
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
