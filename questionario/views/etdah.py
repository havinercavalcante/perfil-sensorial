import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoETDAH, RespostaETDAH
from ..data.data_etdah import (
    ETDAH_ITENS_PAIS, ETDAH_ITENS_PROF,
    ETDAH_SUBESCALAS, ETDAH_OPCOES, ETDAH_CORTE,
)
from ..services import notificar_terapeuta

ETDAH_PAGINAS = [
    {"key": "desatencao", "nome": "Desatenção",                   "cor": "#3498DB", "campo": "pont_desatencao"},
    {"key": "hiperativ",  "nome": "Hiperatividade/Impulsividade", "cor": "#E74C3C", "campo": "pont_hiperativ"},
    {"key": "tod",        "nome": "TOD",                          "cor": "#E67E22", "campo": "pont_tod"},
]
TOTAL_PAGINAS = len(ETDAH_PAGINAS)


def _itens_por_respondente(respondente):
    return ETDAH_ITENS_PAIS if respondente == "pais" else ETDAH_ITENS_PROF


def _itens_por_sub(respondente):
    itens = _itens_por_respondente(respondente)
    return {key: [i for i in itens if i["subescala"] == key] for key in ETDAH_SUBESCALAS}


def _classificar(score, corte_list):
    for label, min_v, max_v in corte_list:
        if min_v <= score <= max_v:
            return label
    return corte_list[-1][0]


def _processar_post(request, pagina_dict, respondente):
    vals = {0, 1, 2, 3}
    erros, novas, obs = [], {}, {}
    for item in _itens_por_sub(respondente)[pagina_dict["key"]]:
        n = item["numero"]
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
        RespostaETDAH.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n,
            defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    total_soma = 0
    total_n = 0
    for key, sub in ETDAH_SUBESCALAS.items():
        itens_sub = sub["itens"]
        soma = sum(respostas.get(n, 0) for n in itens_sub)
        media = soma / len(itens_sub) if itens_sub else 0.0
        setattr(avaliacao, sub["campo"], round(media, 2))
        total_soma += soma
        total_n += len(itens_sub)
    avaliacao.pont_total = round(total_soma / total_n, 2) if total_n else 0.0
    return avaliacao


def _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando, url_form, url_publico, url_resultado, url_visualizar, extra=None):
    ctx = {
        "url_form_name": url_form,
        "url_publico_name": url_publico,
        "url_resultado_name": url_resultado,
        "url_visualizar_name": url_visualizar,
        "avaliacao_titulo": f"ETDAH — {'Pais' if avaliacao.respondente == 'pais' else 'Professor'}",
        "avaliacao": avaliacao, "paciente": avaliacao.paciente,
        "dominio": pagina_dict, "itens": itens_render, "opcoes": ETDAH_OPCOES,
        "pagina": pagina, "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, ETDAH_PAGINAS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando,
    }
    if extra:
        ctx.update(extra)
    return ctx


# ─── PAIS ─────────────────────────────────────────────────────────────────────

@login_required
def nova_avaliacao_etdah_pais(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('etdah_pais'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo ETDAH (Pais).")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoETDAH.objects.create(paciente=paciente, respondente="pais", token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("etdah_pais_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def etdah_pais_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoETDAH, uuid=avaliacao_id, paciente__medico=request.user, respondente="pais")
    if avaliacao.status == "concluida":
        return redirect("etdah_pais_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("etdah_pais_form", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = ETDAH_PAGINAS[pagina - 1]
    itens_pagina = _itens_por_sub("pais")[pagina_dict["key"]]
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post(request, pagina_dict, "pais")
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
                return redirect("etdah_pais_resultado", avaliacao_id=avaliacao_id)
            return redirect("etdah_pais_form", avaliacao_id=avaliacao_id, pagina=proxima)
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))} for i in itens_pagina]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando,
                       "etdah_pais_form", "etdah_pais_publico", "etdah_pais_resultado", "etdah_pais_visualizar"))


