import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoSNAPIV, RespostaSNAPIV
from ..data.data_snap_iv import SNAP_IV_ITENS, SNAP_IV_SUBESCALAS, SNAP_IV_OPCOES, SNAP_IV_CORTE
from ..services import notificar_terapeuta

# ── Paginação por subescala ───────────────────────────────────────────────────

SNAP_IV_PAGINAS = [
    {"key": "desatencao",     "nome": "Desatenção",                     "cor": "#3498DB", "campo": "media_desatencao"},
    {"key": "hiperatividade", "nome": "Hiperatividade / Impulsividade", "cor": "#E74C3C", "campo": "media_hiperatividade"},
    {"key": "tod",            "nome": "TOD (Opositivo Desafiador)",     "cor": "#E67E22", "campo": "media_tod"},
]

TOTAL_PAGINAS = len(SNAP_IV_PAGINAS)

_URL_NAMES = {
    "url_form_name": "snap_iv_form",
    "url_publico_name": "snap_iv_publico",
    "url_visualizar_name": "snap_iv_visualizar",
    "url_resultado_name": "snap_iv_resultado",
    "avaliacao_titulo": "SNAP-IV",
}

# Itens por subescala: key → lista de (numero, texto)
_ITENS_POR_SUBESCALA = {
    key: [(item["numero"], item["texto"]) for item in SNAP_IV_ITENS if item["subescala"] == key]
    for key in SNAP_IV_SUBESCALAS
}


def _itens_da_pagina(pagina_dict):
    return _ITENS_POR_SUBESCALA[pagina_dict["key"]]


def _processar_post_pagina_snap(request, pagina_dict):
    """Processa POST de uma página SNAP-IV. Retorna (erros, novas, obs)."""
    itens = _itens_da_pagina(pagina_dict)
    valores_validos = {0, 1, 2, 3}
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


def _salvar_respostas_snap(avaliacao, novas, obs):
    for numero, valor in novas.items():
        RespostaSNAPIV.objects.update_or_create(
            avaliacao=avaliacao, numero_item=numero,
            defaults={"valor": valor, "observacao": obs.get(numero, "")}
        )


def _context_pagina(avaliacao, pagina_dict, pagina, itens_render, respostas_salvas, itens_faltando, extra=None):
    ctx = {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": pagina_dict,
        "itens": itens_render,
        "opcoes": SNAP_IV_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, SNAP_IV_PAGINAS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando,
    }
    if extra:
        ctx.update(extra)
    return ctx


# ── Cálculo e resultado ───────────────────────────────────────────────────────

