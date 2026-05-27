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
    return redirect("edm_form", avaliacao_id=av.uuid)


@login_required
def edm_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoEDM, uuid=avaliacao_id, paciente__medico=request.user)
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
    avaliacao = get_object_or_404(AvaliacaoEDM, uuid=avaliacao_id, paciente__medico=request.user)
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

    todas_av = list(paciente.avaliacoes_edm.order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    comparativo_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av])
    campos_edm = [
        {"nome": "Mot. Fina",       "campo": "idade_motricidade_fina"},
        {"nome": "Mot. Ampla",      "campo": "idade_motricidade_ampla"},
        {"nome": "Equilíbrio",      "campo": "idade_equilibrio"},
        {"nome": "Esq. Corporal",   "campo": "idade_esquema_corporal"},
        {"nome": "Org. Espacial",   "campo": "idade_organizacao_espacial"},
        {"nome": "Org. Temporal",   "campo": "idade_organizacao_temporal"},
    ]
    cores_linha = ["#2E7D6B", "#3E73D1", "#E8793A", "#9B59B6", "#E8B84B", "#C0392B"]
    comparativo_datasets = []
    for i, dom in enumerate(campos_edm):
        valores = [(getattr(av, dom["campo"]) or 0) for av in todas_av]
        comparativo_datasets.append({"label": dom["nome"], "data": valores, "borderColor": cores_linha[i], "backgroundColor": cores_linha[i] + "33", "tension": 0.3})

    return render(request, "questionario/avaliacoes/edm_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "dominios": dominios,
        "lat_label": lat_label,
        "qm_classificacao": _classificar_qm(avaliacao.quociente_motor),
        "dominios_json": json.dumps([{"nome": d["nome"], "valor": d["valor"] or 0} for d in dominios]),
        "comparativo_labels": comparativo_labels,
        "comparativo_datasets": json.dumps(comparativo_datasets),
        "tem_comparativo": len(todas_av) > 1,
        "outras_avaliacoes": outras,
    })


@login_required
def edm_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoEDM, uuid=avaliacao_id, paciente__medico=request.user)
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
    avaliacao = get_object_or_404(AvaliacaoEDM, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("edm_resultado", avaliacao_id=avaliacao_id)
    return redirect("edm_resultado", avaliacao_id=avaliacao_id)
