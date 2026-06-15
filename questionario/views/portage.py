import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Paciente, AvaliacaoPortage, RespostaPortage
from ..data.portage_data import PORTAGE_DOMINIOS, PORTAGE_OPCOES
from ..data.portage_data import (
    PORTAGE_SOC_PERGUNTAS, PORTAGE_COG_PERGUNTAS, PORTAGE_LIN_PERGUNTAS,
    PORTAGE_AC_PERGUNTAS, PORTAGE_MOT_PERGUNTAS,
)
from ..services import notificar_terapeuta

PORTAGE_PERGUNTAS_MAP = {
    'socializacao':  PORTAGE_SOC_PERGUNTAS,
    'cognicao':      PORTAGE_COG_PERGUNTAS,
    'linguagem':     PORTAGE_LIN_PERGUNTAS,
    'auto_cuidados': PORTAGE_AC_PERGUNTAS,
    'motor':         PORTAGE_MOT_PERGUNTAS,
}

PORTAGE_PONT_MAP = {
    'socializacao':  'pont_soc',
    'cognicao':      'pont_cog',
    'linguagem':     'pont_lin',
    'auto_cuidados': 'pont_ac',
    'motor':         'pont_mot',
}

TOTAL_PAGINAS = len(PORTAGE_DOMINIOS)


def _idade_na_data(data_nascimento, data_referencia):
    """Calcula a idade em anos completos numa data de referência específica."""
    b = data_nascimento
    d = data_referencia
    return d.year - b.year - ((d.month, d.day) < (b.month, b.day))


def _calcular_pontuacao(avaliacao):
    idade = _idade_na_data(avaliacao.paciente.data_nascimento, avaliacao.data)
    for dom in PORTAGE_DOMINIOS:
        key = dom['key']
        campo = PORTAGE_PONT_MAP[key]
        faixas_dom = _faixas_por_idade(dom['faixas'], idade)
        itens_faixa = [n for f in faixas_dom for n in f['itens']]
        total_sim = avaliacao.respostas.filter(dominio=key, numero_item__in=itens_faixa, valor=2).count()
        setattr(avaliacao, campo, total_sim)
    return avaliacao


def _faixas_por_idade(faixas, idade_anos):
    """Retorna todas as faixas de 0 até a idade do paciente."""
    adequadas = [f for f in faixas if int(f['faixa'].split('_')[0]) <= idade_anos]
    return adequadas if adequadas else [faixas[0]]


def _get_paginas(idade_anos):
    """Retorna lista de {'dom', 'faixa'} — uma entrada por faixa × domínio."""
    paginas = []
    for dom in PORTAGE_DOMINIOS:
        for f in _faixas_por_idade(dom['faixas'], idade_anos):
            paginas.append({'dom': dom, 'faixa': f})
    return paginas


def _get_dominios_progresso(paginas, pagina_atual):
    """Retorna 5 dicts de domínio com status done/active/'' para os step-dots."""
    resultado = []
    for dom in PORTAGE_DOMINIOS:
        nums = [i + 1 for i, p in enumerate(paginas) if p['dom']['key'] == dom['key']]
        if not nums:
            continue
        if pagina_atual > nums[-1]:
            status = 'done'
        elif pagina_atual >= nums[0]:
            status = 'active'
        else:
            status = ''
        resultado.append({'nome': dom['nome'], 'status': status, 'primeira_pagina': nums[0]})
    return resultado


def _get_perguntas_por_faixa(dom, respostas_salvas, faixas=None, observacoes=None):
    """Retorna lista de faixas com itens, respostas e observações para renderizar."""
    perguntas_map = PORTAGE_PERGUNTAS_MAP[dom['key']]
    obs = observacoes or {}
    faixas_render = []
    for f in (faixas if faixas is not None else dom['faixas']):
        itens_render = [
            {
                'numero':         n,
                'texto':          perguntas_map.get(n, ''),
                'resposta_salva': respostas_salvas.get(n),
                'observacao_salva': obs.get(n, ''),
            }
            for n in f['itens']
        ]
        faixas_render.append({
            'faixa': f['faixa'],
            'label': f['label'],
            'itens': itens_render,
        })
    return faixas_render


# ── Views autenticadas ────────────────────────────────────────────────────────

