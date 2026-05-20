import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Paciente, AvaliacaoSono, RespostaSono
from ..data.data_sono import SONO_DOMINIOS, SONO_OPCOES
from ..services import notificar_terapeuta

# RespostaSono NÃO tem campo dominio — itens são salvos com numero_item global.
# Numeração global: (index_dominio * 100) + numero_local
# Ex.: domínio 0, item 1 → 1; domínio 1, item 1 → 101; domínio 2, item 3 → 203

TOTAL_PAGINAS = len(SONO_DOMINIOS)

_URL_NAMES = {
    "url_form_name": "sono_form",
    "url_publico_name": "sono_publico",
    "url_visualizar_name": "sono_visualizar",
    "url_resultado_name": "sono_resultado",
    "avaliacao_titulo": "Avaliação de Sono",
}


def _numero_global_sono(idx_dom, numero_local):
    return (idx_dom * 100) + numero_local


def _calcular_sono(avaliacao):
    for idx, dom in enumerate(SONO_DOMINIOS):
        numeros_globais = [_numero_global_sono(idx, n) for n, _ in dom["itens"]]
        respostas = avaliacao.respostas.filter(numero_item__in=numeros_globais)
        total = sum(r.valor for r in respostas)
        setattr(avaliacao, dom["campo"], total)
    return avaliacao


# ── Views autenticadas ────────────────────────────────────────────────────────

@login_required
def nova_avaliacao_sono(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('sono_infantil'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo Avaliação de Sono Infantil.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoSono.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "id": av.id})
    return redirect("sono_form", avaliacao_id=av.id, pagina=1)


@login_required
def sono_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoSono, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("sono_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("sono_form", avaliacao_id=avaliacao_id, pagina=1)

    idx = pagina - 1
    dom = SONO_DOMINIOS[idx]
    numeros_globais = [_numero_global_sono(idx, n) for n, _ in dom["itens"]]
    respostas_qs = list(avaliacao.respostas.filter(numero_item__in=numeros_globais))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas_globais = {r.numero_item: r.observacao for r in respostas_qs}
    respostas_locais = {n: respostas_salvas.get(_numero_global_sono(idx, n)) for n, _ in dom["itens"]}
    obs_locais = {n: obs_salvas_globais.get(_numero_global_sono(idx, n), "") for n, _ in dom["itens"]}

    itens_faltando = []
    obs_render = {}

    if request.method == "POST":
        confirmar_incompleto = request.POST.get("confirmar_incompleto") == "1"
        valores_validos = {o["valor"] for o in SONO_OPCOES}
        erros, novas, obs = [], {}, {}
        for numero, _ in dom["itens"]:
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
        obs_render = obs

        if erros and not confirmar_incompleto:
            resp_render = dict(respostas_locais)
            resp_render.update(novas)
            itens_faltando = erros
            respostas_locais = resp_render
        else:
            for numero, valor in novas.items():
                RespostaSono.objects.update_or_create(
                    avaliacao=avaliacao,
                    numero_item=_numero_global_sono(idx, numero),
                    defaults={"valor": valor, "observacao": obs.get(numero, "")}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, TOTAL_PAGINAS)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular_sono(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                return redirect("sono_resultado", avaliacao_id=avaliacao_id)
            return redirect("sono_form", avaliacao_id=avaliacao_id, pagina=proxima)

    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": respostas_locais.get(n),
         "observacao_salva": obs_render.get(n, obs_locais.get(n, ""))}
        for n, t in dom["itens"]
    ]

    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": dom,
        "itens": itens_render,
        "opcoes": SONO_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, SONO_DOMINIOS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando,
    })


def sono_publico(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoSono, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("sono_publico", token=token, pagina=1)

    idx = pagina - 1
    dom = SONO_DOMINIOS[idx]
    numeros_globais = [_numero_global_sono(idx, n) for n, _ in dom["itens"]]
    respostas_qs = list(avaliacao.respostas.filter(numero_item__in=numeros_globais))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas_globais = {r.numero_item: r.observacao for r in respostas_qs}
    respostas_locais = {n: respostas_salvas.get(_numero_global_sono(idx, n)) for n, _ in dom["itens"]}
    obs_locais = {n: obs_salvas_globais.get(_numero_global_sono(idx, n), "") for n, _ in dom["itens"]}

    itens_faltando = []
    obs_render = {}

    if request.method == "POST":
        confirmar_incompleto = request.POST.get("confirmar_incompleto") == "1"
        valores_validos = {o["valor"] for o in SONO_OPCOES}
        erros, novas, obs = [], {}, {}
        for numero, _ in dom["itens"]:
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
        obs_render = obs

        if erros and not confirmar_incompleto:
            resp_render = dict(respostas_locais)
            resp_render.update(novas)
            itens_faltando = erros
            respostas_locais = resp_render
        else:
            for numero, valor in novas.items():
                RespostaSono.objects.update_or_create(
                    avaliacao=avaliacao,
                    numero_item=_numero_global_sono(idx, numero),
                    defaults={"valor": valor, "observacao": obs.get(numero, "")}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, TOTAL_PAGINAS)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular_sono(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "sono", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("sono_publico", token=token, pagina=proxima)

    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": respostas_locais.get(n),
         "observacao_salva": obs_render.get(n, obs_locais.get(n, ""))}
        for n, t in dom["itens"]
    ]

    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": dom,
        "itens": itens_render,
        "opcoes": SONO_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, SONO_DOMINIOS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando,
        "publico": True,
        "token": token,
    })


@login_required
def sono_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSono, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("sono_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)
    resultado = []
    max_por_item = max(o["valor"] for o in SONO_OPCOES)
    for dom in SONO_DOMINIOS:
        score = getattr(avaliacao, dom["campo"]) or 0
        max_score = len(dom["itens"]) * max_por_item
        resultado.append({
            "key": dom["key"],
            "nome": dom["nome"],
            "cor": dom["cor"],
            "score": score,
            "max": max_score,
            "pct": int(score / max_score * 100) if max_score else 0,
        })
    return render(request, "questionario/avaliacoes/sono_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "resultado": resultado,
    })


@login_required
def sono_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoSono, id=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("sono_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    idx = pagina - 1
    dom = SONO_DOMINIOS[idx]
    numeros_globais = [_numero_global_sono(idx, n) for n, _ in dom["itens"]]
    respostas_qs = list(avaliacao.respostas.filter(numero_item__in=numeros_globais))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas_globais = {r.numero_item: r.observacao for r in respostas_qs}
    respostas_locais = {n: respostas_salvas.get(_numero_global_sono(idx, n)) for n, _ in dom["itens"]}
    obs_locais = {n: obs_salvas_globais.get(_numero_global_sono(idx, n), "") for n, _ in dom["itens"]}
    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": respostas_locais.get(n),
         "observacao_salva": obs_locais.get(n, "")}
        for n, t in dom["itens"]
    ]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": dom,
        "itens": itens_render,
        "opcoes": SONO_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int(pagina / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, SONO_DOMINIOS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": [],
        "readonly": True,
    })


@login_required
def sono_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSono, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação de Sono excluída com sucesso."})
        messages.success(request, "Avaliação de Sono excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_sono(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSono, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("sono_resultado", avaliacao_id=avaliacao_id)
