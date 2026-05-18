import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Paciente, AvaliacaoBeery


_BEERY_ESCORE_PERCENTIL = {
    55: 0, 60: 0, 65: 1, 70: 2, 75: 5, 80: 9, 85: 16,
    90: 25, 95: 37, 100: 50, 105: 63, 110: 75, 115: 84,
    120: 91, 125: 95, 130: 98, 135: 99, 140: 99,
}


def _beery_escore_para_percentil(escore):
    if escore is None:
        return None
    # Encontra a entrada mais próxima
    chaves = sorted(_BEERY_ESCORE_PERCENTIL.keys())
    if escore <= chaves[0]:
        return _BEERY_ESCORE_PERCENTIL[chaves[0]]
    if escore >= chaves[-1]:
        return _BEERY_ESCORE_PERCENTIL[chaves[-1]]
    for i in range(len(chaves) - 1):
        if chaves[i] <= escore < chaves[i + 1]:
            return _BEERY_ESCORE_PERCENTIL[chaves[i]]
    return None


def _classificar_beery(escore):
    if escore is None:
        return "—"
    if escore < 70:
        return "Dificuldade significativa"
    elif escore < 85:
        return "Abaixo da média"
    elif escore <= 115:
        return "Médio"
    elif escore <= 130:
        return "Acima da média"
    else:
        return "Superior"


@login_required
def nova_avaliacao_beery(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('beery'):
        messages.error(request, "Você não tem acesso ao módulo Beery VMI.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoBeery.objects.create(paciente=paciente)
    return redirect("beery_form", avaliacao_id=av.id)


@login_required
def beery_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBeery, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if request.method == "POST":
        def _get_int(name):
            try:
                return int(request.POST.get(name, "").strip())
            except (ValueError, AttributeError):
                return None

        avaliacao.idade_anos = _get_int("idade_anos")
        avaliacao.idade_meses = _get_int("idade_meses")
        avaliacao.vmi_raw = _get_int("vmi_raw")
        avaliacao.vp_raw = _get_int("vp_raw")
        avaliacao.mc_raw = _get_int("mc_raw")
        avaliacao.vmi_escore = _get_int("vmi_escore")
        avaliacao.vp_escore = _get_int("vp_escore")
        avaliacao.mc_escore = _get_int("mc_escore")
        avaliacao.vmi_percentil = _beery_escore_para_percentil(avaliacao.vmi_escore)
        avaliacao.vp_percentil = _beery_escore_para_percentil(avaliacao.vp_escore)
        avaliacao.mc_percentil = _beery_escore_para_percentil(avaliacao.mc_escore)
        avaliacao.save()
        messages.success(request, "Beery VMI salvo com sucesso.")
        return redirect("beery_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/avaliacoes/beery_form.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
    })


@login_required
def beery_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBeery, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    subtestes = [
        {
            "nome": "VMI (Integração Visuomotora)",
            "raw": avaliacao.vmi_raw,
            "escore": avaliacao.vmi_escore,
            "percentil": avaliacao.vmi_percentil,
            "classificacao": _classificar_beery(avaliacao.vmi_escore),
        },
        {
            "nome": "Percepção Visual",
            "raw": avaliacao.vp_raw,
            "escore": avaliacao.vp_escore,
            "percentil": avaliacao.vp_percentil,
            "classificacao": _classificar_beery(avaliacao.vp_escore),
        },
        {
            "nome": "Coordenação Motora",
            "raw": avaliacao.mc_raw,
            "escore": avaliacao.mc_escore,
            "percentil": avaliacao.mc_percentil,
            "classificacao": _classificar_beery(avaliacao.mc_escore),
        },
    ]

    return render(request, "questionario/avaliacoes/beery_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "subtestes": subtestes,
        "subtestes_json": json.dumps([
            {"nome": s["nome"], "escore": s["escore"] or 0} for s in subtestes
        ]),
    })


@login_required
def beery_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoBeery, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação Beery excluída com sucesso."})
        messages.success(request, "Avaliação Beery excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_beery(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoBeery, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("beery_resultado", avaliacao_id=avaliacao_id)
    return redirect("beery_resultado", avaliacao_id=avaliacao_id)
