import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoECA, RespostaECA
from ..data.data_eca import ECA_ITENS, ECA_OPCOES, ECA_SUBESCALAS
from ..services import notificar_terapeuta
from ..tasks import enviar_email

_COR   = "#27AE60"
_TITULO = "ECA — Escala de Avaliação do Comportamento Alimentar"
_URL_NAMES = {
    "url_form_name":       "eca_form",
    "url_publico_name":    "eca_publico",
    "url_visualizar_name": "eca_visualizar",
    "url_resultado_name":  "eca_resultado",
    "avaliacao_titulo":    _TITULO,
}

# Paginação por subescalas agrupadas
ECA_PAGINAS = [
    {
        "key": "parte1",
        "nome": "Mastigação e Seletividade Alimentar",
        "cor": _COR, "campo": "pont_mastigacao",
        # mastigação 1-6 + seletividade 7-17
        "itens": list(range(1, 18)),
    },
    {
        "key": "parte2",
        "nome": "Seletividade e Aspectos Comportamentais",
        "cor": _COR, "campo": "pont_seletividade",
        # seletividade 18-23 + comportamental 24-33 + 35
        "itens": list(range(18, 34)) + [35],
    },
    {
        "key": "parte3",
        "nome": "Sintomas Gastrointestinais, Sensorial e Habilidades",
        "cor": _COR, "campo": "pont_gi",
        # gi 36-42 + sensorial 43-47 + habilidades 48-51
        "itens": list(range(36, 52)),
    },
]
TOTAL_PAGINAS = len(ECA_PAGINAS)

_ITENS_MAP = {n: t for n, t in ECA_ITENS}


def _itens_render_pagina(pagina_dict, respostas_salvas, obs_salvas, obs_render):
    return [
        {
            "numero": n,
            "texto": _ITENS_MAP[n],
            "opcoes": ECA_OPCOES,
            "resposta_salva": respostas_salvas.get(n),
            "observacao_salva": obs_render.get(n, obs_salvas.get(n, "")),
        }
        for n in pagina_dict["itens"]
        if n in _ITENS_MAP
    ]


def _itens_render_todos(respostas_salvas, obs_salvas, obs_render):
    return [
        {
            "numero": n, "texto": t,
            "opcoes": ECA_OPCOES,
            "resposta_salva": respostas_salvas.get(n),
            "observacao_salva": obs_render.get(n, obs_salvas.get(n, "")),
        }
        for n, t in ECA_ITENS
    ]


def _processar_pagina(request, pagina_dict):
    erros, novas, obs = [], {}, {}
    for n in pagina_dict["itens"]:
        if n not in _ITENS_MAP:
            continue
        val = request.POST.get(f"item_{n}")
        if val is None:
            erros.append(n)
        else:
            try:
                v = int(val)
                if 1 <= v <= 5:
                    novas[n] = v
                else:
                    erros.append(n)
            except (ValueError, TypeError):
                erros.append(n)
        obs[n] = request.POST.get(f"obs_{n}", "").strip()
    return erros, novas, obs


def _salvar(avaliacao, novas, obs):
    for n, v in novas.items():
        RespostaECA.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n,
            defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    avaliacao.pont_mastigacao     = sum(respostas.get(i, 0) for i in ECA_SUBESCALAS["mastigacao"]["itens"])
    avaliacao.pont_seletividade   = sum(respostas.get(i, 0) for i in ECA_SUBESCALAS["seletividade"]["itens"])
    avaliacao.pont_comportamental = sum(respostas.get(i, 0) for i in ECA_SUBESCALAS["comportamental"]["itens"])
    avaliacao.pont_gi             = sum(respostas.get(i, 0) for i in ECA_SUBESCALAS["gi"]["itens"])
    avaliacao.pont_sensorial      = sum(respostas.get(i, 0) for i in ECA_SUBESCALAS["sensorial"]["itens"])
    avaliacao.pont_habilidades    = sum(respostas.get(i, 0) for i in ECA_SUBESCALAS["habilidades"]["itens"])
    return avaliacao


def _ctx(avaliacao, pagina_dict, pagina, itens, faltando, readonly=False, publico=False, token=None):
    ctx = {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": pagina_dict,
        "itens": itens,
        "opcoes": ECA_OPCOES,
        "itens_com_opcoes": True,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, ECA_PAGINAS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": faltando,
        "readonly": readonly,
        "publico": publico,
    }
    if token:
        ctx["token"] = token
    return ctx


