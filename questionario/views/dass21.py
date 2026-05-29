import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoDASS21, RespostaDASS21
from ..data.data_dass21 import DASS21_ITENS, DASS21_SUBESCALAS, DASS21_OPCOES, DASS21_CORTE
from ..services import notificar_terapeuta

DASS21_PAGINAS = [
    {"key": "depressao", "nome": "Depressão",  "cor": "#2C3E50", "campo": "pont_depressao"},
    {"key": "ansiedade", "nome": "Ansiedade",  "cor": "#C0392B", "campo": "pont_ansiedade"},
    {"key": "estresse",  "nome": "Estresse",   "cor": "#E67E22", "campo": "pont_estresse"},
]
TOTAL_PAGINAS = 3

_URL_NAMES = {
    "url_form_name": "dass21_form", "url_publico_name": "dass21_publico",
    "url_visualizar_name": "dass21_visualizar", "url_resultado_name": "dass21_resultado",
    "avaliacao_titulo": "DASS-21",
}

_ITENS_POR_SUB = {
    key: [item for item in DASS21_ITENS if item["subescala"] == key]
    for key in DASS21_SUBESCALAS
}


def _itens_da_pagina(pagina_dict):
    return [(i["numero"], i["texto"]) for i in _ITENS_POR_SUB[pagina_dict["key"]]]


def _classificar(score, corte_list):
    for label, min_v, max_v in corte_list:
        if min_v <= score <= max_v:
            return label
    return corte_list[-1][0]


def _processar_post(request, pagina_dict):
    vals = {0, 1, 2, 3}
    erros, novas, obs = [], {}, {}
    for n, _ in _itens_da_pagina(pagina_dict):
        val = request.POST.get(f"item_{n}")
        if val is None:
            erros.append(n)
        else:
            try:
                v = int(val)
                (novas if v in vals else erros).append(n) if v not in vals else novas.update({n: v})
            except (ValueError, TypeError):
                erros.append(n)
        obs[n] = request.POST.get(f"obs_{n}", "").strip()
    return erros, novas, obs


def _processar_post_dass(request, pagina_dict):
    vals = {0, 1, 2, 3}
    erros, novas, obs = [], {}, {}
    for n, _ in _itens_da_pagina(pagina_dict):
        val = request.POST.get(f"item_{n}")
        if val is None:
            erros.append(n)
        else:
            try:
                v = int(val)
                if v in vals:
                    novas[n] = v
                else:
                    erros.append(n)
            except (ValueError, TypeError):
                erros.append(n)
        obs[n] = request.POST.get(f"obs_{n}", "").strip()
    return erros, novas, obs


def _salvar(avaliacao, novas, obs):
    for n, v in novas.items():
        RespostaDASS21.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n, defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    for key, sub in DASS21_SUBESCALAS.items():
        soma = sum(respostas.get(n, 0) for n in sub["itens"])
        setattr(avaliacao, sub["campo"], soma * 2)  # escalar para DASS-42 original
    return avaliacao


def _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando, extra=None):
    ctx = {
        **_URL_NAMES, "avaliacao": avaliacao, "paciente": avaliacao.paciente,
        "dominio": pagina_dict, "itens": itens_render, "opcoes": DASS21_OPCOES,
        "pagina": pagina, "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, DASS21_PAGINAS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando,
    }
    if extra:
        ctx.update(extra)
    return ctx


@login_required
def nova_avaliacao_dass21(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('dass21'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo DASS-21.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoDASS21.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("dass21_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def dass21_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoDASS21, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("dass21_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("dass21_form", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = DASS21_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros = [n for n, _ in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_dass(request, pagina_dict)
        obs_render = obs
        if erros and not confirmar:
            rs.update(novas)
            itens_faltando = erros
        else:
            _salvar(avaliacao, novas, obs)
            proxima = pagina + 1
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                return redirect("dass21_resultado", avaliacao_id=avaliacao_id)
            return redirect("dass21_form", avaliacao_id=avaliacao_id, pagina=proxima)
    itens_render = [{"numero": n, "texto": t, "resposta_salva": rs.get(n), "observacao_salva": obs_render.get(n, os_.get(n, ""))} for n, t in itens_pagina]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando))


@login_required
def dass21_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoDASS21, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("dass21_form", avaliacao_id=avaliacao_id, pagina=1)
    resultado = []
    for key, sub in DASS21_SUBESCALAS.items():
        score = getattr(avaliacao, sub["campo"]) or 0
        max_s = 42
        resultado.append({
            "key": key, "nome": sub["nome"], "cor": sub["cor"],
            "score": score, "max": max_s, "pct": int(score / max_s * 100),
            "classificacao": _classificar(score, DASS21_CORTE[key]),
        })
    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_dass21.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    return render(request, "questionario/avaliacoes/dass21_resultado.html", {
        "avaliacao": avaliacao, "paciente": paciente, "resultado": resultado,
        "comparativo_labels": json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av]),
        "comparativo_datasets": json.dumps([
            {"label": s["nome"], "data": [getattr(av, s["campo"]) or 0 for av in todas_av],
             "borderColor": s["cor"], "backgroundColor": s["cor"] + "33", "tension": 0.3}
            for s in DASS21_SUBESCALAS.values()
        ]),
        "tem_comparativo": len(todas_av) > 1, "outras_avaliacoes": outras,
    })


@login_required
def dass21_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoDASS21, uuid=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("dass21_visualizar", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = DASS21_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros = [n for n, _ in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_render = [{"numero": n, "texto": t, "resposta_salva": rs.get(n), "observacao_salva": os_.get(n, "")} for n, t in itens_pagina]
    ctx = _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, [])
    ctx["progresso"] = int(pagina / TOTAL_PAGINAS * 100)
    ctx["readonly"] = True
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def dass21_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoDASS21, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "DASS-21 excluído com sucesso."})
        messages.success(request, "DASS-21 excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_dass21(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoDASS21, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("dass21_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_dass21(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoDASS21, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado."})
        messages.error(request, "Nenhum e-mail cadastrado.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    if not avaliacao.token:
        avaliacao.token = str(uuid.uuid4())
        avaliacao.save(update_fields=["token"])
    from django.template.loader import render_to_string
    link = request.build_absolute_uri(reverse("dass21_publico", kwargs={"token": avaliacao.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(subject="DASS-21 — IntegraMente", message=f"Link: {link}", from_email=None, recipient_list=[email_dest], html_message=html, fail_silently=False)
    except Exception as exc:
        if is_ajax:
            return JsonResponse({"ok": False, "message": f"Falha: {exc}"})
        messages.error(request, f"Falha: {exc}")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    avaliacao.email_enviado_em = tz.now()
    avaliacao.save(update_fields=["email_enviado_em"])
    if is_ajax:
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)


def dass21_publico(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoDASS21, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("dass21_publico", token=token, pagina=1)
    pagina_dict = DASS21_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros = [n for n, _ in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_dass(request, pagina_dict)
        obs_render = obs
        if erros and not confirmar:
            rs.update(novas)
            itens_faltando = erros
        else:
            _salvar(avaliacao, novas, obs)
            proxima = pagina + 1
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "dass21", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("dass21_publico", token=token, pagina=proxima)
    itens_render = [{"numero": n, "texto": t, "resposta_salva": rs.get(n), "observacao_salva": obs_render.get(n, os_.get(n, ""))} for n, t in itens_pagina]
    ctx = _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando, extra={"publico": True, "token": token})
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)
