from django.conf import settings
import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoTOD, RespostaTOD
from ..data.data_tod import TOD_ITENS, TOD_OPCOES, TOD_ITENS_CORTE, TOD_LIMIAR_CORTE, TOD_VALOR_CORTE
from ..services import notificar_terapeuta
from ..tasks import enviar_email
from django.templatetags.static import static

_COR    = "#C0392B"
_TITULO = "TOD — Escala de Avaliação de Comportamentos Disruptivos"

TOD_PAGINAS = [
    {"key": "parte1", "nome": "Parte 1 — Itens 1 a 15",  "cor": _COR, "campo": "pont_total", "itens": list(range(1,  16))},
    {"key": "parte2", "nome": "Parte 2 — Itens 16 a 30", "cor": _COR, "campo": "pont_total", "itens": list(range(16, 31))},
    {"key": "parte3", "nome": "Parte 3 — Itens 31 a 45", "cor": _COR, "campo": "pont_total", "itens": list(range(31, 46))},
]
TOTAL_PAGINAS = len(TOD_PAGINAS)

_ITENS_MAP = {n: t for n, t in TOD_ITENS}

_URL_NAMES = {
    "url_form_name":       "tod_form",
    "url_publico_name":    "tod_publico",
    "url_visualizar_name": "tod_visualizar",
    "url_resultado_name":  "tod_resultado",
    "avaliacao_titulo":    _TITULO,
}


def _itens_render_pagina(pagina_dict, respostas_salvas, obs_salvas, obs_render):
    return [
        {
            "numero": n,
            "texto": _ITENS_MAP[n],
            "opcoes": TOD_OPCOES,
            "resposta_salva": respostas_salvas.get(n),
            "observacao_salva": obs_render.get(n, obs_salvas.get(n, "")),
            "is_corte": n in TOD_ITENS_CORTE,
        }
        for n in pagina_dict["itens"]
    ]


def _itens_render_todos(respostas_salvas, obs_salvas, obs_render):
    return [
        {
            "numero": n, "texto": t,
            "opcoes": TOD_OPCOES,
            "resposta_salva": respostas_salvas.get(n),
            "observacao_salva": obs_render.get(n, obs_salvas.get(n, "")),
            "is_corte": n in TOD_ITENS_CORTE,
        }
        for n, t in TOD_ITENS
    ]


def _processar_pagina(request, pagina_dict):
    erros, novas, obs = [], {}, {}
    for n in pagina_dict["itens"]:
        val = request.POST.get(f"item_{n}")
        if val is None:
            erros.append(n)
        else:
            try:
                v = int(val)
                if 0 <= v <= 3:
                    novas[n] = v
                else:
                    erros.append(n)
            except (ValueError, TypeError):
                erros.append(n)
        obs[n] = request.POST.get(f"obs_{n}", "").strip()
    return erros, novas, obs


def _salvar(avaliacao, novas, obs):
    for n, v in novas.items():
        RespostaTOD.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n,
            defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    avaliacao.pont_total = sum(respostas.get(n, 0) for n, _ in TOD_ITENS)
    avaliacao.itens_corte_positivos = sum(
        1 for n in TOD_ITENS_CORTE if respostas.get(n, 0) >= TOD_VALOR_CORTE
    )
    return avaliacao


def _ctx(avaliacao, pagina_dict, pagina, itens, faltando, readonly=False, publico=False, token=None):
    ctx = {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": pagina_dict,
        "itens": itens,
        "opcoes": None,
        "itens_com_opcoes": True,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, TOD_PAGINAS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": faltando,
        "readonly": readonly,
        "publico": publico,
    }
    if token:
        ctx["token"] = token
    return ctx


