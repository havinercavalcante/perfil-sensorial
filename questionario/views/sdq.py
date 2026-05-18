import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoSDQ, RespostaSDQ
from ..data.data_sdq import SDQ_ITENS, SDQ_SUBESCALAS, SDQ_OPCOES, SDQ_CORTE
from ..services import notificar_terapeuta


def _calcular_sdq(avaliacao):
    """Calcula pontuações por subescala e total de dificuldades."""
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}

    for key, sub in SDQ_SUBESCALAS.items():
        total = 0
        for item in SDQ_ITENS:
            if item["subescala"] != key:
                continue
            val = respostas.get(item["numero"], 0)
            total += (2 - val) if item["reverso"] else val
        setattr(avaliacao, sub["campo"], total)

    # Total de Dificuldades = soma das 4 subescalas (excl. prossocial)
    avaliacao.pont_total_dificuldades = (
        (avaliacao.pont_emocional or 0)
        + (avaliacao.pont_conduta or 0)
        + (avaliacao.pont_hiperatividade or 0)
        + (avaliacao.pont_pares or 0)
    )
    return avaliacao


def _classificar(score, corte_list):
    for label, min_v, max_v in corte_list:
        if min_v <= score <= max_v:
            return label
    return corte_list[-1][0]


def _build_resultado(avaliacao):
    resultado = []
    for key, sub in SDQ_SUBESCALAS.items():
        score = getattr(avaliacao, sub["campo"]) or 0
        max_score = 10
        resultado.append({
            "key": key,
            "nome": sub["nome"],
            "cor": sub["cor"],
            "score": score,
            "max": max_score,
            "pct": int(score / max_score * 100),
            "classificacao": _classificar(score, SDQ_CORTE[key]),
        })
    total = avaliacao.pont_total_dificuldades or 0
    return resultado, total, _classificar(total, SDQ_CORTE["total"])


# ── Views autenticadas ────────────────────────────────────────────────────────

@login_required
def nova_avaliacao_sdq(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('sdq'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo SDQ.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoSDQ.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "id": av.id})
    return redirect("sdq_form", avaliacao_id=av.id)


@login_required
def sdq_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSDQ, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("sdq_resultado", avaliacao_id=avaliacao_id)

    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    itens_faltando = []

    if request.method == "POST":
        erros = []
        novas = {}
        for item in SDQ_ITENS:
            val = request.POST.get(f"item_{item['numero']}")
            if val is None:
                erros.append(item["numero"])
            else:
                try:
                    v = int(val)
                    if v in (0, 1, 2):
                        novas[item["numero"]] = v
                    else:
                        erros.append(item["numero"])
                except (ValueError, TypeError):
                    erros.append(item["numero"])

        if erros and request.POST.get("confirmar_incompleto") != "1":
            respostas_salvas.update(novas)
            itens_faltando = erros
        else:
            for numero, valor in novas.items():
                RespostaSDQ.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=numero, defaults={"valor": valor}
                )
            avaliacao = _calcular_sdq(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            return redirect("sdq_resultado", avaliacao_id=avaliacao_id)

    itens_render = [
        {**item, "resposta_salva": respostas_salvas.get(item["numero"]),
         "faltando": item["numero"] in itens_faltando}
        for item in SDQ_ITENS
    ]
    return render(request, "questionario/avaliacoes/sdq_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "itens": itens_render,
        "opcoes": SDQ_OPCOES,
        "subescalas": SDQ_SUBESCALAS,
        "itens_faltando": itens_faltando,
    })


@login_required
def sdq_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSDQ, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("sdq_form", avaliacao_id=avaliacao_id)
    resultado, total, class_total = _build_resultado(avaliacao)
    return render(request, "questionario/avaliacoes/sdq_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "resultado": resultado,
        "total": total,
        "class_total": class_total,
    })


@login_required
def sdq_visualizar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSDQ, id=avaliacao_id, paciente__medico=request.user)
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    itens_render = [
        {**item, "resposta_salva": respostas_salvas.get(item["numero"]), "faltando": False}
        for item in SDQ_ITENS
    ]
    return render(request, "questionario/avaliacoes/sdq_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "itens": itens_render,
        "subescalas": SDQ_SUBESCALAS,
        "opcoes": SDQ_OPCOES,
        "respostas_salvas": respostas_salvas,
        "itens_faltando": [],
        "readonly": True,
    })


@login_required
def sdq_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSDQ, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "SDQ excluído com sucesso."})
        messages.success(request, "SDQ excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_sdq(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSDQ, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("sdq_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_sdq(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoSDQ, id=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("sdq_publico", kwargs={"token": avaliacao.token}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(
            subject="SDQ — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário SDQ no link: {link}",
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

def sdq_publico(request, token):
    avaliacao = get_object_or_404(AvaliacaoSDQ, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")

    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    itens_faltando = []

    if request.method == "POST":
        erros = []
        novas = {}
        for item in SDQ_ITENS:
            val = request.POST.get(f"item_{item['numero']}")
            if val is None:
                erros.append(item["numero"])
            else:
                try:
                    v = int(val)
                    if v in (0, 1, 2):
                        novas[item["numero"]] = v
                    else:
                        erros.append(item["numero"])
                except (ValueError, TypeError):
                    erros.append(item["numero"])

        if erros and request.POST.get("confirmar_incompleto") != "1":
            respostas_salvas.update(novas)
            itens_faltando = erros
        else:
            for numero, valor in novas.items():
                RespostaSDQ.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=numero, defaults={"valor": valor}
                )
            avaliacao = _calcular_sdq(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            try:
                notificar_terapeuta(avaliacao.paciente, "sdq", request)
            except Exception:
                pass
            return render(request, "questionario/dashboard/concluido.html")

    itens_render = [
        {**item, "resposta_salva": respostas_salvas.get(item["numero"]),
         "faltando": item["numero"] in itens_faltando}
        for item in SDQ_ITENS
    ]
    return render(request, "questionario/avaliacoes/sdq_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "itens": itens_render,
        "opcoes": SDQ_OPCOES,
        "subescalas": SDQ_SUBESCALAS,
        "itens_faltando": itens_faltando,
        "publico": True,
        "token": token,
    })
