import json
import uuid as _uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Paciente, AvaliacaoProade, RespostaProade
from ..data.data_proade import (
    PROADE_AREAS, PROADE_ITENS, PROADE_OPCOES, PROADE_MAX_AREA, PROADE_MAX_TOTAL,
    PROADE_CLASSIFICACAO, classificar_area_proade, cor_classificacao_proade,
)

_TITULO = "PROADE — Avaliação do Desempenho Escolar"
_COR    = "#3E73D1"

_CAMPOS_AREA = {
    "linguagem_oral": "pont_linguagem_oral",
    "leitura":        "pont_leitura",
    "escrita":        "pont_escrita",
    "matematica":     "pont_matematica",
    "psicossocial":   "pont_psicossocial",
}


def _itens_da_pagina(area_id: str, ano: int):
    return PROADE_ITENS.get(area_id, {}).get(ano, [])


def _calcular_e_salvar(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    total = 0
    for area in PROADE_AREAS:
        itens = _itens_da_pagina(area["id"], avaliacao.ano_escolar)
        pts = sum(respostas.get(n, 0) for n, _ in itens)
        setattr(avaliacao, _CAMPOS_AREA[area["id"]], pts)
        total += pts
    avaliacao.pont_total = total
    avaliacao.status = "concluida"
    avaliacao.save()


def _ctx_resultado(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    areas_resultado = []
    for area in PROADE_AREAS:
        itens = _itens_da_pagina(area["id"], avaliacao.ano_escolar)
        pts = getattr(avaliacao, _CAMPOS_AREA[area["id"]]) or 0
        class_label = classificar_area_proade(pts)
        areas_resultado.append({
            "id":           area["id"],
            "nome":         area["nome"],
            "cor":          area["cor"],
            "icone":        area["icone"],
            "pontos":       pts,
            "max":          PROADE_MAX_AREA,
            "classificacao": class_label,
            "cor_fundo":    cor_classificacao_proade(class_label),
            "itens":        [(n, t, respostas.get(n, 0)) for n, t in itens],
            "pct":          round(pts / PROADE_MAX_AREA * 100),
        })

    todas = list(avaliacao.paciente.avaliacoes_proade.filter(status="concluida").order_by("data"))
    outras = [a for a in todas if a.id != avaliacao.id]

    opcoes_label = {o["valor"]: o["label"] for o in PROADE_OPCOES}

    return {
        "avaliacao":    avaliacao,
        "paciente":     avaliacao.paciente,
        "areas":        areas_resultado,
        "total":        avaliacao.pont_total or 0,
        "max_total":    PROADE_MAX_TOTAL,
        "classificacao_total": classificar_area_proade(
            round((avaliacao.pont_total or 0) / PROADE_MAX_TOTAL * PROADE_MAX_AREA)
        ),
        "corte":        PROADE_CLASSIFICACAO,
        "cor":          _COR,
        "opcoes_label": opcoes_label,
        "outras_avaliacoes": outras,
        "tem_comparativo":   len(todas) > 1,
        "comparativo_labels":   json.dumps([a.data.strftime("%d/%m/%Y") for a in todas]),
        "comparativo_datasets": json.dumps([
            {
                "label": area["nome"],
                "data":  [getattr(a, _CAMPOS_AREA[area["id"]]) or 0 for a in todas],
                "borderColor":     area["cor"],
                "backgroundColor": area["cor"] + "33",
                "tension": 0.3,
            }
            for area in PROADE_AREAS
        ]),
    }


@login_required
def nova_avaliacao_proade(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not request.user.perfil.tem_acesso("proade"):
        if is_ajax:
            return JsonResponse({"ok": False, "error": "Módulo não disponível."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo PROADE.")
        return redirect("detalhe_paciente", paciente_id=paciente_id)

    if request.method == "POST":
        try:
            ano = int(request.POST.get("ano_escolar", 1))
            ano = max(1, min(5, ano))
        except (ValueError, TypeError):
            ano = 1
        av = AvaliacaoProade.objects.create(paciente=paciente, ano_escolar=ano)
        if is_ajax:
            return JsonResponse({"ok": True, "uuid": str(av.uuid)})
        return redirect("proade_form", avaliacao_id=av.uuid, pagina=1)

    if is_ajax:
        from django.urls import reverse
        url = reverse("nova_avaliacao_proade", kwargs={"paciente_id": paciente_id})
        return JsonResponse({"ok": True, "redirect": url})
    return render(request, "questionario/avaliacoes/proade_selecionar_ano.html", {
        "paciente": paciente,
        "anos": [(i, f"{i}º ano") for i in range(1, 6)],
    })


@login_required
def proade_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoProade, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("proade_resultado", avaliacao_id=avaliacao_id)

    total_paginas = len(PROADE_AREAS)
    pagina = max(1, min(pagina, total_paginas))

    area = PROADE_AREAS[pagina - 1]
    itens = _itens_da_pagina(area["id"], avaliacao.ano_escolar)
    numeros = [n for n, _ in itens]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=numeros)}

    faltando = []
    if request.method == "POST":
        novas = {}
        erros = []
        vals = {o["valor"] for o in PROADE_OPCOES}
        for n, _ in itens:
            val = request.POST.get(f"item_{n}")
            if val is None:
                erros.append(n)
            else:
                try:
                    v = int(val)
                    if v in vals:
                        novas[n] = v
                    else:
                        erros.append(n)
                except (ValueError, TypeError):
                    erros.append(n)

        confirmar = request.POST.get("confirmar_incompleto") == "1"
        if erros and not confirmar:
            respostas_salvas = {**respostas_salvas, **novas}
            faltando = erros
        else:
            for n, v in novas.items():
                RespostaProade.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=n,
                    defaults={"valor": v, "area": area["id"]}
                )
            if pagina < total_paginas:
                avaliacao.pagina_atual = pagina + 1
                avaliacao.save(update_fields=["pagina_atual"])
                return redirect("proade_form", avaliacao_id=avaliacao_id, pagina=pagina + 1)
            else:
                _calcular_e_salvar(avaliacao)
                return redirect("proade_resultado", avaliacao_id=avaliacao_id)

    itens_ctx = [
        {"num": n, "texto": t, "resposta": respostas_salvas.get(n), "erro": n in faltando}
        for n, t in itens
    ]
    return render(request, "questionario/avaliacoes/proade_form.html", {
        "avaliacao":      avaliacao,
        "paciente":       avaliacao.paciente,
        "area":           area,
        "itens":          itens_ctx,
        "opcoes":         PROADE_OPCOES,
        "faltando":       faltando,
        "pagina":         pagina,
        "total_paginas":  total_paginas,
        "areas":          PROADE_AREAS,
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "readonly":       False,
    })


@login_required
def proade_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoProade, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("proade_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual or 1)
    return render(request, "questionario/avaliacoes/proade_resultado.html", _ctx_resultado(avaliacao))


@login_required
def proade_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoProade, uuid=avaliacao_id, paciente__medico=request.user)
    total_paginas = len(PROADE_AREAS)
    pagina = max(1, min(pagina, total_paginas))
    area = PROADE_AREAS[pagina - 1]
    itens = _itens_da_pagina(area["id"], avaliacao.ano_escolar)
    numeros = [n for n, _ in itens]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=numeros)}
    itens_ctx = [
        {"num": n, "texto": t, "resposta": respostas_salvas.get(n), "erro": False}
        for n, t in itens
    ]
    return render(request, "questionario/avaliacoes/proade_form.html", {
        "avaliacao":      avaliacao,
        "paciente":       avaliacao.paciente,
        "area":           area,
        "itens":          itens_ctx,
        "opcoes":         PROADE_OPCOES,
        "faltando":       [],
        "pagina":         pagina,
        "total_paginas":  total_paginas,
        "areas":          PROADE_AREAS,
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "readonly":       True,
    })


@login_required
def proade_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoProade, uuid=avaliacao_id, paciente__medico=request.user)
    pid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "PROADE excluído com sucesso."})
    return redirect("detalhe_paciente", paciente_id=pid)


@login_required
def salvar_observacoes_proade(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoProade, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
    return redirect("proade_resultado", avaliacao_id=avaliacao_id)
