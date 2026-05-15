import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Paciente, AvaliacaoCARS, RespostaCARS
from ..data.data_cars import CARS_ITENS, CARS_OPCOES, CARS_CLASSIFICACAO


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
