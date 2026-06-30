import json
from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import (
    Paciente, AvaliacaoVBMAPP, RespostaVBMAPP,
    AvaliacaoVBMAPPBarreiras, AvaliacaoVBMAPPTransicao, AvaliacaoVBMAPPTaskAnalysis,
)
from ..data.vbmapp_data import (
    VBMAPP_DOMINIOS, VBMAPP_ITENS, VBMAPP_OPCOES, itens_do_dominio,
    VBMAPP_BARREIRAS_CAMPOS, VBMAPP_BARREIRAS_ESCALA,
    VBMAPP_TRANSICAO_CAMPOS, VBMAPP_TRANSICAO_ESCALA,
)

TOTAL_PAGINAS = len(VBMAPP_DOMINIOS)
VALORES_VALIDOS = {"0", "0.5", "1"}


def _calcular_pontuacao(avaliacao):
    for dom in VBMAPP_DOMINIOS:
        key = dom["key"]
        campo = f"pont_{key}"
        total = avaliacao.respostas.filter(dominio=key).aggregate(total=Sum("valor"))["total"]
        setattr(avaliacao, campo, total)
    return avaliacao


def _itens_para_render(dom, respostas_salvas):
    """Lista de itens do domínio agrupados por nível, com texto e resposta salva."""
    grupos = []
    for nivel in dom["niveis"]:
        numeros = itens_do_dominio(dom["key"], nivel)
        itens = [
            {
                "numero": n,
                "texto": VBMAPP_ITENS.get(dom["key"], {}).get(n, ""),
                "resposta_salva": respostas_salvas.get(n),
            }
            for n in numeros
        ]
        grupos.append({"nivel": nivel, "itens": itens})
    return grupos


def _dominios_progresso(pagina_atual):
    return [
        {"nome": dom["nome"], "status": "done" if (i + 1) < pagina_atual else ("active" if (i + 1) == pagina_atual else ""), "pagina": i + 1}
        for i, dom in enumerate(VBMAPP_DOMINIOS)
    ]


# ── Views autenticadas (presencial — sem link público) ────────────────────────

@login_required
def nova_avaliacao_vbmapp(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, "perfil") or not request.user.perfil.tem_acesso("vbmapp"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo VB-MAPP.")
        return redirect("detalhe_paciente", paciente_id=paciente_id)
    av = AvaliacaoVBMAPP.objects.create(paciente=paciente)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        from django.urls import reverse
        return JsonResponse({"ok": True, "uuid": str(av.uuid), "redirect": reverse("vbmapp_form", kwargs={"avaliacao_id": av.uuid, "pagina": 1})})
    return redirect("vbmapp_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def vbmapp_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoVBMAPP, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("vbmapp_resultado", avaliacao_id=avaliacao_id)

    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("vbmapp_form", avaliacao_id=avaliacao_id, pagina=1)

    dom = VBMAPP_DOMINIOS[pagina - 1]
    todos_itens = [n for nivel in dom["niveis"] for n in itens_do_dominio(dom["key"], nivel)]

    respostas_qs = avaliacao.respostas.filter(dominio=dom["key"], numero_item__in=todos_itens)
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}

    itens_faltando = []
    respostas_para_render = respostas_salvas

    if request.method == "POST":
        novas = {}
        erros = []
        for n in todos_itens:
            val = request.POST.get(f"item_{n}")
            if val not in VALORES_VALIDOS:
                erros.append(n)
            else:
                novas[n] = Decimal(val)

        if erros:
            respostas_para_render = {**respostas_salvas, **novas}
            itens_faltando = erros
        else:
            for n, v in novas.items():
                RespostaVBMAPP.objects.update_or_create(
                    avaliacao=avaliacao, dominio=dom["key"], numero_item=n,
                    defaults={"valor": v},
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, TOTAL_PAGINAS)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > TOTAL_PAGINAS:
                return redirect("vbmapp_concluir", avaliacao_id=avaliacao_id)
            return redirect("vbmapp_form", avaliacao_id=avaliacao_id, pagina=proxima)

    return render(request, "questionario/avaliacoes/vbmapp_form.html", {
        "avaliacao": avaliacao,
        "dominio": dom,
        "grupos": _itens_para_render(dom, respostas_para_render),
        "todos_itens": todos_itens,
        "opcoes": VBMAPP_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": _dominios_progresso(pagina),
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando,
    })


@login_required
def vbmapp_concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVBMAPP, uuid=avaliacao_id, paciente__medico=request.user)
    avaliacao = _calcular_pontuacao(avaliacao)
    avaliacao.status = "concluida"
    avaliacao.save()
    return redirect("vbmapp_resultado", avaliacao_id=avaliacao_id)


