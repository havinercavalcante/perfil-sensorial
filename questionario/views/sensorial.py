import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Paciente, Avaliacao, Resposta
from ..data import (SECOES, PERGUNTAS, OPCOES, QUADRANTE, QUADRANTES_CONFIG, SECOES_CONFIG,
                    calcular_pontuacao, classificar)
from ..services import notificar_terapeuta, classe_css

TOTAL_PAGINAS = len(SECOES)


def questionario_publico_view(request, token, pagina):
    from django.http import Http404
    avaliacao = get_object_or_404(Avaliacao, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        pagina = 1
    secao_atual = SECOES[pagina - 1]
    itens_secao = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens_secao)}

    from ..data import PERGUNTAS, OPCOES, QUADRANTE, calcular_pontuacao

    def _build_perguntas(itens, respostas):
        return [
            {"numero": item, "texto": PERGUNTAS.get(item, ""),
             "resposta_salva": respostas.get(item), "quadrante": QUADRANTE.get(item)}
            for item in itens
        ]

    perguntas_pagina = _build_perguntas(itens_secao, respostas_salvas)

    if request.method == "POST":
        erros = []
        respostas_novas = {}
        for item in itens_secao:
            val = request.POST.get(f"item_{item}")
            if val is None:
                erros.append(item)
            else:
                try:
                    v = int(val)
                    if 0 <= v <= 5:
                        respostas_novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)

        if erros:
            messages.error(request, "Por favor, responda todas as perguntas antes de continuar.")
        else:
            for item, valor in respostas_novas.items():
                Resposta.objects.update_or_create(avaliacao=avaliacao, numero_item=item, defaults={"valor": valor})
            if pagina < TOTAL_PAGINAS:
                proxima = pagina + 1
                avaliacao.pagina_atual = proxima
                avaliacao.save(update_fields=["pagina_atual"])
                return redirect("questionario_publico", token=token, pagina=proxima)
            else:
                respostas_finais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
                p = calcular_pontuacao(respostas_finais)
                avaliacao.pont_auditiva = p.get("auditiva", 0)
                avaliacao.pont_visual = p.get("visual", 0)
                avaliacao.pont_tato = p.get("tato", 0)
                avaliacao.pont_movimento = p.get("movimento", 0)
                avaliacao.pont_posicao = p.get("posicao", 0)
                avaliacao.pont_oral = p.get("oral", 0)
                avaliacao.pont_conduta = p.get("conduta", 0)
                avaliacao.pont_socioemocional = p.get("socioemocional", 0)
                avaliacao.pont_atencao = p.get("atencao", 0)
                avaliacao.pont_ex = p.get("EX", 0)
                avaliacao.pont_ev = p.get("EV", 0)
                avaliacao.pont_sn = p.get("SN", 0)
                avaliacao.pont_ob = p.get("OB", 0)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "sensorial", request)
                except Exception:
                    pass
                return render(request, "questionario/concluido.html")
        respostas_salvas.update(respostas_novas)
        perguntas_pagina = _build_perguntas(itens_secao, respostas_salvas)

    return render(request, "questionario/questionario.html", {
        "avaliacao": avaliacao,
        "secao": secao_atual,
        "perguntas": perguntas_pagina,
        "opcoes": OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_secoes": [(i + 1, SECOES[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
    })


