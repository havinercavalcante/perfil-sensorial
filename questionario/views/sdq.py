import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoSDQ, RespostaSDQ
from ..data.data_sdq import SDQ_ITENS, SDQ_SUBESCALAS, SDQ_OPCOES, SDQ_CORTE
from ..services import notificar_terapeuta

# ── Paginação por subescala ───────────────────────────────────────────────────

SDQ_PAGINAS = [
    {"key": "emocional",      "nome": "Sintomas Emocionais",       "cor": "#E74C3C", "campo": "pont_emocional"},
    {"key": "conduta",        "nome": "Problemas de Conduta",      "cor": "#E67E22", "campo": "pont_conduta"},
    {"key": "hiperatividade", "nome": "Hiperatividade/Desatenção", "cor": "#3498DB", "campo": "pont_hiperatividade"},
    {"key": "pares",          "nome": "Problemas com Colegas",     "cor": "#9B59B6", "campo": "pont_pares"},
    {"key": "prossocial",     "nome": "Comportamento Prossocial",  "cor": "#27AE60", "campo": "pont_prossocial"},
]

TOTAL_PAGINAS = len(SDQ_PAGINAS)

_URL_NAMES = {
    "url_form_name": "sdq_form",
    "url_publico_name": "sdq_publico",
    "url_visualizar_name": "sdq_visualizar",
    "url_resultado_name": "sdq_resultado",
    "avaliacao_titulo": "SDQ — Questionário de Capacidades e Dificuldades",
}

# Índice rápido: numero_item → dict do item
_ITENS_INDEX = {item["numero"]: item for item in SDQ_ITENS}

# Itens por subescala: key → lista de dicts
_ITENS_POR_SUBESCALA = {
    key: [item for item in SDQ_ITENS if item["subescala"] == key]
    for key in SDQ_SUBESCALAS
}


def _itens_da_pagina(pagina_dict):
    """Retorna lista de (numero, texto) para a subescala da página."""
    key = pagina_dict["key"]
    return [(item["numero"], item["texto"]) for item in _ITENS_POR_SUBESCALA[key]]


def _processar_post_pagina_sdq(request, pagina_dict):
    """Processa POST de uma página SDQ. Retorna (erros, novas, obs)."""
    itens = _itens_da_pagina(pagina_dict)
    valores_validos = {0, 1, 2}
    erros, novas, obs = [], {}, {}
    for numero, _ in itens:
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


def _salvar_respostas_sdq(avaliacao, novas, obs):
    for numero, valor in novas.items():
        RespostaSDQ.objects.update_or_create(
            avaliacao=avaliacao, numero_item=numero,
            defaults={"valor": valor, "observacao": obs.get(numero, "")}
        )


def _context_pagina(avaliacao, pagina_dict, pagina, itens_render, respostas_salvas, itens_faltando, extra=None):
    """Monta o contexto padrão para avaliacao_dominio_form.html."""
    ctx = {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": pagina_dict,
        "itens": itens_render,
        "opcoes": SDQ_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, SDQ_PAGINAS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando,
    }
    if extra:
        ctx.update(extra)
    return ctx


# ── Cálculo e resultado ───────────────────────────────────────────────────────

def _calcular_sdq(avaliacao):
    """Calcula pontuações por subescala e total de dificuldades."""
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}

    for key, sub in SDQ_SUBESCALAS.items():
        total = 0
        for item in SDQ_ITENS:
            if item["subescala"] != key:
                continue
            val = respostas.get(item["numero"], 0)
            total += (2 - val) if item["reverso"] else val
        setattr(avaliacao, sub["campo"], total)

    # Total de Dificuldades = soma das 4 subescalas (excl. prossocial)
    avaliacao.pont_total_dificuldades = (
        (avaliacao.pont_emocional or 0)
        + (avaliacao.pont_conduta or 0)
        + (avaliacao.pont_hiperatividade or 0)
        + (avaliacao.pont_pares or 0)
    )
    return avaliacao


def _classificar(score, corte_list):
    for label, min_v, max_v in corte_list:
        if min_v <= score <= max_v:
            return label
    return corte_list[-1][0]


def _build_resultado(avaliacao):
    resultado = []
    for key, sub in SDQ_SUBESCALAS.items():
        score = getattr(avaliacao, sub["campo"]) or 0
        max_score = 10
        resultado.append({
            "key": key,
            "nome": sub["nome"],
            "cor": sub["cor"],
            "score": score,
            "max": max_score,
            "pct": int(score / max_score * 100),
            "classificacao": _classificar(score, SDQ_CORTE[key]),
        })
    total = avaliacao.pont_total_dificuldades or 0
    return resultado, total, _classificar(total, SDQ_CORTE["total"])


# ── Views autenticadas ────────────────────────────────────────────────────────