@login_required
def vbmapp_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVBMAPP, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("vbmapp_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    if avaliacao.pont_mando is None:
        avaliacao = _calcular_pontuacao(avaliacao)
        avaliacao.save()

    if request.method == "POST" and "observacoes" in request.POST:
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
        return redirect("vbmapp_resultado", avaliacao_id=avaliacao_id)

    dominios_resultado = []
    for dom in VBMAPP_DOMINIOS:
        maximo = len(dom["niveis"]) * 5
        valor = getattr(avaliacao, f"pont_{dom['key']}") or 0
        pct = round(float(valor) / maximo * 100) if maximo else 0
        dominios_resultado.append({
            "key": dom["key"], "nome": dom["nome"], "cor": dom["cor"],
            "niveis": dom["niveis"], "valor": valor, "maximo": maximo, "pct": pct,
        })
    # Dataset à parte para o JS do gráfico: Decimal localizado (vírgula em pt-BR)
    # quebraria os literais numéricos se interpolado direto no template, então
    # serializa como JSON (float) aqui.
    dominios_chart_json = json.dumps([
        {"nome": d["nome"], "pct": d["pct"], "cor": d["cor"], "valor": float(d["valor"]), "maximo": d["maximo"]}
        for d in dominios_resultado
    ])

    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_vbmapp.filter(status="concluida").order_by("data"))
    comparativo_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av])
    cores_linha = ["#2E7D6B", "#3E73D1", "#E8793A", "#9B59B6", "#E8B84B", "#C0392B"]
    comparativo_datasets = []
    for i, dom in enumerate(VBMAPP_DOMINIOS):
        maximo = len(dom["niveis"]) * 5
        valores = [
            round(float(getattr(av, f"pont_{dom['key']}") or 0) / maximo * 100) if maximo else 0
            for av in todas_av
        ]
        comparativo_datasets.append({
            "label": dom["nome"], "data": valores,
            "borderColor": cores_linha[i % len(cores_linha)],
            "backgroundColor": cores_linha[i % len(cores_linha)] + "33",
            "tension": 0.3,
        })

    outras = [av for av in todas_av if av.id != avaliacao.id]

    return render(request, "questionario/avaliacoes/vbmapp_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "dominios": dominios_resultado,
        "dominios_chart_json": dominios_chart_json,
        "comparativo_labels": comparativo_labels,
        "comparativo_datasets": json.dumps(comparativo_datasets),
        "tem_comparativo": len(todas_av) > 1,
        "outras_avaliacoes": outras,
    })


@login_required
def vbmapp_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoVBMAPP, uuid=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("vbmapp_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    dom = VBMAPP_DOMINIOS[pagina - 1]
    todos_itens = [n for nivel in dom["niveis"] for n in itens_do_dominio(dom["key"], nivel)]
    respostas_salvas = {
        r.numero_item: r.valor
        for r in avaliacao.respostas.filter(dominio=dom["key"], numero_item__in=todos_itens)
    }

    return render(request, "questionario/avaliacoes/vbmapp_form.html", {
        "avaliacao": avaliacao,
        "dominio": dom,
        "grupos": _itens_para_render(dom, respostas_salvas),
        "todos_itens": todos_itens,
        "opcoes": VBMAPP_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": _dominios_progresso(pagina),
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": [],
        "readonly": True,
    })


@login_required
def vbmapp_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVBMAPP, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação VB-MAPP excluída com sucesso."})
        messages.success(request, "Avaliação VB-MAPP excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


# ── Avaliação de Barreiras Linguísticas e Transition Assessment ───────────────
# Formulário de página única com N campos fixos pontuados numa escala fechada
# (1-4 para Barreiras, 1-5 para Transition) — sem tabela de respostas item-a-item.

def _nova_simples(request, paciente_id, Model, modulo, titulo, url_form):
    from django.urls import reverse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, "perfil") or not request.user.perfil.tem_acesso(modulo):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, f"Você não tem acesso ao módulo {titulo}.")
        return redirect("detalhe_paciente", paciente_id=paciente_id)
    avaliacao = Model.objects.create(paciente=paciente)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(avaliacao.uuid), "redirect": reverse(url_form, kwargs={"avaliacao_id": avaliacao.uuid})})
    return redirect(url_form, avaliacao_id=avaliacao.uuid)