@login_required
def nova_avaliacao_portage(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('portage'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo Guia Portage.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoPortage.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("portage_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def portage_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoPortage, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("portage_resultado", avaliacao_id=avaliacao_id)

    idade = _idade_na_data(avaliacao.paciente.data_nascimento, avaliacao.data)
    paginas = _get_paginas(idade)
    total_paginas = len(paginas)

    if pagina < 1 or pagina > total_paginas:
        return redirect("portage_form", avaliacao_id=avaliacao_id, pagina=1)

    pagina_info = paginas[pagina - 1]
    dom = pagina_info['dom']
    faixa = pagina_info['faixa']
    todos_itens = list(faixa['itens'])

    respostas_qs = avaliacao.respostas.filter(dominio=dom['key'], numero_item__in=todos_itens)
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    observacoes_salvas = {r.numero_item: r.observacao for r in respostas_qs}

    itens_faltando_local = []
    respostas_para_render = respostas_salvas
    observacoes_para_render = observacoes_salvas

    if request.method == "POST":
        novas = {}
        erros = []
        for n in todos_itens:
            val = request.POST.get(f"item_{n}")
            if val is None:
                erros.append(n)
            else:
                try:
                    v = int(val)
                    if v in (0, 1, 2):
                        novas[n] = v
                    else:
                        erros.append(n)
                except (ValueError, TypeError):
                    erros.append(n)

        novas_obs = {n: request.POST.get(f"obs_{n}", "").strip() for n in todos_itens}
        observacoes_para_render = {**observacoes_salvas, **novas_obs}

        if erros:
            respostas_para_render = {**respostas_salvas, **novas}
            itens_faltando_local = erros
        else:
            for n, v in novas.items():
                RespostaPortage.objects.update_or_create(
                    avaliacao=avaliacao, dominio=dom['key'], numero_item=n,
                    defaults={"valor": v, "observacao": novas_obs.get(n, "")}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, total_paginas)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > total_paginas:
                return redirect("portage_concluir", avaliacao_id=avaliacao_id)
            return redirect("portage_form", avaliacao_id=avaliacao_id, pagina=proxima)

    faixas_do_dom = [p for p in paginas if p['dom']['key'] == dom['key']]
    idx_no_dom = next(i for i, p in enumerate(faixas_do_dom) if p['faixa']['faixa'] == faixa['faixa'])
    faixas_render = _get_perguntas_por_faixa(dom, respostas_para_render, faixas=[faixa], observacoes=observacoes_para_render)

    return render(request, "questionario/avaliacoes/portage_form.html", {
        "avaliacao": avaliacao,
        "dominio": dom,
        "faixa_label": faixa['label'],
        "faixa_no_dominio": idx_no_dom + 1,
        "total_no_dominio": len(faixas_do_dom),
        "faixas": faixas_render,
        "todos_itens": todos_itens,
        "opcoes": PORTAGE_OPCOES,
        "pagina": pagina,
        "total": total_paginas,
        "progresso": int((pagina - 1) / total_paginas * 100),
        "paginas_dominios": _get_dominios_progresso(paginas, pagina),
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando_local,
    })


@login_required
def portage_concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoPortage, uuid=avaliacao_id, paciente__medico=request.user)
    avaliacao = _calcular_pontuacao(avaliacao)
    avaliacao.status = "concluida"
    avaliacao.save()
    return redirect("portage_resultado", avaliacao_id=avaliacao_id)


@login_required
def portage_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoPortage, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("portage_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    if avaliacao.pont_soc is None:
        avaliacao = _calcular_pontuacao(avaliacao)
        avaliacao.save(update_fields=["pont_soc", "pont_cog", "pont_lin", "pont_ac", "pont_mot"])

    idade_paciente = _idade_na_data(avaliacao.paciente.data_nascimento, avaliacao.data)
    dominios_resultado = []
    for dom in PORTAGE_DOMINIOS:
        faixas_dom = _faixas_por_idade(dom['faixas'], idade_paciente)
        faixa_atual = faixas_dom[-1]  # faixa da idade da criança

        # Estatísticas por faixa
        faixas_resultado = []
        for f in faixas_dom:
            total_f = len(f['itens'])
            sim_f = avaliacao.respostas.filter(dominio=dom['key'], numero_item__in=f['itens'], valor=2).count()
            pct_f = int(sim_f / total_f * 100) if total_f else 0
            faixas_resultado.append({
                'label':   f['label'],
                'sim':     sim_f,
                'total':   total_f,
                'pct':     pct_f,
                'atingiu': pct_f >= 80,
            })

        # Resultado da faixa atual (para cards e gráficos)
        dados_atual = faixas_resultado[-1]
        pct = dados_atual['pct']
        atingiu = dados_atual['atingiu']

        # Nível desenvolvimental: a faixa mais alta com ≥80% SIM
        nivel_faixa_label = None
        for f_data in faixas_resultado:
            if f_data['atingiu']:
                nivel_faixa_label = f_data['label']

        if nivel_faixa_label:
            if nivel_faixa_label == faixa_atual['label']:
                nivel_label = f"Adequado — {nivel_faixa_label}"
                nivel_classe = "nivel-ok"
            else:
                nivel_label = f"Nível desenvolvimental: {nivel_faixa_label}"
                nivel_classe = "nivel-medio"
        else:
            nivel_label = "Habilidades emergentes"
            nivel_classe = "nivel-baixo"

        # Alvos de intervenção: SIM com mediação na faixa atual
        perguntas = PORTAGE_PERGUNTAS_MAP[dom['key']]
        mediacao_nums = sorted(avaliacao.respostas.filter(
            dominio=dom['key'], numero_item__in=faixa_atual['itens'], valor=1
        ).values_list('numero_item', flat=True))
        metas = [{'numero': n, 'texto': perguntas.get(n, '')} for n in mediacao_nums]

        dominios_resultado.append({
            'key':          dom['key'],
            'nome':         dom['nome'],
            'sigla':        dom['sigla'],
            'cor':          dom['cor'],
            'sim':          dados_atual['sim'],
            'total':        dados_atual['total'],
            'pct':          pct,
            'faixa_label':  faixa_atual['label'],
            'atingiu':      atingiu,
            'nivel_label':  nivel_label,
            'nivel_classe': nivel_classe,
            'faixas':       faixas_resultado,
            'metas':        metas,
        })

    total_sim = sum(d['sim'] for d in dominios_resultado)
    total_itens_geral = sum(d['total'] for d in dominios_resultado)
    pct_geral = int(total_sim / total_itens_geral * 100) if total_itens_geral else 0

    if request.method == "POST" and "observacoes" in request.POST:
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
        return redirect("portage_resultado", avaliacao_id=avaliacao_id)

    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_portage.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    comparativo_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av])
    cores_linha = ["#2E7D6B", "#3E73D1", "#E8793A", "#9B59B6", "#E8B84B"]
    comparativo_datasets = []
    for i, dom in enumerate(PORTAGE_DOMINIOS):
        valores = []
        for av in todas_av:
            idade_av = _idade_na_data(av.paciente.data_nascimento, av.data)
            faixas_av = _faixas_por_idade(dom['faixas'], idade_av)
            faixa_av = faixas_av[-1]
            total_av = len(faixa_av['itens'])
            sim_av = av.respostas.filter(dominio=dom['key'], numero_item__in=faixa_av['itens'], valor=2).count()
            valores.append(int(sim_av / total_av * 100) if total_av else 0)
        comparativo_datasets.append({
            "label": dom['nome'],
            "data": valores,
            "borderColor": cores_linha[i],
            "backgroundColor": cores_linha[i] + "33",
            "tension": 0.3,
        })

    tem_metas = any(d['metas'] for d in dominios_resultado)

    return render(request, "questionario/avaliacoes/portage_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "dominios": dominios_resultado,
        "total_sim": total_sim,
        "total_itens": total_itens_geral,
        "pct_geral": pct_geral,
        "comparativo_labels": comparativo_labels,
        "comparativo_datasets": json.dumps(comparativo_datasets),
        "tem_comparativo": len(todas_av) > 1,
        "outras_avaliacoes": outras,
        "tem_metas": tem_metas,
    })