@login_required
def nova_avaliacao_tod(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not request.user.perfil.tem_acesso("tod"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo TOD.")
        return redirect("detalhe_paciente", paciente_id=paciente_id)
    av = AvaliacaoTOD.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("tod_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def tod_form(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoTOD, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status == "concluida":
        return redirect("tod_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("tod_form", avaliacao_id=avaliacao_id, pagina=1)

    pagina_dict = TOD_PAGINAS[pagina - 1]
    qs = list(av.respostas.all())
    respostas_salvas = {r.numero_item: r.valor for r in qs}
    obs_salvas = {r.numero_item: r.observacao for r in qs}
    faltando, obs_render = [], {}

    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_pagina(request, pagina_dict)
        obs_render = obs
        if erros and not confirmar:
            respostas_salvas = {**respostas_salvas, **novas}
            faltando = erros
        else:
            _salvar(av, novas, obs)
            proxima = pagina + 1
            if proxima > TOTAL_PAGINAS:
                av = _calcular(av)
                av.status = "concluida"
                av.save()
                return redirect("tod_resultado", avaliacao_id=avaliacao_id)
            return redirect("tod_form", avaliacao_id=avaliacao_id, pagina=proxima)

    itens = _itens_render_pagina(pagina_dict, respostas_salvas, obs_salvas, obs_render)
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(av, pagina_dict, pagina, itens, faltando))


@login_required
def tod_resultado(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoTOD, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status != "concluida":
        return redirect("tod_form", avaliacao_id=avaliacao_id, pagina=1)
    todas = list(av.paciente.avaliacoes_tod.filter(status="concluida").order_by("data"))
    outras = [a for a in todas if a.id != av.id]
    itens_corte_positivos = av.itens_corte_positivos or 0
    positivo_tod = itens_corte_positivos >= TOD_LIMIAR_CORTE
    return render(request, "questionario/avaliacoes/tod_resultado.html", {
        "avaliacao": av, "paciente": av.paciente,
        "pont_total": av.pont_total or 0,
        "itens_corte_positivos": itens_corte_positivos,
        "positivo_tod": positivo_tod,
        "limiar_corte": TOD_LIMIAR_CORTE,
        "cor": _COR,
        "comparativo_labels": json.dumps([a.data.strftime("%d/%m/%Y") for a in todas]),
        "comparativo_datasets": json.dumps([{"label": "TOD (Total)", "data": [a.pont_total or 0 for a in todas], "borderColor": _COR, "backgroundColor": _COR + "33", "tension": 0.3}]),
        "tem_comparativo": len(todas) > 1, "outras_avaliacoes": outras,
    })


@login_required
def tod_visualizar(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoTOD, uuid=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        pagina = 1
    pagina_dict = TOD_PAGINAS[pagina - 1]
    qs = list(av.respostas.all())
    respostas = {r.numero_item: r.valor for r in qs}
    obs = {r.numero_item: r.observacao for r in qs}
    itens = _itens_render_pagina(pagina_dict, respostas, obs, {})
    ctx = _ctx(av, pagina_dict, pagina, itens, [], readonly=True)
    ctx["progresso"] = int(pagina / TOTAL_PAGINAS * 100)
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def tod_deletar(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoTOD, uuid=avaliacao_id, paciente__medico=request.user)
    pid = av.paciente.uuid
    if request.method == "POST":
        av.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "TOD excluído com sucesso."})
    return redirect("detalhe_paciente", paciente_id=pid)


@login_required
def salvar_observacoes_tod(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoTOD, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        av.observacoes = request.POST.get("observacoes", "").strip()
        av.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
    return redirect("tod_resultado", avaliacao_id=avaliacao_id)


def tod_publico(request, token, pagina):
    av = get_object_or_404(AvaliacaoTOD, token=token)
    if av.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("tod_publico", token=token, pagina=1)

    pagina_dict = TOD_PAGINAS[pagina - 1]
    qs = list(av.respostas.all())
    respostas_salvas = {r.numero_item: r.valor for r in qs}
    obs_salvas = {r.numero_item: r.observacao for r in qs}
    faltando, obs_render = [], {}

    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_pagina(request, pagina_dict)
        obs_render = obs
        if erros and not confirmar:
            respostas_salvas = {**respostas_salvas, **novas}
            faltando = erros
        else:
            _salvar(av, novas, obs)
            proxima = pagina + 1
            if proxima > TOTAL_PAGINAS:
                av = _calcular(av)
                av.status = "concluida"
                av.save()
                try:
                    notificar_terapeuta(av.paciente, "tod", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("tod_publico", token=token, pagina=proxima)

    itens = _itens_render_pagina(pagina_dict, respostas_salvas, obs_salvas, obs_render)
    ctx = _ctx(av, pagina_dict, pagina, itens, faltando, publico=True, token=token)
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def enviar_email_tod(request, avaliacao_id):
    from django.utils import timezone as tz
    from django.template.loader import render_to_string
    av = get_object_or_404(AvaliacaoTOD, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = av.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    if not av.token:
        av.token = str(uuid.uuid4())
        av.save(update_fields=["token"])
    link = request.build_absolute_uri(reverse("tod_publico", kwargs={"token": av.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        enviar_email.delay(subject="TOD — IntegraMente", message=f"Responda o questionário em: {link}",
            recipient_list=[email_dest], html_message=html, fail_silently=False)
    except Exception as exc:
        if is_ajax:
            return JsonResponse({"ok": False, "message": f"Falha: {exc}"})
        messages.error(request, f"Falha: {exc}")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    av.email_enviado_em = tz.now()
    av.save(update_fields=["email_enviado_em"])
    if is_ajax:
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)