def _form_simples(request, avaliacao_id, Model, campos, escala, titulo, url_resultado):
    avaliacao = get_object_or_404(Model, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if request.method == "POST":
        valores = {}
        erros = []
        for nome, _label in campos:
            val = request.POST.get(nome)
            try:
                v = int(val)
                if v in escala:
                    valores[nome] = v
                else:
                    erros.append(nome)
            except (TypeError, ValueError):
                erros.append(nome)

        if not erros:
            for nome, v in valores.items():
                setattr(avaliacao, nome, v)
            avaliacao.status = "concluida"
            avaliacao.observacoes = request.POST.get("observacoes", "").strip()
            avaliacao.save()
            messages.success(request, f"{titulo} salva com sucesso.")
            return redirect(url_resultado, avaliacao_id=avaliacao.uuid)
        messages.error(request, "Preencha todas as áreas antes de salvar.")

    campos_render = [
        {"nome": nome, "label": label, "valor": getattr(avaliacao, nome)}
        for nome, label in campos
    ]
    return render(request, "questionario/avaliacoes/vbmapp_simples_form.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "titulo": titulo,
        "campos": campos_render,
        "escala": escala,
    })


@login_required
def nova_avaliacao_vbmapp_barreiras(request, paciente_id):
    return _nova_simples(request, paciente_id, AvaliacaoVBMAPPBarreiras, "vbmapp",
                          "Avaliação de Barreiras Linguísticas", "vbmapp_barreiras_form")


@login_required
def vbmapp_barreiras_form(request, avaliacao_id):
    return _form_simples(
        request, avaliacao_id, AvaliacaoVBMAPPBarreiras,
        VBMAPP_BARREIRAS_CAMPOS, VBMAPP_BARREIRAS_ESCALA,
        "Avaliação de Barreiras Linguísticas", "vbmapp_barreiras_resultado",
    )


CORES_CICLO = ["#7C3AED", "#2E7D6B", "#3E73D1", "#E8793A", "#9B59B6", "#E8B84B", "#C0392B", "#16A085"]


def _campos_chart_json(campos, escala_max):
    return json.dumps([
        {"nome": c["label"], "valor": c["valor"] or 0, "pct": round((c["valor"] or 0) / escala_max * 100),
         "cor": CORES_CICLO[i % len(CORES_CICLO)]}
        for i, c in enumerate(campos)
    ])


@login_required
def vbmapp_barreiras_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVBMAPPBarreiras, uuid=avaliacao_id, paciente__medico=request.user)
    campos_render = [
        {"nome": nome, "label": label, "valor": getattr(avaliacao, nome)}
        for nome, label in VBMAPP_BARREIRAS_CAMPOS
    ]
    escala_max = max(VBMAPP_BARREIRAS_ESCALA)
    outras = list(avaliacao.paciente.avaliacoes_vbmapp_barreiras.filter(status="concluida").exclude(id=avaliacao.id).order_by("-data"))
    return render(request, "questionario/avaliacoes/vbmapp_simples_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "titulo": "Avaliação de Barreiras Linguísticas",
        "campos": campos_render,
        "campos_chart_json": _campos_chart_json(campos_render, escala_max),
        "escala_max": escala_max,
        "url_deletar": "vbmapp_barreiras_deletar",
        "url_resultado": "vbmapp_barreiras_resultado",
        "outras_avaliacoes": outras,
    })


@login_required
def vbmapp_barreiras_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVBMAPPBarreiras, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação de Barreiras excluída com sucesso."})
        messages.success(request, "Avaliação de Barreiras excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def nova_avaliacao_vbmapp_transicao(request, paciente_id):
    return _nova_simples(request, paciente_id, AvaliacaoVBMAPPTransicao, "vbmapp",
                          "Transition Assessment", "vbmapp_transicao_form")


@login_required
def vbmapp_transicao_form(request, avaliacao_id):
    return _form_simples(
        request, avaliacao_id, AvaliacaoVBMAPPTransicao,
        VBMAPP_TRANSICAO_CAMPOS, VBMAPP_TRANSICAO_ESCALA,
        "Transition Assessment", "vbmapp_transicao_resultado",
    )


@login_required
def vbmapp_transicao_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVBMAPPTransicao, uuid=avaliacao_id, paciente__medico=request.user)
    campos_render = [
        {"nome": nome, "label": label, "valor": getattr(avaliacao, nome)}
        for nome, label in VBMAPP_TRANSICAO_CAMPOS
    ]
    escala_max = max(VBMAPP_TRANSICAO_ESCALA)
    outras = list(avaliacao.paciente.avaliacoes_vbmapp_transicao.filter(status="concluida").exclude(id=avaliacao.id).order_by("-data"))
    return render(request, "questionario/avaliacoes/vbmapp_simples_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "titulo": "Transition Assessment",
        "campos": campos_render,
        "campos_chart_json": _campos_chart_json(campos_render, escala_max),
        "escala_max": escala_max,
        "url_deletar": "vbmapp_transicao_deletar",
        "url_resultado": "vbmapp_transicao_resultado",
        "outras_avaliacoes": outras,
    })


