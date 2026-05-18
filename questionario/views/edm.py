import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Paciente, AvaliacaoEDM


def _classificar_qm(qm):
    if qm is None:
        return "—"
    if qm >= 130:
        return "Superior"
    elif qm >= 110:
        return "Normal Alto"
    elif qm >= 90:
        return "Normal Médio"
    elif qm >= 70:
        return "Normal Baixo"
    elif qm >= 50:
        return "Inferior"
    else:
        return "Muito Inferior"


@login_required
def nova_avaliacao_edm(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('edm'):
        messages.error(request, "Você não tem acesso ao módulo EDM.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoEDM.objects.create(paciente=paciente)
    return redirect("edm_form", avaliacao_id=av.id)


@login_required
def edm_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoEDM, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if request.method == "POST":
        def _get_int(name):
            try:
                v = int(request.POST.get(name, "").strip())
                return v if v >= 0 else None
            except (ValueError, AttributeError):
                return None

        mf = _get_int("motricidade_fina")
        ma = _get_int("motricidade_ampla")
        eq = _get_int("equilibrio")
        ec = _get_int("esquema_corporal")
        oe = _get_int("organizacao_espacial")
        ot = _get_int("organizacao_temporal")
        lat = request.POST.get("lateralidade", "").strip() or None

        avaliacao.idade_motricidade_fina = mf
        avaliacao.idade_motricidade_ampla = ma
        avaliacao.idade_equilibrio = eq
        avaliacao.idade_esquema_corporal = ec
        avaliacao.idade_organizacao_espacial = oe
        avaliacao.idade_organizacao_temporal = ot
        avaliacao.lateralidade = lat

        idades = [v for v in [mf, ma, eq, ec, oe, ot] if v is not None]
        if idades:
            img = sum(idades) / len(idades)
            avaliacao.idade_motora_geral = round(img, 1)
            hoje = __import__('django.utils.timezone', fromlist=['now']).now().date()
            b = paciente.data_nascimento
            ic = (hoje.year - b.year) * 12 + (hoje.month - b.month)
            if ic > 0:
                avaliacao.quociente_motor = round(img / ic * 100, 1)
            else:
                avaliacao.quociente_motor = None
        else:
            avaliacao.idade_motora_geral = None
            avaliacao.quociente_motor = None

        avaliacao.save()
        messages.success(request, "EDM salvo com sucesso.")
        return redirect("edm_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/avaliacoes/edm_form.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
    })


@login_required
def edm_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoEDM, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    dominios = [
        {"nome": "Motricidade Fina",       "valor": avaliacao.idade_motricidade_fina},
        {"nome": "Motricidade Ampla",       "valor": avaliacao.idade_motricidade_ampla},
        {"nome": "Equilíbrio",              "valor": avaliacao.idade_equilibrio},
        {"nome": "Esquema Corporal",        "valor": avaliacao.idade_esquema_corporal},
        {"nome": "Organização Espacial",    "valor": avaliacao.idade_organizacao_espacial},
        {"nome": "Organização Temporal",    "valor": avaliacao.idade_organizacao_temporal},
    ]

    lat_label = dict(AvaliacaoEDM.LATERALIDADE_CHOICES).get(avaliacao.lateralidade, "—") if avaliacao.lateralidade else "—"

    return render(request, "questionario/avaliacoes/edm_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "dominios": dominios,
        "lat_label": lat_label,
        "qm_classificacao": _classificar_qm(avaliacao.quociente_motor),
        "dominios_json": json.dumps([{"nome": d["nome"], "valor": d["valor"] or 0} for d in dominios]),
    })


@login_required
def edm_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoEDM, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação EDM excluída com sucesso."})
        messages.success(request, "Avaliação EDM excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_edm(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoEDM, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("edm_resultado", avaliacao_id=avaliacao_id)
    return redirect("edm_resultado", avaliacao_id=avaliacao_id)
