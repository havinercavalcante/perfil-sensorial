import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Paciente, AvaliacaoDenver, RespostaDenver
from ..data.data_denver import DENVER_ITENS, DENVER_DOMINIOS, DENVER_OPCOES

# 4 paginas — 1 por dominio
DENVER_PAGINAS = [
    {"key": "pessoal_social",  "nome": "Pessoal-Social",        "cor": "#E74C3C", "campo": "pont_pessoal_social"},
    {"key": "motor_fino",      "nome": "Motor Fino-Adaptativo", "cor": "#3498DB", "campo": "pont_motor_fino"},
    {"key": "linguagem",       "nome": "Linguagem",              "cor": "#27AE60", "campo": "pont_linguagem"},
    {"key": "motor_grosseiro", "nome": "Motor Grosseiro",        "cor": "#E67E22", "campo": "pont_motor_grosseiro"},
]
TOTAL_PAGINAS = 4

_URL_NAMES = {
    "url_form_name": "denver_form",
    "url_publico_name": "denver_publico",
    "url_visualizar_name": "denver_visualizar",
    "url_resultado_name": "denver_resultado",
    "avaliacao_titulo": "Checklist Denver II — Desenvolvimento",
}

_ITENS_POR_DOM = {
    key: [i for i in DENVER_ITENS if i["dominio"] == key]
    for key in DENVER_DOMINIOS
}


def _itens_da_pagina(pagina_dict):
    return _ITENS_POR_DOM[pagina_dict["key"]]


def _processar_post_denver(request, pagina_dict):
    """
    Para o Denver, o valor pode ser 1, 0, ou None (NT).
    Retorna (erros, novas, obs) onde novas[numero] = valor (int ou None).
    """
    erros, novas, obs = [], {}, {}
    for item in _itens_da_pagina(pagina_dict):
        numero = item["numero"]
        val = request.POST.get(f"item_{numero}")
        if val is None:
            erros.append(numero)
        elif val == "None" or val == "":
            novas[numero] = None  # NT
        else:
            try:
                v = int(val)
                if v in (0, 1):
                    novas[numero] = v
                else:
                    erros.append(numero)
            except (ValueError, TypeError):
                erros.append(numero)
        obs[numero] = request.POST.get(f"obs_{numero}", "").strip()
    return erros, novas, obs


def _salvar_denver(avaliacao, novas, obs):
    for numero, valor in novas.items():
        RespostaDenver.objects.update_or_create(
            avaliacao=avaliacao, numero_item=numero,
            defaults={"valor": valor, "observacao": obs.get(numero, "")}
        )


def _calcular_denver(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    for key, dom in DENVER_DOMINIOS.items():
        itens = _ITENS_POR_DOM[key]
        # Conta apenas itens que Passam (valor == 1)
        passa = sum(1 for i in itens if respostas.get(i["numero"]) == 1)
        setattr(avaliacao, dom["campo"], passa)
    return avaliacao


def _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando, extra=None):
    ctx = {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": pagina_dict,
        "itens": itens_render,
        "opcoes": DENVER_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, DENVER_PAGINAS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando,
        "denver_modo": True,  # sinaliza template que valor pode ser None (NT)
    }
    if extra:
        ctx.update(extra)
    return ctx


