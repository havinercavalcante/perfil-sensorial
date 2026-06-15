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
    """Retorna apenas a faixa correspondente à idade do paciente."""
    adequadas = [f for f in faixas if int(f['faixa'].split('_')[0]) <= idade_anos]
    return [adequadas[-1]] if adequadas else [faixas[0]]


def _get_perguntas_por_faixa(dom, respostas_salvas, faixas=None):
    """Retorna lista de faixas com itens e respostas para renderizar."""
    perguntas_map = PORTAGE_PERGUNTAS_MAP[dom['key']]
    faixas_render = []
    for f in (faixas if faixas is not None else dom['faixas']):
        itens_render = [
            {
                'numero': n,
                'texto':  perguntas_map.get(n, ''),
                'resposta_salva': respostas_salvas.get(n),
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

    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("portage_form", avaliacao_id=avaliacao_id, pagina=1)

    dom = PORTAGE_DOMINIOS[pagina - 1]
    faixas_dom = _faixas_por_idade(dom['faixas'], _idade_na_data(avaliacao.paciente.data_nascimento, avaliacao.data))
    todos_itens = [n for f in faixas_dom for n in f['itens']]
    respostas_salvas = {
        r.numero_item: r.valor
        for r in avaliacao.respostas.filter(dominio=dom['key'], numero_item__in=todos_itens)
    }

    itens_faltando_local = []
    respostas_para_render = respostas_salvas

    if request.method == "POST":
        confirmar_incompleto = request.POST.get("confirmar_incompleto") == "1"
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

        if erros and not confirmar_incompleto:
            respostas_para_render = dict(respostas_salvas)
            respostas_para_render.update(novas)
            itens_faltando_local = erros
        else:
            for n, v in novas.items():
                RespostaPortage.objects.update_or_create(
                    avaliacao=avaliacao, dominio=dom['key'], numero_item=n,
                    defaults={"valor": v}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, TOTAL_PAGINAS)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > TOTAL_PAGINAS:
                return redirect("portage_concluir", avaliacao_id=avaliacao_id)
            return redirect("portage_form", avaliacao_id=avaliacao_id, pagina=proxima)

    faixas_render = _get_perguntas_por_faixa(dom, respostas_para_render, faixas=faixas_dom)

    return render(request, "questionario/avaliacoes/portage_form.html", {
        "avaliacao": avaliacao,
        "dominio": dom,
        "faixas": faixas_render,
        "todos_itens": todos_itens,
        "opcoes": PORTAGE_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, PORTAGE_DOMINIOS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
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

    # Calcular resultados por domínio baseado na faixa etária do paciente
    def adequado_para_faixa(dom_key, faixas_dom):
        """Verifica se o paciente atingiu ≥80% de SIM na faixa etária."""
        f = faixas_dom[0]
        total = len(f['itens'])
        if total == 0:
            return False
        sim = avaliacao.respostas.filter(dominio=dom_key, numero_item__in=f['itens'], valor=2).count()
        return sim / total >= 0.8

    idade_paciente = _idade_na_data(avaliacao.paciente.data_nascimento, avaliacao.data)
    dominios_resultado = []
    for dom in PORTAGE_DOMINIOS:
        faixas_dom = _faixas_por_idade(dom['faixas'], idade_paciente)
        faixa_atual = faixas_dom[0]
        itens_faixa = faixa_atual['itens']
        total_itens = len(itens_faixa)
        sim = avaliacao.respostas.filter(dominio=dom['key'], numero_item__in=itens_faixa, valor=2).count()
        pct = int(sim / total_itens * 100) if total_itens else 0
        atingiu = adequado_para_faixa(dom['key'], faixas_dom)

        idx_faixa = next(i for i, f in enumerate(dom['faixas']) if f['faixa'] == faixa_atual['faixa'])
        if pct >= 80:
            nivel_label = f"Adequado — {faixa_atual['label']}"
            nivel_classe = "nivel-ok"
        elif pct >= 50:
            nivel_label = f"Em desenvolvimento — {faixa_atual['label']}"
            nivel_classe = "nivel-medio"
        else:
            if idx_faixa > 0:
                nivel_label = f"Estimado: {dom['faixas'][idx_faixa - 1]['label']}"
            else:
                nivel_label = "Habilidades emergentes (0–1 ano)"
            nivel_classe = "nivel-baixo"

        perguntas = PORTAGE_PERGUNTAS_MAP[dom['key']]
        mediacao_nums = sorted(avaliacao.respostas.filter(
            dominio=dom['key'], numero_item__in=itens_faixa, valor=1
        ).values_list('numero_item', flat=True))
        metas = [{'numero': n, 'texto': perguntas.get(n, '')} for n in mediacao_nums]

        dominios_resultado.append({
            'key':         dom['key'],
            'nome':        dom['nome'],
            'sigla':       dom['sigla'],
            'cor':         dom['cor'],
            'sim':         sim,
            'total':       total_itens,
            'pct':         pct,
            'faixa_label': faixa_atual['label'],
            'atingiu':     atingiu,
            'nivel_label': nivel_label,
            'nivel_classe': nivel_classe,
            'metas':       metas,
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
    dominios_comp = [
        {"nome": d["nome"], "campo": PORTAGE_PONT_MAP[d['key']], "max": 100}
        for d in dominios_resultado
    ]
    cores_linha = ["#2E7D6B", "#3E73D1", "#E8793A", "#9B59B6", "#E8B84B"]
    comparativo_datasets = []
    for i, dom in enumerate(dominios_comp):
        valores = [(getattr(av, dom["campo"]) or 0) for av in todas_av]
        comparativo_datasets.append({"label": dom["nome"], "data": valores, "borderColor": cores_linha[i], "backgroundColor": cores_linha[i] + "33", "tension": 0.3})

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

    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("portage_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    dom = PORTAGE_DOMINIOS[pagina - 1]
    faixas_dom = _faixas_por_idade(dom['faixas'], _idade_na_data(avaliacao.paciente.data_nascimento, avaliacao.data))
    todos_itens = [n for f in faixas_dom for n in f['itens']]
    respostas_salvas = {
        r.numero_item: r.valor
        for r in avaliacao.respostas.filter(dominio=dom['key'], numero_item__in=todos_itens)
    }
    faixas_render = _get_perguntas_por_faixa(dom, respostas_salvas, faixas=faixas_dom)

    return render(request, "questionario/avaliacoes/portage_form.html", {
        "avaliacao": avaliacao,
        "dominio": dom,
        "faixas": faixas_render,
        "todos_itens": todos_itens,
        "opcoes": PORTAGE_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, PORTAGE_DOMINIOS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": [],
        "readonly": True,
    })


# ── View pública (token) ──────────────────────────────────────────────────────

def portage_publico_view(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoPortage, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")

    if pagina < 1 or pagina > TOTAL_PAGINAS:
        pagina = 1

    dom = PORTAGE_DOMINIOS[pagina - 1]
    faixas_dom = _faixas_por_idade(dom['faixas'], _idade_na_data(avaliacao.paciente.data_nascimento, avaliacao.data))
    todos_itens = [n for f in faixas_dom for n in f['itens']]
    respostas_salvas = {
        r.numero_item: r.valor
        for r in avaliacao.respostas.filter(dominio=dom['key'], numero_item__in=todos_itens)
    }

    itens_faltando_local = []
    respostas_para_render = respostas_salvas

    if request.method == "POST":
        confirmar_incompleto = request.POST.get("confirmar_incompleto") == "1"
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

        if erros and not confirmar_incompleto:
            respostas_para_render = dict(respostas_salvas)
            respostas_para_render.update(novas)
            itens_faltando_local = erros
        else:
            for n, v in novas.items():
                RespostaPortage.objects.update_or_create(
                    avaliacao=avaliacao, dominio=dom['key'], numero_item=n,
                    defaults={"valor": v}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, TOTAL_PAGINAS)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular_pontuacao(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "portage", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("portage_publico", token=token, pagina=proxima)

    faixas_render = _get_perguntas_por_faixa(dom, respostas_para_render, faixas=faixas_dom)

    return render(request, "questionario/avaliacoes/portage_form.html", {
        "avaliacao": avaliacao,
        "dominio": dom,
        "faixas": faixas_render,
        "todos_itens": todos_itens,
        "opcoes": PORTAGE_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, PORTAGE_DOMINIOS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
        "token": token,
        "itens_faltando": itens_faltando_local,
    })