@login_required
def etdah_pais_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoETDAH, uuid=avaliacao_id, paciente__medico=request.user, respondente="pais")
    if avaliacao.status != "concluida":
        return redirect("etdah_pais_form", avaliacao_id=avaliacao_id, pagina=1)
    resultado = []
    for key, sub in ETDAH_SUBESCALAS.items():
        score = getattr(avaliacao, sub["campo"]) or 0.0
        resultado.append({
            "key": key, "nome": sub["nome"], "cor": sub["cor"],
            "score": score, "max": 3.0, "pct": int(score / 3.0 * 100),
            "classificacao": _classificar(int(score * len(sub["itens"])), ETDAH_CORTE.get(key, [("Normal", 0, 9999)])),
        })
    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_etdah.filter(status="concluida", respondente="pais").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    return render(request, "questionario/avaliacoes/etdah_resultado.html", {
        "avaliacao": avaliacao, "paciente": paciente, "resultado": resultado,
        "pont_total": avaliacao.pont_total or 0,
        "tipo_label": "Pais",
        "comparativo_labels": json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av]),
        "comparativo_datasets": json.dumps([
            {"label": s["nome"], "data": [getattr(av, s["campo"]) or 0 for av in todas_av],
             "borderColor": s["cor"], "backgroundColor": s["cor"] + "33", "tension": 0.3}
            for s in ETDAH_SUBESCALAS.values()
        ]),
        "tem_comparativo": len(todas_av) > 1, "outras_avaliacoes": outras,
        "url_resultado_name": "etdah_pais_resultado",
        "url_laudo_name": "etdah_pais_laudo",
        "url_deletar_name": "etdah_pais_deletar",
        "url_observacoes_name": "salvar_observacoes_etdah_pais",
    })


@login_required
def etdah_pais_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoETDAH, uuid=avaliacao_id, paciente__medico=request.user, respondente="pais")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("etdah_pais_visualizar", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = ETDAH_PAGINAS[pagina - 1]
    itens_pagina = _itens_por_sub("pais")[pagina_dict["key"]]
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": os_.get(i["numero"], "")} for i in itens_pagina]
    ctx = _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, [],
               "etdah_pais_form", "etdah_pais_publico", "etdah_pais_resultado", "etdah_pais_visualizar")
    ctx["progresso"] = int(pagina / TOTAL_PAGINAS * 100)
    ctx["readonly"] = True
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def etdah_pais_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoETDAH, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "ETDAH excluído com sucesso."})
        messages.success(request, "ETDAH excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_etdah_pais(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoETDAH, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("etdah_pais_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_etdah_pais(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoETDAH, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("etdah_pais_publico", kwargs={"token": avaliacao.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(subject="ETDAH — IntegraMente", message=f"Link: {link}", from_email=None, recipient_list=[email_dest], html_message=html, fail_silently=False)
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


def etdah_pais_publico(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoETDAH, token=token, respondente="pais")
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("etdah_pais_publico", token=token, pagina=1)
    pagina_dict = ETDAH_PAGINAS[pagina - 1]
    itens_pagina = _itens_por_sub("pais")[pagina_dict["key"]]
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post(request, pagina_dict, "pais")
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
                    notificar_terapeuta(avaliacao.paciente, "etdah_pais", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("etdah_pais_publico", token=token, pagina=proxima)
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))} for i in itens_pagina]
    ctx = _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando,
               "etdah_pais_form", "etdah_pais_publico", "etdah_pais_resultado", "etdah_pais_visualizar",
               extra={"publico": True, "token": token})
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


# ─── PROFESSOR ────────────────────────────────────────────────────────────────

@login_required
def nova_avaliacao_etdah_prof(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('etdah_prof'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo ETDAH (Professor).")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoETDAH.objects.create(paciente=paciente, respondente="professor", token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("etdah_prof_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def etdah_prof_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoETDAH, uuid=avaliacao_id, paciente__medico=request.user, respondente="professor")
    if avaliacao.status == "concluida":
        return redirect("etdah_prof_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("etdah_prof_form", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = ETDAH_PAGINAS[pagina - 1]
    itens_pagina = _itens_por_sub("professor")[pagina_dict["key"]]
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post(request, pagina_dict, "professor")
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
                return redirect("etdah_prof_resultado", avaliacao_id=avaliacao_id)
            return redirect("etdah_prof_form", avaliacao_id=avaliacao_id, pagina=proxima)
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))} for i in itens_pagina]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando,
                       "etdah_prof_form", "etdah_prof_publico", "etdah_prof_resultado", "etdah_prof_visualizar"))