@login_required
def nova_avaliacao_denver(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('denver'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo Denver II.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoDenver.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("detalhe_paciente", paciente_id=paciente_id)


@login_required
def denver_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoDenver, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("denver_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("denver_form", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = DENVER_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}

    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_denver(request, pagina_dict)
        obs_render = obs
        if erros and not confirmar:
            rs.update(novas)
            itens_faltando = erros
        else:
            _salvar_denver(avaliacao, novas, obs)
            proxima = pagina + 1
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular_denver(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                return redirect("denver_resultado", avaliacao_id=avaliacao_id)
            return redirect("denver_form", avaliacao_id=avaliacao_id, pagina=proxima)

    itens_render = [
        {
            "numero": i["numero"], "texto": i["texto"], "faixa": i.get("faixa", ""),
            "resposta_salva": rs.get(i["numero"], "__unset__"),
            "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], "")),
        }
        for i in itens_pagina
    ]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando))


@login_required
def denver_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoDenver, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("denver_form", avaliacao_id=avaliacao_id, pagina=1)

    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    resultado = []
    for key, dom in DENVER_DOMINIOS.items():
        itens = _ITENS_POR_DOM[key]
        total_itens = len(itens)
        passa = getattr(avaliacao, dom["campo"]) or 0
        respondidos = {i["numero"] for i in itens if i["numero"] in respostas}
        nt = sum(1 for n in respondidos if respostas[n] is None)
        falha = sum(1 for n in respondidos if respostas[n] == 0)
        nao_respondidos = total_itens - len(respondidos)
        pct_passa = int(passa / total_itens * 100) if total_itens else 0
        # Item breakdown for this domain
        itens_detail = [
            {
                "numero": i["numero"],
                "texto": i["texto"],
                "faixa": i.get("faixa", ""),
                "respondido": i["numero"] in respostas,
                "valor": respostas.get(i["numero"]),  # 1=Passou, 0=Falhou, None=NT
            }
            for i in itens
        ]
        resultado.append({
            "key": key,
            "nome": dom["nome"],
            "cor": dom["cor"],
            "passa": passa,
            "falha": falha,
            "nt": nt,
            "nao_respondidos": nao_respondidos,
            "total": total_itens,
            "pct": pct_passa,
            "itens": itens_detail,
        })

    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_denver.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]

    radar_data = json.dumps({
        "labels": [r["nome"] for r in resultado],
        "datasets": [{
            "label": "Marcos atingidos (%)",
            "data": [r["pct"] for r in resultado],
            "backgroundColor": "rgba(52,152,219,.25)",
            "borderColor": "#3498DB",
            "borderWidth": 2,
            "pointBackgroundColor": [r["cor"] for r in resultado],
        }]
    })

    return render(request, "questionario/avaliacoes/denver_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "resultado": resultado,
        "outras_avaliacoes": outras,
        "radar_data": radar_data,
        "comparativo_labels": json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av]),
        "comparativo_datasets": json.dumps([
            {
                "label": dom["nome"],
                "data": [getattr(av, dom["campo"]) or 0 for av in todas_av],
                "borderColor": dom["cor"],
                "backgroundColor": dom["cor"] + "33",
                "tension": 0.3,
            }
            for dom in DENVER_DOMINIOS.values()
        ]),
        "tem_comparativo": len(todas_av) > 1,
    })


@login_required
def denver_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoDenver, uuid=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("denver_visualizar", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = DENVER_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_render = [
        {
            "numero": i["numero"], "texto": i["texto"], "faixa": i.get("faixa", ""),
            "resposta_salva": rs.get(i["numero"], "__unset__"),
            "observacao_salva": os_.get(i["numero"], ""),
        }
        for i in itens_pagina
    ]
    ctx = _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, [])
    ctx["progresso"] = int(pagina / TOTAL_PAGINAS * 100)
    ctx["readonly"] = True
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def denver_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoDenver, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Denver II excluído com sucesso."})
        messages.success(request, "Denver II excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_denver(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoDenver, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("denver_resultado", avaliacao_id=avaliacao_id)


def denver_publico(request, token, pagina):
    from ..services import notificar_terapeuta
    avaliacao = get_object_or_404(AvaliacaoDenver, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("denver_publico", token=token, pagina=1)
    pagina_dict = DENVER_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros = [i["numero"] for i in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}

    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_denver(request, pagina_dict)
        obs_render = obs
        if erros and not confirmar:
            rs.update({n: v for n, v in novas.items() if v is not None})
            itens_faltando = erros
        else:
            _salvar_denver(avaliacao, novas, obs)
            proxima = pagina + 1
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular_denver(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "denver", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("denver_publico", token=token, pagina=proxima)

    itens_render = [
        {
            "numero": i["numero"], "texto": i["texto"], "faixa": i.get("faixa", ""),
            "resposta_salva": rs.get(i["numero"], "__unset__"),
            "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], "")),
        }
        for i in itens_pagina
    ]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando))


@login_required
def enviar_email_denver(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    from django.urls import reverse
    from django.template.loader import render_to_string
    avaliacao = get_object_or_404(AvaliacaoDenver, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(
        reverse("denver_publico", kwargs={"token": avaliacao.token, "pagina": 1})
    )
    html = render_to_string(
        "questionario/emails/email_link_avaliacao.html",
        {"paciente": paciente, "link": link}
    )
    try:
        send_mail(
            subject="Checklist Denver II — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário no link: {link}",
            from_email=None, recipient_list=[email_dest], html_message=html, fail_silently=False,
        )
    except Exception as exc:
        if is_ajax:
            return JsonResponse({"ok": False, "message": f"Falha ao enviar e-mail: {exc}"})
        messages.error(request, f"Falha: {exc}")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    avaliacao.email_enviado_em = tz.now()
    avaliacao.save(update_fields=["email_enviado_em"])
    if is_ajax:
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)