def _calcular_snap_iv(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    for key, sub in SNAP_IV_SUBESCALAS.items():
        itens = sub["itens"]
        valores = [respostas.get(n, 0) for n in itens]
        media = sum(valores) / len(itens)
        setattr(avaliacao, sub["campo"], round(media, 2))
    return avaliacao


def _build_resultado(avaliacao):
    resultado = []
    for key, sub in SNAP_IV_SUBESCALAS.items():
        media = getattr(avaliacao, sub["campo"]) or 0.0
        resultado.append({
            "key": key,
            "nome": sub["nome"],
            "cor": sub["cor"],
            "media": media,
            "significativo": media >= SNAP_IV_CORTE,
        })
    return resultado


# ── Views autenticadas ────────────────────────────────────────────────────────

@login_required
def nova_avaliacao_snap_iv(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('snap_iv'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo SNAP-IV.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    respondente = request.POST.get("respondente", "pais")
    if respondente not in ("pais", "professor"):
        respondente = "pais"
    av = AvaliacaoSNAPIV.objects.create(
        paciente=paciente, token=str(uuid.uuid4()), respondente=respondente
    )
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("snap_iv_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def snap_iv_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("snap_iv_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("snap_iv_form", avaliacao_id=avaliacao_id, pagina=1)

    pagina_dict = SNAP_IV_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros_pagina = [n for n, _ in itens_pagina]

    respostas_qs = list(avaliacao.respostas.filter(numero_item__in=numeros_pagina))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas = {r.numero_item: r.observacao for r in respostas_qs}
    itens_faltando = []
    obs_render = {}

    if request.method == "POST":
        confirmar_incompleto = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_pagina_snap(request, pagina_dict)
        obs_render = obs

        if erros and not confirmar_incompleto:
            resp_render = dict(respostas_salvas)
            resp_render.update(novas)
            respostas_salvas = resp_render
            itens_faltando = erros
        else:
            _salvar_respostas_snap(avaliacao, novas, obs)
            proxima = pagina + 1
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular_snap_iv(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                return redirect("snap_iv_resultado", avaliacao_id=avaliacao_id)
            return redirect("snap_iv_form", avaliacao_id=avaliacao_id, pagina=proxima)

    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": respostas_salvas.get(n),
         "observacao_salva": obs_render.get(n, obs_salvas.get(n, ""))}
        for n, t in itens_pagina
    ]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _context_pagina(avaliacao, pagina_dict, pagina, itens_render, respostas_salvas, itens_faltando))


@login_required
def snap_iv_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("snap_iv_form", avaliacao_id=avaliacao_id, pagina=1)
    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_snap_iv.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    comparativo_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av])
    dominios_comp = [
        {"nome": "Desatenção",     "campo": "media_desatencao",    "max": 3},
        {"nome": "Hiperatividade", "campo": "media_hiperatividade","max": 3},
        {"nome": "TOD",            "campo": "media_tod",           "max": 3},
    ]
    cores_linha = ["#2E7D6B", "#3E73D1", "#E8793A"]
    comparativo_datasets = []
    for i, dom in enumerate(dominios_comp):
        valores = [round((getattr(av, dom["campo"]) or 0) / dom["max"] * 100) for av in todas_av]
        comparativo_datasets.append({"label": dom["nome"], "data": valores, "borderColor": cores_linha[i], "backgroundColor": cores_linha[i] + "33", "tension": 0.3})

    return render(request, "questionario/avaliacoes/snap_iv_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "resultado": _build_resultado(avaliacao),
        "corte": SNAP_IV_CORTE,
        "comparativo_labels": comparativo_labels,
        "comparativo_datasets": json.dumps(comparativo_datasets),
        "tem_comparativo": len(todas_av) > 1,
        "outras_avaliacoes": outras,
    })


@login_required
def snap_iv_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, uuid=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("snap_iv_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    pagina_dict = SNAP_IV_PAGINAS[pagina - 1]
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
def snap_iv_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "SNAP-IV excluído com sucesso."})
        messages.success(request, "SNAP-IV excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_snap_iv(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("snap_iv_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_snap_iv(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("snap_iv_publico", kwargs={"token": avaliacao.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(
            subject="SNAP-IV — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário SNAP-IV no link: {link}",
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

def snap_iv_publico(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoSNAPIV, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("snap_iv_publico", token=token, pagina=1)

    pagina_dict = SNAP_IV_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros_pagina = [n for n, _ in itens_pagina]

    respostas_qs = list(avaliacao.respostas.filter(numero_item__in=numeros_pagina))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas = {r.numero_item: r.observacao for r in respostas_qs}
    itens_faltando = []
    obs_render = {}

    if request.method == "POST":
        confirmar_incompleto = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_pagina_snap(request, pagina_dict)
        obs_render = obs

        if erros and not confirmar_incompleto:
            resp_render = dict(respostas_salvas)
            resp_render.update(novas)
            respostas_salvas = resp_render
            itens_faltando = erros
        else:
            _salvar_respostas_snap(avaliacao, novas, obs)
            proxima = pagina + 1
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular_snap_iv(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "snap_iv", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("snap_iv_publico", token=token, pagina=proxima)

    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": respostas_salvas.get(n),
         "observacao_salva": obs_render.get(n, obs_salvas.get(n, ""))}
        for n, t in itens_pagina
    ]
    ctx = _context_pagina(avaliacao, pagina_dict, pagina, itens_render, respostas_salvas, itens_faltando,
                          extra={"publico": True, "token": token})
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)