@login_required
def questionario_view(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("dashboard", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("questionario", avaliacao_id=avaliacao_id, pagina=1)

    secao_atual = SECOES[pagina - 1]
    itens_secao = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens_secao)}

    if request.method == "POST":
        erros = []
        respostas_novas = {}
        for item in itens_secao:
            val = request.POST.get(f"item_{item}")
            if val is None:
                erros.append(item)
            else:
                try:
                    v = int(val)
                    if 0 <= v <= 5:
                        respostas_novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)

        if erros:
            messages.error(request, "Por favor, responda todas as perguntas antes de continuar.")
        else:
            for item, valor in respostas_novas.items():
                Resposta.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={"valor": valor})
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, TOTAL_PAGINAS)
            avaliacao.save()
            if proxima > TOTAL_PAGINAS:
                return redirect("concluir", avaliacao_id=avaliacao_id)
            return redirect("questionario", avaliacao_id=avaliacao_id, pagina=proxima)
        respostas_salvas.update(respostas_novas)

    perguntas_pagina = [
        {"numero": item, "texto": PERGUNTAS.get(item, ""), "resposta_salva": respostas_salvas.get(item),
         "quadrante": QUADRANTE.get(item)}
        for item in itens_secao
    ]
    return render(request, "questionario/questionario.html", {
        "avaliacao": avaliacao, "secao": secao_atual, "perguntas": perguntas_pagina,
        "opcoes": OPCOES, "pagina": pagina, "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_secoes": [(i + 1, SECOES[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    })


@login_required
def concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    respostas_qs = avaliacao.respostas.all()
    if respostas_qs.count() < 86:
        messages.warning(request, "Ainda há perguntas sem resposta.")
        return redirect("questionario", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    respostas = {r.numero_item: r.valor for r in respostas_qs}
    p = calcular_pontuacao(respostas)
    avaliacao.pont_auditiva = p.get("auditiva", 0)
    avaliacao.pont_visual = p.get("visual", 0)
    avaliacao.pont_tato = p.get("tato", 0)
    avaliacao.pont_movimento = p.get("movimento", 0)
    avaliacao.pont_posicao = p.get("posicao", 0)
    avaliacao.pont_oral = p.get("oral", 0)
    avaliacao.pont_conduta = p.get("conduta", 0)
    avaliacao.pont_socioemocional = p.get("socioemocional", 0)
    avaliacao.pont_atencao = p.get("atencao", 0)
    avaliacao.pont_ex = p.get("EX", 0)
    avaliacao.pont_ev = p.get("EV", 0)
    avaliacao.pont_sn = p.get("SN", 0)
    avaliacao.pont_ob = p.get("OB", 0)
    avaliacao.status = "concluida"
    avaliacao.save()
    return redirect("dashboard", avaliacao_id=avaliacao_id)


@login_required
def salvar_observacoes(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("dashboard", avaliacao_id=avaliacao_id)
    return redirect("dashboard", avaliacao_id=avaliacao_id)


@login_required
def dashboard(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    if avaliacao.status != "concluida":
        return redirect("questionario", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    secao_map = {
        "auditiva": avaliacao.pont_auditiva, "visual": avaliacao.pont_visual,
        "tato": avaliacao.pont_tato, "movimento": avaliacao.pont_movimento,
        "posicao": avaliacao.pont_posicao, "oral": avaliacao.pont_oral,
        "conduta": avaliacao.pont_conduta, "socioemocional": avaliacao.pont_socioemocional,
        "atencao": avaliacao.pont_atencao,
    }
    secoes_dados = []
    for sid, config in SECOES_CONFIG.items():
        valor = secao_map.get(sid, 0) or 0
        maximo = config["max"]
        classificacao = classificar(valor, config["faixas"])
        secoes_dados.append({
            "id": sid, "nome": config["nome"], "valor": valor, "maximo": maximo,
            "pct": int(valor / maximo * 100) if maximo else 0,
            "classificacao": classificacao, "classe_css": classe_css(classificacao),
        })

    quad_map = {"EX": avaliacao.pont_ex or 0, "EV": avaliacao.pont_ev or 0,
                "SN": avaliacao.pont_sn or 0, "OB": avaliacao.pont_ob or 0}
    quadrantes_dados = []
    for qid, config in QUADRANTES_CONFIG.items():
        valor = quad_map.get(qid, 0)
        maximo = config["max"]
        classificacao = classificar(valor, config["faixas"])
        quadrantes_dados.append({
            "id": qid, "nome": config["nome"], "subtitulo": config["subtitulo"],
            "valor": valor, "maximo": maximo,
            "pct": int(valor / maximo * 100) if maximo else 0,
            "classificacao": classificacao, "cor": config["cor"],
            "classe_css": classe_css(classificacao),
        })

    todas_avaliacoes = list(paciente.avaliacoes.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_avaliacoes if av.id != avaliacao_id]

    comparativo_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_avaliacoes])
    dominios_comparativo = [
        {"key": "auditiva", "nome": "Auditiva", "campo": "pont_auditiva", "max": SECOES_CONFIG["auditiva"]["max"]},
        {"key": "visual", "nome": "Visual", "campo": "pont_visual", "max": SECOES_CONFIG["visual"]["max"]},
        {"key": "tato", "nome": "Tato", "campo": "pont_tato", "max": SECOES_CONFIG["tato"]["max"]},
        {"key": "movimento", "nome": "Movimento", "campo": "pont_movimento", "max": SECOES_CONFIG["movimento"]["max"]},
        {"key": "posicao", "nome": "Posição", "campo": "pont_posicao", "max": SECOES_CONFIG["posicao"]["max"]},
        {"key": "oral", "nome": "Oral", "campo": "pont_oral", "max": SECOES_CONFIG["oral"]["max"]},
        {"key": "conduta", "nome": "Conduta", "campo": "pont_conduta", "max": SECOES_CONFIG["conduta"]["max"]},
        {"key": "socioemocional", "nome": "Socioemocional", "campo": "pont_socioemocional", "max": SECOES_CONFIG["socioemocional"]["max"]},
        {"key": "atencao", "nome": "Atenção", "campo": "pont_atencao", "max": SECOES_CONFIG["atencao"]["max"]},
    ]
    cores_linha = ["#2E7D6B","#3E73D1","#E8793A","#9B59B6","#E8B84B","#C0392B","#16A085","#1ABC9C","#7DB87D"]
    comparativo_datasets = []
    for i, dom in enumerate(dominios_comparativo):
        valores = [round(getattr(av, dom["campo"]) / dom["max"] * 100) if getattr(av, dom["campo"]) is not None else 0 for av in todas_avaliacoes]
        comparativo_datasets.append({"label": dom["nome"], "data": valores, "borderColor": cores_linha[i], "backgroundColor": cores_linha[i] + "33", "tension": 0.3})

    return render(request, "questionario/dashboard.html", {
        "avaliacao": avaliacao, "paciente": paciente,
        "secoes": secoes_dados, "quadrantes": quadrantes_dados, "outras_avaliacoes": outras,
        "radar_labels": json.dumps([s["nome"] for s in secoes_dados]),
        "radar_valores": json.dumps([s["pct"] for s in secoes_dados]),
        "quad_labels": json.dumps([q["nome"] for q in quadrantes_dados]),
        "quad_valores": json.dumps([q["pct"] for q in quadrantes_dados]),
        "quad_cores": json.dumps([q["cor"] for q in quadrantes_dados]),
        "comparativo_labels": comparativo_labels,
        "comparativo_datasets": json.dumps(comparativo_datasets),
        "tem_comparativo": len(todas_avaliacoes) > 1,
    })


@login_required
def questionario_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("questionario_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    secao_atual = SECOES[pagina - 1]
    itens_secao = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens_secao)}

    perguntas_pagina = [
        {"numero": item, "texto": PERGUNTAS.get(item, ""), "resposta_salva": respostas_salvas.get(item),
         "quadrante": QUADRANTE.get(item)}
        for item in itens_secao
    ]
    return render(request, "questionario/questionario.html", {
        "avaliacao": avaliacao, "secao": secao_atual, "perguntas": perguntas_pagina,
        "opcoes": OPCOES, "pagina": pagina, "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_secoes": [(i + 1, SECOES[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "readonly": True,
    })


@login_required
def enviar_email_link(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            from django.http import JsonResponse
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    link = request.build_absolute_uri(f"/questionario/publico/{avaliacao.token}/1/")
    html = render_to_string("questionario/email_link_avaliacao.html", {
        "paciente": paciente, "link": link,
    })
    send_mail(
        subject="Questionário CeciSys",
        message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário no link: {link}",
        from_email=None,
        recipient_list=[email_dest],
        html_message=html,
        fail_silently=False,
    )
    avaliacao.email_enviado_em = tz.now()
    avaliacao.save(update_fields=["email_enviado_em"])
    if is_ajax:
        from django.http import JsonResponse
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)