@login_required
def etdah_prof_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoETDAH, uuid=avaliacao_id, paciente__medico=request.user, respondente="professor")
    if avaliacao.status != "concluida":
        return redirect("etdah_prof_form", avaliacao_id=avaliacao_id, pagina=1)
    resultado = []
    for key, sub in ETDAH_SUBESCALAS.items():
        score = getattr(avaliacao, sub["campo"]) or 0.0
        resultado.append({
            "key": key, "nome": sub["nome"], "cor": sub["cor"],
            "score": score, "max": 3.0, "pct": int(score / 3.0 * 100),
            "classificacao": _classificar(int(score * len(sub["itens"])), ETDAH_CORTE.get(key, [("Normal", 0, 9999)])),
        })
    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_etdah.filter(status="concluida", respondente="professor").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    return render(request, "questionario/avaliacoes/etdah_resultado.html", {
        "avaliacao": avaliacao, "paciente": paciente, "resultado": resultado,
        "pont_total": avaliacao.pont_total or 0,
        "tipo_label": "Professor",
        "comparativo_labels": json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av]),
        "comparativo_datasets": json.dumps([
            {"label": s["nome"], "data": [getattr(av, s["campo"]) or 0 for av in todas_av],
             "borderColor": s["cor"], "backgroundColor": s["cor"] + "33", "tension": 0.3}
            for s in ETDAH_SUBESCALAS.values()
        ]),
        "tem_comparativo": len(todas_av) > 1, "outras_avaliacoes": outras,
        "url_resultado_name": "etdah_prof_resultado",
        "url_laudo_name": "etdah_prof_laudo",
        "url_deletar_name": "etdah_prof_deletar",
        "url_observacoes_name": "salvar_observacoes_etdah_prof",
    })


@login_required
def etdah_prof_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoETDAH, uuid=avaliacao_id, paciente__medico=request.user, respondente="professor")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("etdah_prof_visualizar", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = ETDAH_PAGINAS[pagina - 1]
    itens_pagina = _itens_por_sub("professor")[pagina_dict["key"]]
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": os_.get(i["numero"], "")} for i in itens_pagina]
    ctx = _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, [],
               "etdah_prof_form", "etdah_prof_publico", "etdah_prof_resultado", "etdah_prof_visualizar")
    ctx["progresso"] = int(pagina / TOTAL_PAGINAS * 100)
    ctx["readonly"] = True
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def etdah_prof_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoETDAH, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "ETDAH excluído com sucesso."})
        messages.success(request, "ETDAH excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_etdah_prof(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoETDAH, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("etdah_prof_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_etdah_prof(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoETDAH, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("etdah_prof_publico", kwargs={"token": avaliacao.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(subject="ETDAH — IntegraMente", message=f"Link: {link}", from_email=None, recipient_list=[email_dest], html_message=html, fail_silently=False)
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


def etdah_prof_publico(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoETDAH, token=token, respondente="professor")
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("etdah_prof_publico", token=token, pagina=1)
    pagina_dict = ETDAH_PAGINAS[pagina - 1]
    itens_pagina = _itens_por_sub("professor")[pagina_dict["key"]]
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post(request, pagina_dict, "professor")
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
                    notificar_terapeuta(avaliacao.paciente, "etdah_prof", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("etdah_prof_publico", token=token, pagina=proxima)
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))} for i in itens_pagina]
    ctx = _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando,
               "etdah_prof_form", "etdah_prof_publico", "etdah_prof_resultado", "etdah_prof_visualizar",
               extra={"publico": True, "token": token})
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)
