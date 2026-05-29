import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoHAD, RespostaHAD
from ..data.data_had import HAD_ITENS, HAD_SUBESCALAS, HAD_CORTE
from ..services import notificar_terapeuta

HAD_PAGINAS = [
    {"key": "ansiedade", "nome": "Ansiedade (HAD)", "cor": "#C0392B", "campo": "pont_ansiedade"},
    {"key": "depressao", "nome": "Depressão (HAD)",  "cor": "#2C3E50", "campo": "pont_depressao"},
]
TOTAL_PAGINAS = 2

_URL_NAMES = {
    "url_form_name": "had_form", "url_publico_name": "had_publico",
    "url_visualizar_name": "had_visualizar", "url_resultado_name": "had_resultado",
    "avaliacao_titulo": "HAD — Escala Hospitalar de Ansiedade e Depressão",
}

_ITENS_POR_SUB = {
    key: [item for item in HAD_ITENS if item["subescala"] == key]
    for key in HAD_SUBESCALAS
}


def _itens_da_pagina(pagina_dict):
    return _ITENS_POR_SUB[pagina_dict["key"]]


def _classificar(score, corte_list):
    for label, min_v, max_v in corte_list:
        if min_v <= score <= max_v:
            return label
    return corte_list[-1][0]


def _processar_post_had(request, pagina_dict):
    erros, novas, obs = [], {}, {}
    for item in _itens_da_pagina(pagina_dict):
        n = item["numero"]
        val = request.POST.get(f"item_{n}")
        if val is None:
            erros.append(n)
        else:
            vals_validos = {o["valor"] for o in item["opcoes"]}
            try:
                v = int(val)
                if v in vals_validos:
                    novas[n] = v
                else:
                    erros.append(n)
            except (ValueError, TypeError):
                erros.append(n)
        obs[n] = request.POST.get(f"obs_{n}", "").strip()
    return erros, novas, obs


def _salvar_had(avaliacao, novas, obs):
    for n, v in novas.items():
        RespostaHAD.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n, defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular_had(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    for key, sub in HAD_SUBESCALAS.items():
        total = sum(respostas.get(n, 0) for n in sub["itens"])
        setattr(avaliacao, sub["campo"], total)
    return avaliacao


def _ctx_had(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando, extra=None):
    ctx = {
        **_URL_NAMES, "avaliacao": avaliacao, "paciente": avaliacao.paciente,
        "dominio": pagina_dict, "itens": itens_render,
        "opcoes": None,  # HAD tem opcoes por item
        "itens_com_opcoes_variaveis": True,
        "pagina": pagina, "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, HAD_PAGINAS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando,
    }
    if extra:
        ctx.update(extra)
    return ctx


@login_required
def nova_avaliacao_had(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('had'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo HAD.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoHAD.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("had_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def had_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoHAD, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("had_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("had_form", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = HAD_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_had(request, pagina_dict)
        obs_render = obs
        if erros and not confirmar:
            rs.update(novas)
            itens_faltando = erros
        else:
            _salvar_had(avaliacao, novas, obs)
            proxima = pagina + 1
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular_had(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                return redirect("had_resultado", avaliacao_id=avaliacao_id)
            return redirect("had_form", avaliacao_id=avaliacao_id, pagina=proxima)
    itens_render = [
        {"numero": i["numero"], "texto": i["texto"], "opcoes": i["opcoes"],
         "resposta_salva": rs.get(i["numero"]), "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))}
        for i in itens_pagina
    ]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx_had(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando))


@login_required
def had_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoHAD, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("had_form", avaliacao_id=avaliacao_id, pagina=1)
    resultado = []
    for key, sub in HAD_SUBESCALAS.items():
        score = getattr(avaliacao, sub["campo"]) or 0
        resultado.append({
            "key": key, "nome": sub["nome"], "cor": sub["cor"],
            "score": score, "max": 21, "pct": int(score / 21 * 100),
            "classificacao": _classificar(score, HAD_CORTE[key]),
        })
    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_had.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    return render(request, "questionario/avaliacoes/had_resultado.html", {
        "avaliacao": avaliacao, "paciente": paciente, "resultado": resultado,
        "comparativo_labels": json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av]),
        "comparativo_datasets": json.dumps([
            {"label": sub["nome"], "data": [getattr(av, sub["campo"]) or 0 for av in todas_av],
             "borderColor": sub["cor"], "backgroundColor": sub["cor"] + "33", "tension": 0.3}
            for sub in HAD_SUBESCALAS.values()
        ]),
        "tem_comparativo": len(todas_av) > 1, "outras_avaliacoes": outras,
    })


@login_required
def had_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoHAD, uuid=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("had_visualizar", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = HAD_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_render = [
        {"numero": i["numero"], "texto": i["texto"], "opcoes": i["opcoes"],
         "resposta_salva": rs.get(i["numero"]), "observacao_salva": os_.get(i["numero"], "")}
        for i in itens_pagina
    ]
    ctx = _ctx_had(avaliacao, pagina_dict, pagina, itens_render, rs, [])
    ctx["progresso"] = int(pagina / TOTAL_PAGINAS * 100)
    ctx["readonly"] = True
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def had_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoHAD, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "HAD excluído com sucesso."})
        messages.success(request, "HAD excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_had(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoHAD, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("had_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_had(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoHAD, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("had_publico", kwargs={"token": avaliacao.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(subject="HAD — IntegraMente", message=f"Link: {link}", from_email=None, recipient_list=[email_dest], html_message=html, fail_silently=False)
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


def had_publico(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoHAD, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("had_publico", token=token, pagina=1)
    pagina_dict = HAD_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_had(request, pagina_dict)
        obs_render = obs
        if erros and not confirmar:
            rs.update(novas)
            itens_faltando = erros
        else:
            _salvar_had(avaliacao, novas, obs)
            proxima = pagina + 1
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular_had(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "had", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("had_publico", token=token, pagina=proxima)
    itens_render = [
        {"numero": i["numero"], "texto": i["texto"], "opcoes": i["opcoes"],
         "resposta_salva": rs.get(i["numero"]), "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))}
        for i in itens_pagina
    ]
    ctx = _ctx_had(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando, extra={"publico": True, "token": token})
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)
