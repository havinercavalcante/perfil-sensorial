import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoAUQEI, RespostaAUQEI
from ..data.data_auqei import AUQEI_ITENS, AUQEI_SUBESCALAS, AUQEI_OPCOES, AUQEI_CORTE
from ..services import notificar_terapeuta

AUQEI_PAGINAS = [
    {"key": "familia",      "nome": "Família",             "cor": "#E74C3C", "campo": "pont_familia"},
    {"key": "lazer",        "nome": "Lazer",               "cor": "#27AE60", "campo": "pont_lazer"},
    {"key": "escola",       "nome": "Escola",              "cor": "#3498DB", "campo": "pont_escola"},
    {"key": "autonomia",    "nome": "Autonomia",            "cor": "#9B59B6", "campo": "pont_autonomia"},
    {"key": "funcoes",      "nome": "Funções Corporais",   "cor": "#E67E22", "campo": "pont_funcoes"},
    {"key": "amigos",       "nome": "Amigos",              "cor": "#F1C40F", "campo": "pont_amigos"},
    {"key": "independente", "nome": "Itens Independentes", "cor": "#1ABC9C", "campo": "pont_independente"},
]
TOTAL_PAGINAS = len(AUQEI_PAGINAS)

_ITENS_POR_SUB = {
    key: [i for i in AUQEI_ITENS if i["subescala"] == key]
    for key in AUQEI_SUBESCALAS
}

_URL_NAMES = {
    "url_form_name": "auqei_form",
    "url_publico_name": "auqei_publico",
    "url_resultado_name": "auqei_resultado",
    "url_visualizar_name": "auqei_visualizar",
    "avaliacao_titulo": "AUQEI — Qualidade de Vida Infantil",
}


def _classificar(score, corte_list):
    for label, min_v, max_v in corte_list:
        if min_v <= score <= max_v:
            return label
    return corte_list[-1][0]


def _processar_post(request, pagina_dict):
    vals = {1, 2, 3, 4}
    erros, novas, obs = [], {}, {}
    for item in _ITENS_POR_SUB[pagina_dict["key"]]:
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
        RespostaAUQEI.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n,
            defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    total = 0
    for key, sub in AUQEI_SUBESCALAS.items():
        itens_sub = sub["itens"]
        soma = sum(respostas.get(n, 0) for n in itens_sub)
        media = soma / len(itens_sub) if itens_sub else 0.0
        setattr(avaliacao, sub["campo"], round(media, 2))
        total += soma
    avaliacao.pont_total = total
    return avaliacao


def _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando, extra=None):
    ctx = {
        **_URL_NAMES, "avaliacao": avaliacao, "paciente": avaliacao.paciente,
        "dominio": pagina_dict, "itens": itens_render, "opcoes": AUQEI_OPCOES,
        "pagina": pagina, "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, AUQEI_PAGINAS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando,
    }
    if extra:
        ctx.update(extra)
    return ctx


@login_required
def nova_avaliacao_auqei(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('auqei'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo AUQEI.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoAUQEI.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("auqei_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def auqei_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoAUQEI, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("auqei_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("auqei_form", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = AUQEI_PAGINAS[pagina - 1]
    itens_pagina = _ITENS_POR_SUB[pagina_dict["key"]]
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post(request, pagina_dict)
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
                return redirect("auqei_resultado", avaliacao_id=avaliacao_id)
            return redirect("auqei_form", avaliacao_id=avaliacao_id, pagina=proxima)
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))} for i in itens_pagina]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando))


@login_required
def auqei_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAUQEI, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("auqei_form", avaliacao_id=avaliacao_id, pagina=1)
    resultado = []
    for key, sub in AUQEI_SUBESCALAS.items():
        score = getattr(avaliacao, sub["campo"]) or 0.0
        resultado.append({
            "key": key, "nome": sub["nome"], "cor": sub["cor"],
            "score": score, "max": 4.0, "pct": int(score / 4.0 * 100),
            "classificacao": "",
        })
    total = avaliacao.pont_total or 0
    class_total = _classificar(total, AUQEI_CORTE["total"])
    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_auqei.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    return render(request, "questionario/avaliacoes/auqei_resultado.html", {
        "avaliacao": avaliacao, "paciente": paciente, "resultado": resultado,
        "total": total, "class_total": class_total, "max_total": 104,
        "pct_total": int(total / 104 * 100),
        "comparativo_labels": json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av]),
        "comparativo_datasets": json.dumps([
            {"label": "Total", "data": [av.pont_total or 0 for av in todas_av],
             "borderColor": "#3498DB", "backgroundColor": "#3498DB33", "tension": 0.3}
        ]),
        "tem_comparativo": len(todas_av) > 1, "outras_avaliacoes": outras,
    })


@login_required
def auqei_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoAUQEI, uuid=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("auqei_visualizar", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = AUQEI_PAGINAS[pagina - 1]
    itens_pagina = _ITENS_POR_SUB[pagina_dict["key"]]
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": os_.get(i["numero"], "")} for i in itens_pagina]
    ctx = _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, [])
    ctx["progresso"] = int(pagina / TOTAL_PAGINAS * 100)
    ctx["readonly"] = True
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def auqei_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAUQEI, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "AUQEI excluído com sucesso."})
        messages.success(request, "AUQEI excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_auqei(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAUQEI, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("auqei_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_auqei(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoAUQEI, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("auqei_publico", kwargs={"token": avaliacao.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(subject="AUQEI — IntegraMente", message=f"Link: {link}", from_email=None, recipient_list=[email_dest], html_message=html, fail_silently=False)
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


def auqei_publico(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoAUQEI, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("auqei_publico", token=token, pagina=1)
    pagina_dict = AUQEI_PAGINAS[pagina - 1]
    itens_pagina = _ITENS_POR_SUB[pagina_dict["key"]]
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post(request, pagina_dict)
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
                    notificar_terapeuta(avaliacao.paciente, "auqei", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("auqei_publico", token=token, pagina=proxima)
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))} for i in itens_pagina]
    ctx = _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando, extra={"publico": True, "token": token})
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)
