import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Paciente, AvaliacaoLinguagem, RespostaLinguagem
from ..data.data_linguagem import LINGUAGEM_DOMINIOS, LINGUAGEM_OPCOES, LINGUAGEM_CLASSIFICACAO
from ..services import notificar_terapeuta

TOTAL_PAGINAS = len(LINGUAGEM_DOMINIOS)

_URL_NAMES = {
    "url_form_name": "linguagem_form",
    "url_publico_name": "linguagem_publico",
    "url_visualizar_name": "linguagem_visualizar",
    "url_resultado_name": "linguagem_resultado",
    "avaliacao_titulo": "Avaliação de Linguagem",
}


def _calcular_linguagem(avaliacao):
    for dom in LINGUAGEM_DOMINIOS:
        itens = [n for n, _ in dom["itens"]]
        respostas = avaliacao.respostas.filter(dominio=dom["key"], numero_item__in=itens)
        total = sum(r.valor for r in respostas)
        setattr(avaliacao, dom["campo"], total)
    return avaliacao


def _classificar(pct, cortes):
    for label, min_pct, max_pct in cortes:
        if min_pct <= pct <= max_pct:
            return label
    return cortes[-1][0]


def _processar_post_pagina(request, dom):
    """Processa o POST de uma página, salva respostas e retorna (erros, novas, obs)."""
    numeros = [n for n, _ in dom["itens"]]
    valores_validos = {o["valor"] for o in LINGUAGEM_OPCOES}
    erros, novas, obs = [], {}, {}
    for numero in numeros:
        val = request.POST.get(f"item_{numero}")
        if val is None:
            erros.append(numero)
        else:
            try:
                v = int(val)
                if v in valores_validos:
                    novas[numero] = v
                else:
                    erros.append(numero)
            except (ValueError, TypeError):
                erros.append(numero)
        obs[numero] = request.POST.get(f"obs_{numero}", "").strip()
    return erros, novas, obs


def _salvar_respostas(avaliacao, dom_key, novas, obs):
    for numero, valor in novas.items():
        RespostaLinguagem.objects.update_or_create(
            avaliacao=avaliacao, dominio=dom_key, numero_item=numero,
            defaults={"valor": valor, "observacao": obs.get(numero, "")}
        )


# ── Views autenticadas ────────────────────────────────────────────────────────

@login_required
def nova_avaliacao_linguagem(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('linguagem'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo Avaliação de Linguagem.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoLinguagem.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("linguagem_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def linguagem_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoLinguagem, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("linguagem_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("linguagem_form", avaliacao_id=avaliacao_id, pagina=1)

    dom = LINGUAGEM_DOMINIOS[pagina - 1]
    numeros = [n for n, _ in dom["itens"]]
    respostas_qs = list(avaliacao.respostas.filter(dominio=dom["key"], numero_item__in=numeros))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas = {r.numero_item: r.observacao for r in respostas_qs}

    itens_faltando = []
    obs_render = {}

    if request.method == "POST":
        confirmar_incompleto = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_pagina(request, dom)
        obs_render = obs

        if erros and not confirmar_incompleto:
            resp_render = dict(respostas_salvas)
            resp_render.update(novas)
            itens_faltando = erros
            respostas_salvas = resp_render
        else:
            _salvar_respostas(avaliacao, dom["key"], novas, obs)
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, TOTAL_PAGINAS)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular_linguagem(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                return redirect("linguagem_resultado", avaliacao_id=avaliacao_id)
            return redirect("linguagem_form", avaliacao_id=avaliacao_id, pagina=proxima)

    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": respostas_salvas.get(n),
         "observacao_salva": obs_render.get(n, obs_salvas.get(n, ""))}
        for n, t in dom["itens"]
    ]

    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": dom,
        "itens": itens_render,
        "opcoes": LINGUAGEM_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, LINGUAGEM_DOMINIOS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando,
    })


