from django.conf import settings
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Paciente, Avaliacao, Resposta
from ..data.data import (SECOES, PERGUNTAS, OPCOES, QUADRANTE, QUADRANTES_CONFIG, SECOES_CONFIG,
                    calcular_pontuacao, classificar)
from ..services import notificar_terapeuta, classe_css
from ..tasks import enviar_email
from django.templatetags.static import static

TOTAL_PAGINAS = len(SECOES)


def questionario_publico_view(request, token, pagina):
    from django.http import Http404
    avaliacao = get_object_or_404(Avaliacao, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        pagina = 1
    secao_atual = SECOES[pagina - 1]
    itens_secao = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens_secao)}

    from ..data.data import PERGUNTAS, OPCOES, QUADRANTE, calcular_pontuacao

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
                return render(request, "questionario/dashboard/concluido.html")
        respostas_salvas.update(respostas_novas)
        perguntas_pagina = _build_perguntas(itens_secao, respostas_salvas)

    return render(request, "questionario/dashboard/questionario.html", {
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
    avaliacao = get_object_or_404(Avaliacao, uuid=avaliacao_id, paciente__medico=request.user)
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
    return render(request, "questionario/dashboard/questionario.html", {
        "avaliacao": avaliacao, "secao": secao_atual, "perguntas": perguntas_pagina,
        "opcoes": OPCOES, "pagina": pagina, "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_secoes": [(i + 1, SECOES[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    })


@login_required
def concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, uuid=avaliacao_id, paciente__medico=request.user)
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
    avaliacao = get_object_or_404(Avaliacao, uuid=avaliacao_id, paciente__medico=request.user)
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
    avaliacao = get_object_or_404(Avaliacao, uuid=avaliacao_id, paciente__medico=request.user)
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

    return render(request, "questionario/dashboard/dashboard.html", {
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
    avaliacao = get_object_or_404(Avaliacao, uuid=avaliacao_id, paciente__medico=request.user)
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
    return render(request, "questionario/dashboard/questionario.html", {
        "avaliacao": avaliacao, "secao": secao_atual, "perguntas": perguntas_pagina,
        "opcoes": OPCOES, "pagina": pagina, "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_secoes": [(i + 1, SECOES[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "readonly": True,
    })


# ─────────────────────────────────────────────────────────────
#  LAUDO AUTOMÁTICO — textos clínicos por quadrante e seção
# ─────────────────────────────────────────────────────────────

def _texto_quadrante(q):
    sid, cl, v, mx = q["id"], q["classificacao"], q["valor"], q["maximo"]
    TEXTOS = {
        "EX": {
            "Muito mais": (
                f"Pontuação significativamente elevada ({v}/{mx} pts), indicando forte tendência à Busca Sensorial. "
                "A criança procura ativamente por experiências sensoriais intensas com frequência muito maior do que seus pares, "
                "podendo apresentar alto nível de atividade, dificuldade de permanecer quieta e constante necessidade de estimulação."
            ),
            "Mais": (
                f"Pontuação acima do esperado ({v}/{mx} pts), indicando tendência aumentada à Busca Sensorial. "
                "A criança demonstra maior interesse por experiências sensoriais do que seus pares da mesma faixa etária."
            ),
            "Típico": f"Pontuação dentro do esperado ({v}/{mx} pts), com padrão de Exploração Sensorial adequado à faixa etária.",
            "Menos": f"Pontuação abaixo do esperado ({v}/{mx} pts), indicando menor tendência a buscar ativamente experiências sensoriais.",
            "Muito menos": (
                f"Pontuação significativamente reduzida ({v}/{mx} pts), evidenciando muito baixa tendência à Exploração Sensorial. "
                "A criança demonstra pouca iniciativa para buscar experiências sensoriais, podendo apresentar comportamento passivo e baixo nível de atividade."
            ),
        },
        "EV": {
            "Muito mais": (
                f"Pontuação significativamente elevada ({v}/{mx} pts), indicando forte padrão de Esquiva Sensorial. "
                "A criança demonstra intensa necessidade de evitar experiências sensoriais, podendo apresentar reações de recusa, "
                "retirada ou angústia frente a texturas, sons, luzes ou outros estímulos do cotidiano."
            ),
            "Mais": (
                f"Pontuação acima do esperado ({v}/{mx} pts), indicando tendência aumentada à Esquiva Sensorial. "
                "A criança demonstra maior necessidade de evitar estímulos sensoriais do que seus pares."
            ),
            "Típico": f"Pontuação dentro do esperado ({v}/{mx} pts), com padrão de Esquiva Sensorial adequado à faixa etária.",
            "Menos": f"Pontuação abaixo do esperado ({v}/{mx} pts), com menor tendência à Esquiva Sensorial.",
            "Muito menos": (
                f"Pontuação significativamente reduzida ({v}/{mx} pts), evidenciando muito baixa tendência à Esquiva Sensorial. "
                "A criança demonstra tolerância incomum a estímulos sensoriais intensos."
            ),
        },
        "SN": {
            "Muito mais": (
                f"Pontuação significativamente elevada ({v}/{mx} pts), indicando alta Sensibilidade Sensorial. "
                "A criança percebe e reage a estímulos do ambiente com grande intensidade, notando detalhes que outros ignorariam, "
                "o que pode interferir significativamente em suas atividades diárias e escolares."
            ),
            "Mais": (
                f"Pontuação acima do esperado ({v}/{mx} pts), com Sensibilidade Sensorial aumentada. "
                "A criança tende a perceber e reagir a estímulos com maior intensidade do que seus pares."
            ),
            "Típico": f"Pontuação dentro do esperado ({v}/{mx} pts), com padrão de Sensibilidade Sensorial adequado à faixa etária.",
            "Menos": f"Pontuação abaixo do esperado ({v}/{mx} pts), com menor Sensibilidade Sensorial.",
            "Muito menos": (
                f"Pontuação significativamente reduzida ({v}/{mx} pts), indicando baixíssima Sensibilidade Sensorial. "
                "A criança pode não perceber estímulos sensoriais que outros notariam com facilidade."
            ),
        },
        "OB": {
            "Muito mais": (
                f"Pontuação significativamente elevada ({v}/{mx} pts), indicando importante Baixo Registro Sensorial. "
                "A criança apresenta dificuldade em registrar e processar estímulos do ambiente de forma automática, "
                "podendo não notar objetos, pessoas ou eventos ao redor, com respostas demoradas e aparente desatenção."
            ),
            "Mais": (
                f"Pontuação acima do esperado ({v}/{mx} pts), com tendência ao Baixo Registro Sensorial. "
                "A criança pode necessitar de input sensorial mais intenso para registrar e responder ao ambiente."
            ),
            "Típico": f"Pontuação dentro do esperado ({v}/{mx} pts), com padrão de Registro Sensorial adequado à faixa etária.",
            "Menos": f"Pontuação abaixo do esperado ({v}/{mx} pts), com tendência aumentada ao Registro Sensorial ativo.",
            "Muito menos": f"Pontuação significativamente reduzida ({v}/{mx} pts), com padrão de Observação muito abaixo do esperado para a faixa etária.",
        },
    }
    return TEXTOS.get(sid, {}).get(cl, f"{q['nome']}: {v}/{mx} pts — {cl}.")


def _texto_secao(s):
    sid, cl, v, mx = s["id"], s["classificacao"], s["valor"], s["maximo"]
    TEXTOS = {
        "auditiva": {
            "Muito mais": f"Processamento auditivo significativamente elevado ({v}/{mx} pts): reações intensas a sons do ambiente, possível dificuldade em locais barulhentos, tendência a tapar os ouvidos e distração frequente por sons de fundo.",
            "Mais":       f"Processamento auditivo acima do esperado ({v}/{mx} pts): tendência a responder com maior intensidade a estímulos sonoros do que seus pares.",
            "Típico":     f"Processamento auditivo dentro do esperado ({v}/{mx} pts) para a faixa etária.",
            "Menos":      f"Processamento auditivo abaixo do esperado ({v}/{mx} pts), com menor reatividade a estímulos sonoros.",
            "Muito menos":f"Processamento auditivo significativamente reduzido ({v}/{mx} pts): baixa responsividade a estímulos sonoros do ambiente.",
        },
        "visual": {
            "Muito mais": f"Processamento visual significativamente elevado ({v}/{mx} pts): reações intensas a luz intensa, ambientes visualmente complexos ou movimentos no campo visual.",
            "Mais":       f"Processamento visual acima do esperado ({v}/{mx} pts): tendência aumentada a reagir e se distrair com estímulos visuais.",
            "Típico":     f"Processamento visual dentro do esperado ({v}/{mx} pts) para a faixa etária.",
            "Menos":      f"Processamento visual abaixo do esperado ({v}/{mx} pts).",
            "Muito menos":f"Processamento visual significativamente reduzido ({v}/{mx} pts): baixa responsividade a estímulos visuais do ambiente.",
        },
        "tato": {
            "Muito mais": f"Processamento tátil significativamente elevado ({v}/{mx} pts): alta reatividade ao toque, possível evitação de texturas, reações negativas ao toque inesperado, dificuldade com roupas e resistência ao cuidado pessoal.",
            "Mais":       f"Processamento tátil acima do esperado ({v}/{mx} pts): tendência a responder com maior intensidade ao toque e a diferentes texturas.",
            "Típico":     f"Processamento tátil dentro do esperado ({v}/{mx} pts) para a faixa etária.",
            "Menos":      f"Processamento tátil abaixo do esperado ({v}/{mx} pts): pode buscar mais input tátil.",
            "Muito menos":f"Processamento tátil significativamente reduzido ({v}/{mx} pts): baixa responsividade ao toque, podendo não perceber dor, temperatura ou texturas adequadamente.",
        },
        "movimento": {
            "Muito mais": f"Processamento vestibular/movimento significativamente elevado ({v}/{mx} pts): alta busca por atividades que envolvam movimento, agitação motora e dificuldade de manter-se quieta.",
            "Mais":       f"Processamento vestibular/movimento acima do esperado ({v}/{mx} pts): maior tendência a buscar experiências de movimento e atividade física.",
            "Típico":     f"Processamento vestibular/movimento dentro do esperado ({v}/{mx} pts) para a faixa etária.",
            "Menos":      f"Processamento de movimento abaixo do esperado ({v}/{mx} pts): possível cautela ou hesitação em atividades que envolvam movimento.",
            "Muito menos":f"Processamento de movimento significativamente reduzido ({v}/{mx} pts): possível baixa tolerância a mudanças posturais ou movimento.",
        },
        "posicao": {
            "Muito mais": f"Processamento proprioceptivo significativamente elevado ({v}/{mx} pts): intensa busca por pressão e resistência muscular, podendo abraçar com força excessiva e preferir roupas justas.",
            "Mais":       f"Processamento proprioceptivo acima do esperado ({v}/{mx} pts): tendência aumentada a buscar input de pressão e resistência.",
            "Típico":     f"Processamento proprioceptivo dentro do esperado ({v}/{mx} pts) para a faixa etária.",
            "Menos":      f"Processamento proprioceptivo abaixo do esperado ({v}/{mx} pts): possíveis dificuldades com noção corporal e gradação de força.",
            "Muito menos":f"Processamento proprioceptivo significativamente reduzido ({v}/{mx} pts): possíveis dificuldades de noção corporal, gradação de força e coordenação motora.",
        },
        "oral": {
            "Muito mais": f"Processamento oral significativamente elevado ({v}/{mx} pts): seletividade alimentar importante, recusa de texturas/sabores, comportamentos orais alterados e reações intensas à higiene bucal.",
            "Mais":       f"Processamento oral acima do esperado ({v}/{mx} pts): seletividade alimentar ou preferências orais acentuadas.",
            "Típico":     f"Processamento oral dentro do esperado ({v}/{mx} pts) para a faixa etária.",
            "Menos":      f"Processamento oral abaixo do esperado ({v}/{mx} pts).",
            "Muito menos":f"Processamento oral significativamente reduzido ({v}/{mx} pts): baixa responsividade oral, possível busca por input oral intenso.",
        },
        "conduta": {
            "Muito mais": f"Conduta com pontuação significativamente elevada ({v}/{mx} pts): possível impulsividade, dificuldade de autorregulação e comportamentos desafiadores relacionados ao processamento sensorial.",
            "Mais":       f"Conduta acima do esperado ({v}/{mx} pts): sinais de dificuldade de autorregulação comportamental.",
            "Típico":     f"Conduta dentro do esperado ({v}/{mx} pts) para a faixa etária.",
            "Menos":      f"Conduta abaixo do esperado ({v}/{mx} pts).",
            "Muito menos":f"Conduta com pontuação significativamente abaixo do esperado ({v}/{mx} pts).",
        },
        "socioemocional": {
            "Muito mais": f"Área socioemocional com pontuação significativamente elevada ({v}/{mx} pts): possíveis dificuldades de regulação emocional, ansiedade, resistência a mudanças de rotina e desafios nas relações interpessoais.",
            "Mais":       f"Área socioemocional acima do esperado ({v}/{mx} pts): possíveis dificuldades de regulação emocional ou interação social.",
            "Típico":     f"Desenvolvimento socioemocional dentro do esperado ({v}/{mx} pts) para a faixa etária.",
            "Menos":      f"Área socioemocional abaixo do esperado ({v}/{mx} pts).",
            "Muito menos":f"Área socioemocional com pontuação significativamente abaixo do esperado ({v}/{mx} pts).",
        },
        "atencao": {
            "Muito mais": f"Atenção com pontuação significativamente elevada ({v}/{mx} pts): importantes dificuldades atencionais possivelmente relacionadas ao processamento sensorial, incluindo distratividade, dificuldade de manutenção do foco e impulsividade.",
            "Mais":       f"Atenção acima do esperado ({v}/{mx} pts): sinais de dificuldades atencionais acima do esperado para a faixa etária.",
            "Típico":     f"Padrão atencional dentro do esperado ({v}/{mx} pts) para a faixa etária.",
            "Menos":      f"Atenção abaixo do esperado ({v}/{mx} pts).",
            "Muito menos":f"Atenção com pontuação significativamente abaixo do esperado ({v}/{mx} pts).",
        },
    }
    return TEXTOS.get(sid, {}).get(cl, f"{s['nome']}: {v}/{mx} pts — {cl}.")


@login_required
def laudo_sensorial(request, avaliacao_id):
    from datetime import date
    avaliacao = get_object_or_404(Avaliacao, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    if avaliacao.status != "concluida":
        return redirect("dashboard", avaliacao_id=avaliacao_id)

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
        s = {
            "id": sid, "nome": config["nome"], "valor": valor, "maximo": maximo,
            "pct": int(valor / maximo * 100) if maximo else 0,
            "classificacao": classificacao, "classe_css": classe_css(classificacao),
        }
        s["texto"] = _texto_secao(s)
        secoes_dados.append(s)

    quad_map = {"EX": avaliacao.pont_ex or 0, "EV": avaliacao.pont_ev or 0,
                "SN": avaliacao.pont_sn or 0, "OB": avaliacao.pont_ob or 0}
    quadrantes_dados = []
    for qid, config in QUADRANTES_CONFIG.items():
        valor = quad_map.get(qid, 0)
        maximo = config["max"]
        classificacao = classificar(valor, config["faixas"])
        q = {
            "id": qid, "nome": config["nome"], "subtitulo": config["subtitulo"],
            "valor": valor, "maximo": maximo,
            "pct": int(valor / maximo * 100) if maximo else 0,
            "classificacao": classificacao, "cor": config["cor"],
            "classe_css": classe_css(classificacao),
        }
        q["texto"] = _texto_quadrante(q)
        quadrantes_dados.append(q)

    # Identificar achados mais relevantes para síntese
    criticos = [q for q in quadrantes_dados if q["classificacao"] in ("Muito mais", "Muito menos")]
    alertas  = [q for q in quadrantes_dados if q["classificacao"] in ("Mais", "Menos")]
    if criticos:
        nomes = " e ".join(q["nome"] for q in criticos)
        intro_analise = (
            f"A avaliação do Perfil Sensorial evidenciou alterações significativas nos quadrantes de {nomes}, "
            "requerendo atenção clínica prioritária e planejamento terapêutico direcionado."
        )
    elif alertas:
        nomes = " e ".join(q["nome"] for q in alertas)
        intro_analise = (
            f"A avaliação do Perfil Sensorial evidenciou padrões acima ou abaixo do esperado nos quadrantes de {nomes}."
        )
    else:
        intro_analise = (
            "A avaliação do Perfil Sensorial evidenciou processamento sensorial dentro do esperado "
            "em todos os quadrantes avaliados."
        )

    # Calcular idade
    hoje = date.today()
    if paciente.data_nascimento:
        anos = hoje.year - paciente.data_nascimento.year - (
            (hoje.month, hoje.day) < (paciente.data_nascimento.month, paciente.data_nascimento.day)
        )
        meses = (hoje.month - paciente.data_nascimento.month - (
            hoje.day < paciente.data_nascimento.day
        )) % 12
        idade_str = f"{anos} anos e {meses} meses" if meses else f"{anos} anos"
    else:
        idade_str = "—"

    return render(request, "questionario/avaliacoes/laudo_sensorial.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "secoes": secoes_dados,
        "quadrantes": quadrantes_dados,
        "intro_analise": intro_analise,
        "idade_str": idade_str,
        "data_hoje": hoje.strftime("%d/%m/%Y"),
    })


@login_required
def enviar_email_link(request, avaliacao_id):
    from django.template.loader import render_to_string
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(Avaliacao, uuid=avaliacao_id, paciente__medico=request.user)
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
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {
        "paciente": paciente, "link": link,
    })
    try:
        enviar_email.delay(
            subject="Questionário IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário no link: {link}",
            recipient_list=[email_dest],
            html_message=html,
            fail_silently=False,
        )
    except Exception as exc:
        if is_ajax:
            from django.http import JsonResponse
            return JsonResponse({"ok": False, "message": f"Falha ao enviar e-mail: {exc}"})
        messages.error(request, f"Falha ao enviar e-mail: {exc}")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    avaliacao.email_enviado_em = tz.now()
    avaliacao.save(update_fields=["email_enviado_em"])
    if is_ajax:
        from django.http import JsonResponse
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)
