import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoSNAPIV, RespostaSNAPIV
from ..data.data_snap_iv import SNAP_IV_ITENS, SNAP_IV_SUBESCALAS, SNAP_IV_OPCOES, SNAP_IV_CORTE
from ..services import notificar_terapeuta


def _calcular_snap_iv(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    for key, sub in SNAP_IV_SUBESCALAS.items():
        itens = sub["itens"]
        valores = [respostas.get(n, 0) for n in itens]
        media = sum(valores) / len(itens)
        setattr(avaliacao, sub["campo"], round(media, 2))
    return avaliacao


def _build_resultado(avaliacao):
    resultado = []
    for key, sub in SNAP_IV_SUBESCALAS.items():
        media = getattr(avaliacao, sub["campo"]) or 0.0
        resultado.append({
            "key": key,
            "nome": sub["nome"],
            "cor": sub["cor"],
            "media": media,
            "significativo": media >= SNAP_IV_CORTE,
        })
    return resultado


# ── Views autenticadas ────────────────────────────────────────────────────────

@login_required
def nova_avaliacao_snap_iv(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('snap_iv'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo SNAP-IV.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    respondente = request.POST.get("respondente", "pais")
    if respondente not in ("pais", "professor"):
        respondente = "pais"
    av = AvaliacaoSNAPIV.objects.create(
        paciente=paciente, token=str(uuid.uuid4()), respondente=respondente
    )
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "id": av.id})
    return redirect("snap_iv_form", avaliacao_id=av.id)


@login_required
def snap_iv_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("snap_iv_resultado", avaliacao_id=avaliacao_id)

    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    itens_faltando = []

    if request.method == "POST":
        erros = []
        novas = {}
        for item in SNAP_IV_ITENS:
            val = request.POST.get(f"item_{item['numero']}")
            if val is None:
                erros.append(item["numero"])
            else:
                try:
                    v = int(val)
                    if v in (0, 1, 2, 3):
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
                RespostaSNAPIV.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=numero, defaults={"valor": valor}
                )
            avaliacao = _calcular_snap_iv(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            return redirect("snap_iv_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/snap_iv_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "itens": SNAP_IV_ITENS,
        "subescalas": SNAP_IV_SUBESCALAS,
        "opcoes": SNAP_IV_OPCOES,
        "respostas_salvas": respostas_salvas,
        "itens_faltando": itens_faltando,
    })


@login_required
def snap_iv_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("snap_iv_form", avaliacao_id=avaliacao_id)
    return render(request, "questionario/snap_iv_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "resultado": _build_resultado(avaliacao),
        "corte": SNAP_IV_CORTE,
    })


@login_required
def snap_iv_visualizar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, id=avaliacao_id, paciente__medico=request.user)
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    return render(request, "questionario/snap_iv_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "itens": SNAP_IV_ITENS,
        "subescalas": SNAP_IV_SUBESCALAS,
        "opcoes": SNAP_IV_OPCOES,
        "respostas_salvas": respostas_salvas,
        "itens_faltando": [],
        "readonly": True,
    })


@login_required
def snap_iv_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "SNAP-IV excluído com sucesso."})
        messages.success(request, "SNAP-IV excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_snap_iv(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("snap_iv_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_snap_iv(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, id=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("snap_iv_publico", kwargs={"token": avaliacao.token}))
    html = render_to_string("questionario/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(
            subject="SNAP-IV — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário SNAP-IV no link: {link}",
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

def snap_iv_publico(request, token):
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/concluido.html")

    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    itens_faltando = []

    if request.method == "POST":
        erros = []
        novas = {}
        for item in SNAP_IV_ITENS:
            val = request.POST.get(f"item_{item['numero']}")
            if val is None:
                erros.append(item["numero"])
            else:
                try:
                    v = int(val)
                    if v in (0, 1, 2, 3):
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
                RespostaSNAPIV.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=numero, defaults={"valor": valor}
                )
            avaliacao = _calcular_snap_iv(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            try:
                notificar_terapeuta(avaliacao.paciente, "snap_iv", request)
            except Exception:
                pass
            return render(request, "questionario/concluido.html")

    return render(request, "questionario/snap_iv_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "itens": SNAP_IV_ITENS,
        "subescalas": SNAP_IV_SUBESCALAS,
        "opcoes": SNAP_IV_OPCOES,
        "respostas_salvas": respostas_salvas,
        "itens_faltando": itens_faltando,
        "publico": True,
        "token": token,
    })