@login_required
def nova_avaliacao_eca(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not request.user.perfil.tem_acesso("eca"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo ECA.")
        return redirect("detalhe_paciente", paciente_id=paciente_id)
    av = AvaliacaoECA.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("eca_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def eca_form(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoECA, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status == "concluida":
        return redirect("eca_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("eca_form", avaliacao_id=avaliacao_id, pagina=1)

    pagina_dict = ECA_PAGINAS[pagina - 1]
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
                return redirect("eca_resultado", avaliacao_id=avaliacao_id)
            return redirect("eca_form", avaliacao_id=avaliacao_id, pagina=proxima)

    itens = _itens_render_pagina(pagina_dict, respostas_salvas, obs_salvas, obs_render)
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(av, pagina_dict, pagina, itens, faltando))


@login_required
def eca_resultado(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoECA, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status != "concluida":
        return redirect("eca_form", avaliacao_id=avaliacao_id, pagina=1)
    todas = list(av.paciente.avaliacoes_eca.filter(status="concluida").order_by("data"))
    outras = [a for a in todas if a.id != av.id]
    subescalas = [
        {"nome": info["nome"], "pont": getattr(av, f"pont_{key}", 0) or 0, "max": info["max"]}
        for key, info in ECA_SUBESCALAS.items()
    ]
    total_geral = sum(s["pont"] for s in subescalas)
    max_geral = sum(s["max"] for s in subescalas)
    return render(request, "questionario/avaliacoes/eca_resultado.html", {
        "avaliacao": av, "paciente": av.paciente,
        "subescalas": subescalas,
        "total_geral": total_geral, "max_geral": max_geral,
        "cor": _COR,
        "comparativo_labels": json.dumps([a.data.strftime("%d/%m/%Y") for a in todas]),
        "comparativo_datasets": json.dumps([{"label": "ECA (Total)", "data": [
            sum(filter(None, [a.pont_mastigacao, a.pont_seletividade, a.pont_comportamental,
                              a.pont_gi, a.pont_sensorial, a.pont_habilidades]))
            for a in todas], "borderColor": _COR, "backgroundColor": _COR + "33", "tension": 0.3}]),
        "tem_comparativo": len(todas) > 1, "outras_avaliacoes": outras,
    })


@login_required
def eca_visualizar(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoECA, uuid=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("eca_visualizar", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = ECA_PAGINAS[pagina - 1]
    qs = list(av.respostas.all())
    respostas = {r.numero_item: r.valor for r in qs}
    obs = {r.numero_item: r.observacao for r in qs}
    itens = _itens_render_pagina(pagina_dict, respostas, obs, {})
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(av, pagina_dict, pagina, itens, [], readonly=True))


@login_required
def eca_deletar(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoECA, uuid=avaliacao_id, paciente__medico=request.user)
    pid = av.paciente.uuid
    if request.method == "POST":
        av.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "ECA excluído com sucesso."})
    return redirect("detalhe_paciente", paciente_id=pid)


@login_required
def salvar_observacoes_eca(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoECA, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        av.observacoes = request.POST.get("observacoes", "").strip()
        av.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
    return redirect("eca_resultado", avaliacao_id=avaliacao_id)


def eca_publico(request, token, pagina):
    av = get_object_or_404(AvaliacaoECA, token=token)
    if av.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("eca_publico", token=token, pagina=1)

    pagina_dict = ECA_PAGINAS[pagina - 1]
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
                    notificar_terapeuta(av.paciente, "eca", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("eca_publico", token=token, pagina=proxima)

    itens = _itens_render_pagina(pagina_dict, respostas_salvas, obs_salvas, obs_render)
    ctx = _ctx(av, pagina_dict, pagina, itens, faltando, publico=True, token=token)
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def enviar_email_eca(request, avaliacao_id):
    from django.utils import timezone as tz
    from django.template.loader import render_to_string
    av = get_object_or_404(AvaliacaoECA, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("eca_publico", kwargs={"token": av.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        enviar_email.delay(subject="ECA — IntegraMente", message=f"Responda o questionário em: {link}",
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