def linguagem_publico(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoLinguagem, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("linguagem_publico", token=token, pagina=1)

    dom = LINGUAGEM_DOMINIOS[pagina - 1]
    numeros = [n for n, _ in dom["itens"]]
    respostas_qs = list(avaliacao.respostas.filter(dominio=dom["key"], numero_item__in=numeros))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas = {r.numero_item: r.observacao for r in respostas_qs}

    itens_faltando = []
    obs_render = {}

    if request.method == "POST":
        confirmar_incompleto = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_pagina(request, dom)
        obs_render = obs

        if erros and not confirmar_incompleto:
            resp_render = dict(respostas_salvas)
            resp_render.update(novas)
            itens_faltando = erros
            respostas_salvas = resp_render
        else:
            _salvar_respostas(avaliacao, dom["key"], novas, obs)
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, TOTAL_PAGINAS)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular_linguagem(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "linguagem", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("linguagem_publico", token=token, pagina=proxima)

    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": respostas_salvas.get(n),
         "observacao_salva": obs_render.get(n, obs_salvas.get(n, ""))}
        for n, t in dom["itens"]
    ]

    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": dom,
        "itens": itens_render,
        "opcoes": LINGUAGEM_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, LINGUAGEM_DOMINIOS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando,
        "publico": True,
        "token": token,
    })


@login_required
def linguagem_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoLinguagem, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("linguagem_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)
    resultado = []
    total_score = 0
    total_max = 0
    for dom in LINGUAGEM_DOMINIOS:
        score = getattr(avaliacao, dom["campo"]) or 0
        max_score = len(dom["itens"]) * 3
        pct = int(score / max_score * 100) if max_score else 0
        total_score += score
        total_max += max_score
        resultado.append({
            "key": dom["key"],
            "nome": dom["nome"],
            "cor": dom["cor"],
            "score": score,
            "max": max_score,
            "pct": pct,
            "classificacao": _classificar(pct, LINGUAGEM_CLASSIFICACAO[dom["key"]]),
        })
    total_pct = int(total_score / total_max * 100) if total_max else 0
    class_total = _classificar(total_pct, LINGUAGEM_CLASSIFICACAO["total"])
    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_linguagem.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    comparativo_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av])
    cores_linha = ["#2E7D6B", "#3E73D1", "#E8793A", "#9B59B6", "#E8B84B", "#C0392B"]
    comparativo_datasets = []
    for i, dom in enumerate(LINGUAGEM_DOMINIOS):
        mx = len(dom["itens"]) * 3
        valores = [round((getattr(av, dom["campo"]) or 0) / mx * 100) if mx else 0 for av in todas_av]
        comparativo_datasets.append({"label": dom["nome"], "data": valores, "borderColor": cores_linha[i % len(cores_linha)], "backgroundColor": cores_linha[i % len(cores_linha)] + "33", "tension": 0.3})

    return render(request, "questionario/avaliacoes/linguagem_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "resultado": resultado,
        "total_score": total_score,
        "total_max": total_max,
        "total_pct": total_pct,
        "class_total": class_total,
        "comparativo_labels": comparativo_labels,
        "comparativo_datasets": json.dumps(comparativo_datasets),
        "tem_comparativo": len(todas_av) > 1,
        "outras_avaliacoes": outras,
    })


@login_required
def linguagem_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoLinguagem, uuid=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("linguagem_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    dom = LINGUAGEM_DOMINIOS[pagina - 1]
    numeros = [n for n, _ in dom["itens"]]
    respostas_qs = list(avaliacao.respostas.filter(dominio=dom["key"], numero_item__in=numeros))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas = {r.numero_item: r.observacao for r in respostas_qs}
    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": respostas_salvas.get(n),
         "observacao_salva": obs_salvas.get(n, "")}
        for n, t in dom["itens"]
    ]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": dom,
        "itens": itens_render,
        "opcoes": LINGUAGEM_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int(pagina / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, LINGUAGEM_DOMINIOS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": [],
        "readonly": True,
    })


@login_required
def linguagem_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoLinguagem, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação de Linguagem excluída com sucesso."})
        messages.success(request, "Avaliação de Linguagem excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_linguagem(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoLinguagem, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("linguagem_resultado", avaliacao_id=avaliacao_id)