@login_required
def nova_avaliacao_sdq(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('sdq'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo SDQ.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoSDQ.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("sdq_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def sdq_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoSDQ, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("sdq_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("sdq_form", avaliacao_id=avaliacao_id, pagina=1)

    pagina_dict = SDQ_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros_pagina = [n for n, _ in itens_pagina]

    respostas_qs = list(avaliacao.respostas.filter(numero_item__in=numeros_pagina))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas = {r.numero_item: r.observacao for r in respostas_qs}
    itens_faltando = []
    obs_render = {}

    if request.method == "POST":
        confirmar_incompleto = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_pagina_sdq(request, pagina_dict)
        obs_render = obs

        if erros and not confirmar_incompleto:
            resp_render = dict(respostas_salvas)
            resp_render.update(novas)
            respostas_salvas = resp_render
            itens_faltando = erros
        else:
            _salvar_respostas_sdq(avaliacao, novas, obs)
            proxima = pagina + 1
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular_sdq(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                return redirect("sdq_resultado", avaliacao_id=avaliacao_id)
            return redirect("sdq_form", avaliacao_id=avaliacao_id, pagina=proxima)

    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": respostas_salvas.get(n),
         "observacao_salva": obs_render.get(n, obs_salvas.get(n, ""))}
        for n, t in itens_pagina
    ]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _context_pagina(avaliacao, pagina_dict, pagina, itens_render, respostas_salvas, itens_faltando))


@login_required
def sdq_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSDQ, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("sdq_form", avaliacao_id=avaliacao_id, pagina=1)
    resultado, total, class_total = _build_resultado(avaliacao)
    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_sdq.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    comparativo_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av])
    dominios_comp = [
        {"nome": "Emocional",        "campo": "pont_emocional",          "max": 10},
        {"nome": "Conduta",          "campo": "pont_conduta",            "max": 10},
        {"nome": "Hiperatividade",   "campo": "pont_hiperatividade",     "max": 10},
        {"nome": "Pares",            "campo": "pont_pares",              "max": 10},
        {"nome": "Prossocial",       "campo": "pont_prossocial",         "max": 10},
        {"nome": "Total Dificul.",   "campo": "pont_total_dificuldades", "max": 40},
    ]
    cores_linha = ["#2E7D6B", "#3E73D1", "#E8793A", "#9B59B6", "#E8B84B", "#C0392B"]
    comparativo_datasets = []
    for i, dom in enumerate(dominios_comp):
        valores = [round((getattr(av, dom["campo"]) or 0) / dom["max"] * 100) for av in todas_av]
        comparativo_datasets.append({"label": dom["nome"], "data": valores, "borderColor": cores_linha[i], "backgroundColor": cores_linha[i] + "33", "tension": 0.3})

    return render(request, "questionario/avaliacoes/sdq_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "resultado": resultado,
        "total": total,
        "class_total": class_total,
        "comparativo_labels": comparativo_labels,
        "comparativo_datasets": json.dumps(comparativo_datasets),
        "tem_comparativo": len(todas_av) > 1,
        "outras_avaliacoes": outras,
    })


@login_required
def sdq_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoSDQ, uuid=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("sdq_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    pagina_dict = SDQ_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros_pagina = [n for n, _ in itens_pagina]

    respostas_qs = list(avaliacao.respostas.filter(numero_item__in=numeros_pagina))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas = {r.numero_item: r.observacao for r in respostas_qs}
    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": respostas_salvas.get(n),
         "observacao_salva": obs_salvas.get(n, "")}
        for n, t in itens_pagina
    ]
    ctx = _context_pagina(avaliacao, pagina_dict, pagina, itens_render, respostas_salvas, [])
    ctx["progresso"] = int(pagina / TOTAL_PAGINAS * 100)
    ctx["readonly"] = True
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def sdq_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSDQ, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "SDQ excluído com sucesso."})
        messages.success(request, "SDQ excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_sdq(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSDQ, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("sdq_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_sdq(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoSDQ, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    if not avaliacao.token:
        avaliacao.token = str(uuid.uuid4())
        avaliacao.save(update_fields=["token"])
    from django.template.loader import render_to_string
    link = request.build_absolute_uri(reverse("sdq_publico", kwargs={"token": avaliacao.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(
            subject="SDQ — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário SDQ no link: {link}",
            from_email=None,
            recipient_list=[email_dest],
            html_message=html,
            fail_silently=False,
        )
    except Exception as exc:
        if is_ajax:
            return JsonResponse({"ok": False, "message": f"Falha ao enviar e-mail: {exc}"})
        messages.error(request, f"Falha ao enviar e-mail: {exc}")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    avaliacao.email_enviado_em = tz.now()
    avaliacao.save(update_fields=["email_enviado_em"])
    if is_ajax:
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)


# ── View pública (token) ──────────────────────────────────────────────────────

def sdq_publico(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoSDQ, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("sdq_publico", token=token, pagina=1)

    pagina_dict = SDQ_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros_pagina = [n for n, _ in itens_pagina]

    respostas_qs = list(avaliacao.respostas.filter(numero_item__in=numeros_pagina))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas = {r.numero_item: r.observacao for r in respostas_qs}
    itens_faltando = []
    obs_render = {}

    if request.method == "POST":
        confirmar_incompleto = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_pagina_sdq(request, pagina_dict)
        obs_render = obs

        if erros and not confirmar_incompleto:
            resp_render = dict(respostas_salvas)
            resp_render.update(novas)
            respostas_salvas = resp_render
            itens_faltando = erros
        else:
            _salvar_respostas_sdq(avaliacao, novas, obs)
            proxima = pagina + 1
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular_sdq(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "sdq", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("sdq_publico", token=token, pagina=proxima)

    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": respostas_salvas.get(n),
         "observacao_salva": obs_render.get(n, obs_salvas.get(n, ""))}
        for n, t in itens_pagina
    ]
    ctx = _context_pagina(avaliacao, pagina_dict, pagina, itens_render, respostas_salvas, itens_faltando,
                          extra={"publico": True, "token": token})
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)
