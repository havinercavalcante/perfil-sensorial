import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoCARS, RespostaCARS
from ..data.data_cars import CARS_ITENS, CARS_OPCOES, CARS_CLASSIFICACAO
from ..services import notificar_terapeuta


def _calcular_cars(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    total = sum(respostas.get(i["numero"], 1.0) for i in CARS_ITENS)
    avaliacao.score_total = round(total, 1)
    for codigo, label, min_v, max_v, _ in CARS_CLASSIFICACAO:
        if min_v <= total <= max_v:
            avaliacao.classificacao = codigo
            break
    return avaliacao


# ── Views autenticadas ────────────────────────────────────────────────────────

@login_required
def nova_avaliacao_cars(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('cars'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo CARS-2.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoCARS.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "id": av.id})
    return redirect("cars_form", avaliacao_id=av.id)


@login_required
def cars_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoCARS, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("cars_resultado", avaliacao_id=avaliacao_id)

    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}

    if request.method == "POST":
        novas = {}
        for item in CARS_ITENS:
            val = request.POST.get(f"item_{item['numero']}")
            if val is not None:
                try:
                    v = float(val)
                    if v in CARS_OPCOES:
                        novas[item["numero"]] = v
                except (ValueError, TypeError):
                    pass
        for numero, valor in novas.items():
            RespostaCARS.objects.update_or_create(
                avaliacao=avaliacao, numero_item=numero, defaults={"valor": valor}
            )
        avaliacao = _calcular_cars(avaliacao)
        avaliacao.status = "concluida"
        avaliacao.save()
        return redirect("cars_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/cars_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "itens": CARS_ITENS,
        "opcoes": CARS_OPCOES,
        "respostas_salvas": respostas_salvas,
    })


@login_required
def cars_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoCARS, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("cars_form", avaliacao_id=avaliacao_id)
    class_info = next(
        (c for c in CARS_CLASSIFICACAO if c[0] == avaliacao.classificacao), CARS_CLASSIFICACAO[0]
    )
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    return render(request, "questionario/cars_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "itens": CARS_ITENS,
        "respostas": respostas,
        "class_info": class_info,
        "classificacoes": CARS_CLASSIFICACAO,
    })


@login_required
def cars_visualizar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoCARS, id=avaliacao_id, paciente__medico=request.user)
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    return render(request, "questionario/cars_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "itens": CARS_ITENS,
        "opcoes": CARS_OPCOES,
        "respostas_salvas": respostas_salvas,
        "readonly": True,
    })


@login_required
def cars_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoCARS, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "CARS-2 excluído com sucesso."})
        messages.success(request, "CARS-2 excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_cars(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoCARS, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("cars_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_cars(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoCARS, id=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("cars_publico", kwargs={"token": avaliacao.token}))
    html = render_to_string("questionario/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(
            subject="CARS-2 — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nPreencha o questionário CARS-2 no link: {link}",
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

def cars_publico(request, token):
    avaliacao = get_object_or_404(AvaliacaoCARS, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/concluido.html")

    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}

    if request.method == "POST":
        novas = {}
        for item in CARS_ITENS:
            val = request.POST.get(f"item_{item['numero']}")
            if val is not None:
                try:
                    v = float(val)
                    if v in CARS_OPCOES:
                        novas[item["numero"]] = v
                except (ValueError, TypeError):
                    pass
        for numero, valor in novas.items():
            RespostaCARS.objects.update_or_create(
                avaliacao=avaliacao, numero_item=numero, defaults={"valor": valor}
            )
        avaliacao = _calcular_cars(avaliacao)
        avaliacao.status = "concluida"
        avaliacao.save()
        try:
            notificar_terapeuta(avaliacao.paciente, "cars", request)
        except Exception:
            pass
        return render(request, "questionario/concluido.html")

    return render(request, "questionario/cars_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "itens": CARS_ITENS,
        "opcoes": CARS_OPCOES,
        "respostas_salvas": respostas_salvas,
        "publico": True,
        "token": token,
    })
