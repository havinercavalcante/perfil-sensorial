import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Paciente, AvaliacaoMABC2


def _mabc2_escore_para_percentil(escore_total):
    """Conversão aproximada escore total (3-57) → percentil."""
    tabela = [
        (3, 0), (6, 0), (9, 1), (12, 2), (15, 5), (18, 9),
        (21, 16), (24, 25), (27, 37), (30, 50), (33, 63),
        (36, 75), (39, 84), (42, 91), (45, 95), (48, 98),
        (51, 99), (57, 99),
    ]
    if escore_total is None:
        return None
    for escore, perc in tabela:
        if escore_total <= escore:
            return perc
    return 99


def _classificar_mabc2(percentil):
    if percentil is None:
        return "—"
    if percentil <= 5:
        return "Dificuldade significativa"
    elif percentil <= 15:
        return "Risco"
    else:
        return "Típico"


@login_required
def nova_avaliacao_mabc2(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('mabc2'):
        messages.error(request, "Você não tem acesso ao módulo MABC-2.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoMABC2.objects.create(paciente=paciente, faixa_etaria="3_6")
    return redirect("mabc2_form", avaliacao_id=av.id)


@login_required
def mabc2_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoMABC2, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if request.method == "POST":
        def _get_float(name):
            try:
                return float(request.POST.get(name, "").strip())
            except (ValueError, AttributeError):
                return None

        def _get_int(name):
            try:
                return int(request.POST.get(name, "").strip())
            except (ValueError, AttributeError):
                return None

        avaliacao.faixa_etaria = request.POST.get("faixa_etaria", "3_6")
        avaliacao.md1_raw = _get_float("md1_raw")
        avaliacao.md2_raw = _get_float("md2_raw")
        avaliacao.md3_raw = _get_float("md3_raw")
        avaliacao.ac1_raw = _get_float("ac1_raw")
        avaliacao.ac2_raw = _get_float("ac2_raw")
        avaliacao.eq1_raw = _get_float("eq1_raw")
        avaliacao.eq2_raw = _get_float("eq2_raw")
        avaliacao.eq3_raw = _get_float("eq3_raw")
        avaliacao.md_escore = _get_int("md_escore")
        avaliacao.ac_escore = _get_int("ac_escore")
        avaliacao.eq_escore = _get_int("eq_escore")

        scores = [avaliacao.md_escore, avaliacao.ac_escore, avaliacao.eq_escore]
        if all(s is not None for s in scores):
            avaliacao.escore_total = sum(scores)
            avaliacao.percentil = _mabc2_escore_para_percentil(avaliacao.escore_total)
        avaliacao.save()
        messages.success(request, "MABC-2 salvo com sucesso.")
        return redirect("mabc2_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/mabc2_form.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "faixa_choices": AvaliacaoMABC2.FAIXA_CHOICES,
    })


@login_required
def mabc2_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoMABC2, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    classificacao = _classificar_mabc2(avaliacao.percentil)
    faixa_label = dict(AvaliacaoMABC2.FAIXA_CHOICES).get(avaliacao.faixa_etaria, "—")

    componentes = [
        {"nome": "Destreza Manual", "escore": avaliacao.md_escore},
        {"nome": "Arremesso/Recepção", "escore": avaliacao.ac_escore},
        {"nome": "Equilíbrio", "escore": avaliacao.eq_escore},
    ]

    return render(request, "questionario/mabc2_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "componentes": componentes,
        "classificacao": classificacao,
        "faixa_label": faixa_label,
        "componentes_json": json.dumps([{"nome": c["nome"], "escore": c["escore"] or 0} for c in componentes]),
    })


@login_required
def mabc2_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoMABC2, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação MABC-2 excluída com sucesso."})
        messages.success(request, "Avaliação MABC-2 excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_mabc2(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoMABC2, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("mabc2_resultado", avaliacao_id=avaliacao_id)
    return redirect("mabc2_resultado", avaliacao_id=avaliacao_id)
