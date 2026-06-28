"""
Views públicas (sem login) para PS2 Bebê/CP (Winnie Dunn) e Perfil Sensorial Adulto.
Acessadas via token após o responsável/paciente clicar no link enviado pelo terapeuta.
"""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from ..models import AvaliacaoPS2Bebe, RespostaPS2Bebe, AvaliacaoAdultoSensorial, RespostaAdultoSensorial
from ..data.data_ps2_bebe_wd import (
    SECOES_PS2_BEBE, PERGUNTAS_PS2_BEBE, OPCOES_PS2,
    calcular_pontuacao_ps2_bebe,
)
from ..data.data_ps2_cp_wd import (
    SECOES_PS2_CP, PERGUNTAS_PS2_CP, ITENS_EXTRAS_PS2_CP,
    calcular_pontuacao_ps2_cp,
)
from ..data.data_adulto_sensorial import (
    SECOES_ADULTO, PERGUNTAS_ADULTO, OPCOES_ADULTO,
    calcular_pontuacao_adulto,
)


def ps2_bebe_wd_publico_view(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoPS2Bebe, token=token)

    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")

    faixa = avaliacao.faixa
    secoes       = SECOES_PS2_BEBE if faixa == "bebe" else SECOES_PS2_CP
    perguntas_d  = PERGUNTAS_PS2_BEBE if faixa == "bebe" else PERGUNTAS_PS2_CP
    extras       = [] if faixa == "bebe" else ITENS_EXTRAS_PS2_CP
    opcoes       = OPCOES_PS2
    total_pags   = len(secoes)

    if pagina < 1 or pagina > total_pags:
        pagina = 1

    secao_atual  = secoes[pagina - 1]
    itens_secao  = [i for i in secao_atual["itens"] if i not in extras]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens_secao)}

    if request.method == "POST":
        erros = []
        novas = {}
        for item in itens_secao:
            val = request.POST.get(f"item_{item}")
            if val is None:
                erros.append(item)
            else:
                try:
                    v = int(val)
                    if 1 <= v <= 5:
                        novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)

        if erros:
            messages.error(request, "Por favor, responda todas as perguntas antes de continuar.")
        else:
            for item, valor in novas.items():
                RespostaPS2Bebe.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={"valor": valor}
                )
            if pagina < total_pags:
                avaliacao.pagina_atual = pagina + 1
                avaliacao.save(update_fields=["pagina_atual"])
                return redirect("ps2_bebe_wd_publico", token=token, pagina=pagina + 1)
            else:
                respostas_finais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
                if faixa == "bebe":
                    p = calcular_pontuacao_ps2_bebe(respostas_finais)
                else:
                    p = calcular_pontuacao_ps2_cp(respostas_finais)
                avaliacao.pont_geral          = p.get("geral", 0)
                avaliacao.pont_auditivo       = p.get("auditivo", 0)
                avaliacao.pont_visual         = p.get("visual", 0)
                avaliacao.pont_tato           = p.get("tato", 0)
                avaliacao.pont_movimentos     = p.get("movimentos", 0)
                avaliacao.pont_oral           = p.get("oral", 0)
                avaliacao.pont_comportamental = p.get("comportamental", 0)
                avaliacao.pont_ex = p.get("EX", 0)
                avaliacao.pont_ev = p.get("EV", 0)
                avaliacao.pont_sn = p.get("SN", 0)
                avaliacao.pont_ob = p.get("OB", 0)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    from ..views.sensorial import notificar_terapeuta
                    notificar_terapeuta(avaliacao.paciente, "ps2_bebe_wd", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
        respostas_salvas.update(novas)

    perguntas = [
        {"numero": item, "texto": perguntas_d.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens_secao
    ]
    return render(request, "questionario/avaliacoes/bebe_form.html", {
        "avaliacao": avaliacao,
        "secao": secao_atual,
        "perguntas": perguntas,
        "opcoes": opcoes,
        "pagina": pagina,
        "total": total_pags,
        "progresso": int((pagina - 1) / total_pags * 100),
        "paginas_secoes": [(i + 1, secoes[i]["nome"]) for i in range(total_pags)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
    })


def adulto_sensorial_publico_view(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoAdultoSensorial, token=token)

    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")

    total_pags = len(SECOES_ADULTO)
    if pagina < 1 or pagina > total_pags:
        pagina = 1

    secao_atual = SECOES_ADULTO[pagina - 1]
    itens_secao = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens_secao)}

    if request.method == "POST":
        erros = []
        novas = {}
        for item in itens_secao:
            val = request.POST.get(f"item_{item}")
            if val is None:
                erros.append(item)
            else:
                try:
                    v = int(val)
                    if 1 <= v <= 5:
                        novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)

        if erros:
            messages.error(request, "Por favor, responda todas as perguntas antes de continuar.")
        else:
            for item, valor in novas.items():
                RespostaAdultoSensorial.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={"valor": valor}
                )
            if pagina < total_pags:
                avaliacao.pagina_atual = pagina + 1
                avaliacao.save(update_fields=["pagina_atual"])
                return redirect("adulto_sensorial_publico", token=token, pagina=pagina + 1)
            else:
                respostas_finais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
                p = calcular_pontuacao_adulto(respostas_finais)
                avaliacao.pont_baixo_registro   = p.get("Q1", 0)
                avaliacao.pont_procura_sensacao = p.get("Q2", 0)
                avaliacao.pont_sensitividade    = p.get("Q3", 0)
                avaliacao.pont_evita_sensacao   = p.get("Q4", 0)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    from ..views.sensorial import notificar_terapeuta
                    notificar_terapeuta(avaliacao.paciente, "adulto_sensorial", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
        respostas_salvas.update(novas)

    perguntas = [
        {"numero": item, "texto": PERGUNTAS_ADULTO.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens_secao
    ]
    return render(request, "questionario/avaliacoes/bebe_form.html", {
        "avaliacao": avaliacao,
        "secao": secao_atual,
        "perguntas": perguntas,
        "opcoes": OPCOES_ADULTO,
        "pagina": pagina,
        "total": total_pags,
        "progresso": int((pagina - 1) / total_pags * 100),
        "paginas_secoes": [(i + 1, SECOES_ADULTO[i]["nome"]) for i in range(total_pags)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
    })