@login_required
def portage_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoPortage, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação Portage excluída com sucesso."})
        messages.success(request, "Avaliação Portage excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def portage_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoPortage, uuid=avaliacao_id, paciente__medico=request.user)

    idade = _idade_na_data(avaliacao.paciente.data_nascimento, avaliacao.data)
    paginas = _get_paginas(idade)
    total_paginas = len(paginas)

    if pagina < 1 or pagina > total_paginas:
        return redirect("portage_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    pagina_info = paginas[pagina - 1]
    dom = pagina_info['dom']
    faixa = pagina_info['faixa']
    todos_itens = list(faixa['itens'])

    respostas_qs = avaliacao.respostas.filter(dominio=dom['key'], numero_item__in=todos_itens)
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    observacoes_salvas = {r.numero_item: r.observacao for r in respostas_qs}

    faixas_do_dom = [p for p in paginas if p['dom']['key'] == dom['key']]
    idx_no_dom = next(i for i, p in enumerate(faixas_do_dom) if p['faixa']['faixa'] == faixa['faixa'])
    faixas_render = _get_perguntas_por_faixa(dom, respostas_salvas, faixas=[faixa], observacoes=observacoes_salvas)

    return render(request, "questionario/avaliacoes/portage_form.html", {
        "avaliacao": avaliacao,
        "dominio": dom,
        "faixa_label": faixa['label'],
        "faixa_no_dominio": idx_no_dom + 1,
        "total_no_dominio": len(faixas_do_dom),
        "faixas": faixas_render,
        "todos_itens": todos_itens,
        "opcoes": PORTAGE_OPCOES,
        "pagina": pagina,
        "total": total_paginas,
        "progresso": int((pagina - 1) / total_paginas * 100),
        "paginas_dominios": _get_dominios_progresso(paginas, pagina),
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": [],
        "readonly": True,
    })


# ── View pública (token) ──────────────────────────────────────────────────────

def portage_publico_view(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoPortage, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")

    idade = _idade_na_data(avaliacao.paciente.data_nascimento, avaliacao.data)
    paginas = _get_paginas(idade)
    total_paginas = len(paginas)

    if pagina < 1 or pagina > total_paginas:
        pagina = 1

    pagina_info = paginas[pagina - 1]
    dom = pagina_info['dom']
    faixa = pagina_info['faixa']
    todos_itens = list(faixa['itens'])

    respostas_salvas = {
        r.numero_item: r.valor
        for r in avaliacao.respostas.filter(dominio=dom['key'], numero_item__in=todos_itens)
    }

    itens_faltando_local = []
    respostas_para_render = respostas_salvas

    if request.method == "POST":
        novas = {}
        erros = []
        for n in todos_itens:
            val = request.POST.get(f"item_{n}")
            if val is None:
                erros.append(n)
            else:
                try:
                    v = int(val)
                    if v in (0, 1, 2):
                        novas[n] = v
                    else:
                        erros.append(n)
                except (ValueError, TypeError):
                    erros.append(n)

        if erros:
            respostas_para_render = {**respostas_salvas, **novas}
            itens_faltando_local = erros
        else:
            for n, v in novas.items():
                RespostaPortage.objects.update_or_create(
                    avaliacao=avaliacao, dominio=dom['key'], numero_item=n,
                    defaults={"valor": v}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, total_paginas)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > total_paginas:
                avaliacao = _calcular_pontuacao(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "portage", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("portage_publico", token=token, pagina=proxima)

    faixas_do_dom = [p for p in paginas if p['dom']['key'] == dom['key']]
    idx_no_dom = next(i for i, p in enumerate(faixas_do_dom) if p['faixa']['faixa'] == faixa['faixa'])
    faixas_render = _get_perguntas_por_faixa(dom, respostas_para_render, faixas=[faixa])

    return render(request, "questionario/avaliacoes/portage_form.html", {
        "avaliacao": avaliacao,
        "dominio": dom,
        "faixa_label": faixa['label'],
        "faixa_no_dominio": idx_no_dom + 1,
        "total_no_dominio": len(faixas_do_dom),
        "faixas": faixas_render,
        "todos_itens": todos_itens,
        "opcoes": PORTAGE_OPCOES,
        "pagina": pagina,
        "total": total_paginas,
        "progresso": int((pagina - 1) / total_paginas * 100),
        "paginas_dominios": _get_dominios_progresso(paginas, pagina),
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
        "token": token,
        "itens_faltando": itens_faltando_local,
    })
