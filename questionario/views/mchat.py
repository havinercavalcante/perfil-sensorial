import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoMCHAT, RespostaMCHAT
from ..data.data_mchat import MCHAT_ITENS, MCHAT_RISCO
from ..services import notificar_terapeuta


def _calcular_mchat(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    score = 0
    for item in MCHAT_ITENS:
        resposta_bool = respostas.get(item["numero"])
        if resposta_bool is None:
            continue
        # True=Sim, False=Não
        if item["risco_sim"]:
            if resposta_bool:
                score += 1
        else:
            if not resposta_bool:
                score += 1
    avaliacao.score_total = score

    for nivel, label, min_v, max_v, _ in MCHAT_RISCO:
        if min_v <= score <= max_v:
            avaliacao.classificacao = nivel
            break
    return avaliacao


# ── Views autenticadas ────────────────────────────────────────────────────────

@login_required
def nova_avaliacao_mchat(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('mchat'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo M-CHAT-R.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoMCHAT.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "id": av.id})
    return redirect("mchat_form", avaliacao_id=av.id)


@login_required
def mchat_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoMCHAT, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("mchat_resultado", avaliacao_id=avaliacao_id)

    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    itens_faltando = []

    if request.method == "POST":
        erros = []
        novas = {}
        for item in MCHAT_ITENS:
            val = request.POST.get(f"item_{item['numero']}")
            if val is None:
                erros.append(item["numero"])
            elif val in ("true", "1"):
                novas[item["numero"]] = True
            elif val in ("false", "0"):
                novas[item["numero"]] = False
            else:
                erros.append(item["numero"])

        if erros and request.POST.get("confirmar_incompleto") != "1":
            respostas_salvas.update(novas)
            itens_faltando = erros
        else:
            for numero, valor in novas.items():
                RespostaMCHAT.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=numero, defaults={"valor": valor}
                )
            avaliacao = _calcular_mchat(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            return redirect("mchat_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/mchat_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "itens": MCHAT_ITENS,
        "respostas_salvas": respostas_salvas,
        "itens_faltando": itens_faltando,
    })


@login_required
def mchat_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoMCHAT, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("mchat_form", avaliacao_id=avaliacao_id)
    risco_info = next((r for r in MCHAT_RISCO if r[0] == avaliacao.classificacao), MCHAT_RISCO[0])
    return render(request, "questionario/mchat_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "risco_info": risco_info,
        "risco_lista": MCHAT_RISCO,
    })


@login_required
def mchat_visualizar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoMCHAT, id=avaliacao_id, paciente__medico=request.user)
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    return render(request, "questionario/mchat_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "itens": MCHAT_ITENS,
        "respostas_salvas": respostas_salvas,
        "itens_faltando": [],
        "readonly": True,
    })


@login_required
def mchat_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoMCHAT, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "M-CHAT-R excluído com sucesso."})
        messages.success(request, "M-CHAT-R excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_mchat(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoMCHAT, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("mchat_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_mchat(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoMCHAT, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    if not avaliacao.token:
        avaliacao.token = str(uuid.uuid4())
        avaliacao.save(update_fields=["token"])
    from django.template.loader import render_to_string
    link = request.build_absolute_uri(reverse("mchat_publico", kwargs={"token": avaliacao.token}))
    html = render_to_string("questionario/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(
            subject="M-CHAT-R — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário M-CHAT-R no link: {link}",
            from_email=None,
            recipient_list=[email_dest],
            html_message=html,
            fail_silently=False,
        )
    except Exception as exc:
        if is_ajax:
            return JsonResponse({"ok": False, "message": f"Falha ao enviar e-mail: {exc}"})
        messages.error(request, f"Falha ao enviar e-mail: {exc}")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    avaliacao.email_enviado_em = tz.now()
    avaliacao.save(update_fields=["email_enviado_em"])
    if is_ajax:
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)


# ── View pública (token) ──────────────────────────────────────────────────────

def mchat_publico(request, token):
    avaliacao = get_object_or_404(AvaliacaoMCHAT, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/concluido.html")

    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    itens_faltando = []

    if request.method == "POST":
        erros = []
        novas = {}
        for item in MCHAT_ITENS:
            val = request.POST.get(f"item_{item['numero']}")
            if val is None:
                erros.append(item["numero"])
            elif val in ("true", "1"):
                novas[item["numero"]] = True
            elif val in ("false", "0"):
                novas[item["numero"]] = False
            else:
                erros.append(item["numero"])

        if erros and request.POST.get("confirmar_incompleto") != "1":
            respostas_salvas.update(novas)
            itens_faltando = erros
        else:
            for numero, valor in novas.items():
                RespostaMCHAT.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=numero, defaults={"valor": valor}
                )
            avaliacao = _calcular_mchat(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            try:
                notificar_terapeuta(avaliacao.paciente, "mchat", request)
            except Exception:
                pass
            return render(request, "questionario/concluido.html")

    return render(request, "questionario/mchat_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "itens": MCHAT_ITENS,
        "respostas_salvas": respostas_salvas,
        "itens_faltando": itens_faltando,
        "publico": True,
        "token": token,
    })