@login_required
def vbmapp_transicao_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVBMAPPTransicao, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Transition Assessment excluído com sucesso."})
        messages.success(request, "Transition Assessment excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


# ── Task Analysis Skills Tracking ──────────────────────────────────────────────
# Checklist binário de domínio mastery, um registro por nível (1/2/3). Reaproveita
# os mesmos domínios/itens/textos da Avaliação de Marcos (os PDFs enviados só
# trazem códigos crípticos para as sub-habilidades do Task Analysis "oficial",
# sem texto descritivo confiável para transcrever) — aqui cada item é uma
# checkbox "dominado / ainda não" em vez de pontuado 0/½/1.

def _dominios_do_nivel(nivel):
    return [d for d in VBMAPP_DOMINIOS if nivel in d["niveis"]]


@login_required
def nova_avaliacao_vbmapp_task_analysis(request, paciente_id, nivel):
    from django.urls import reverse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, "perfil") or not request.user.perfil.tem_acesso("vbmapp"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo VB-MAPP.")
        return redirect("detalhe_paciente", paciente_id=paciente_id)
    avaliacao = AvaliacaoVBMAPPTaskAnalysis.objects.create(paciente=paciente, nivel=nivel)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(avaliacao.uuid), "redirect": reverse("vbmapp_task_analysis_form", kwargs={"avaliacao_id": avaliacao.uuid})})
    return redirect("vbmapp_task_analysis_form", avaliacao_id=avaliacao.uuid)


@login_required
def vbmapp_task_analysis_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVBMAPPTaskAnalysis, uuid=avaliacao_id, paciente__medico=request.user)
    dominios = _dominios_do_nivel(avaliacao.nivel)

    if request.method == "POST":
        conteudo = {}
        for dom in dominios:
            marcados = request.POST.getlist(f"dom_{dom['key']}")
            conteudo[dom["key"]] = [int(n) for n in marcados]
        avaliacao.conteudo = conteudo
        avaliacao.status = "concluida"
        avaliacao.save()
        messages.success(request, "Task Analysis salva com sucesso.")
        return redirect("vbmapp_task_analysis_resultado", avaliacao_id=avaliacao.uuid)

    grupos = []
    for dom in dominios:
        numeros = itens_do_dominio(dom["key"], avaliacao.nivel)
        marcados = set(avaliacao.conteudo.get(dom["key"], []))
        grupos.append({
            "dominio": dom,
            "itens": [
                {"numero": n, "texto": VBMAPP_ITENS.get(dom["key"], {}).get(n, ""), "marcado": n in marcados}
                for n in numeros
            ],
        })

    return render(request, "questionario/avaliacoes/vbmapp_task_analysis_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "grupos": grupos,
    })


@login_required
def vbmapp_task_analysis_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVBMAPPTaskAnalysis, uuid=avaliacao_id, paciente__medico=request.user)
    dominios = _dominios_do_nivel(avaliacao.nivel)
    grupos = []
    for dom in dominios:
        numeros = itens_do_dominio(dom["key"], avaliacao.nivel)
        marcados = set(avaliacao.conteudo.get(dom["key"], []))
        grupos.append({
            "dominio": dom,
            "total": len(numeros),
            "dominados": len(marcados),
            "pct": round(len(marcados) / len(numeros) * 100) if numeros else 0,
            "itens": [
                {"numero": n, "texto": VBMAPP_ITENS.get(dom["key"], {}).get(n, ""), "marcado": n in marcados}
                for n in numeros
            ],
        })
    grupos_chart_json = json.dumps([
        {"nome": g["dominio"]["nome"], "pct": g["pct"], "cor": g["dominio"]["cor"],
         "dominados": g["dominados"], "total": g["total"]}
        for g in grupos
    ])
    outras = list(
        avaliacao.paciente.avaliacoes_vbmapp_task_analysis
        .filter(status="concluida", nivel=avaliacao.nivel).exclude(id=avaliacao.id).order_by("-data")
    )
    return render(request, "questionario/avaliacoes/vbmapp_task_analysis_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "grupos": grupos,
        "grupos_chart_json": grupos_chart_json,
        "outras_avaliacoes": outras,
    })


@login_required
def vbmapp_task_analysis_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVBMAPPTaskAnalysis, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Task Analysis excluída com sucesso."})
        messages.success(request, "Task Analysis excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)
