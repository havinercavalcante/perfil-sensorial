from django.conf import settings
import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Paciente, AvaliacaoQMPI, RespostaQMPI
from ..data.data_qmpi import QMPI_ITENS, QMPI_SUBESCALAS, QMPI_OPCOES, QMPI_CORTE
from ..tasks import enviar_email
from django.templatetags.static import static

QMPI_PAGINAS = [
    {"key": "ansiedade", "nome": "Ansiedade",        "cor": "#E74C3C", "campo": "pont_ansiedade"},
    {"key": "depressao", "nome": "Depressão",        "cor": "#9B59B6", "campo": "pont_depressao"},
    {"key": "tdah",      "nome": "TDAH/Atenção",     "cor": "#3498DB", "campo": "pont_tdah"},
    {"key": "conduta",   "nome": "Conduta/Oposição", "cor": "#E67E22", "campo": "pont_conduta"},
    {"key": "autismo",   "nome": "Sinais de TEA",    "cor": "#27AE60", "campo": "pont_autismo"},
]
TOTAL_PAGINAS = 5

_URL_NAMES = {
    "url_form_name": "qmpi_form",
    "url_publico_name": "qmpi_publico",
    "url_visualizar_name": "qmpi_visualizar",
    "url_resultado_name": "qmpi_resultado",
    "avaliacao_titulo": "QMPI — Morbidade Psiquiátrica Infantil",
}

_ITENS_POR_SUB = {
    key: [i for i in QMPI_ITENS if i["subescala"] == key]
    for key in QMPI_SUBESCALAS
}


def _itens_da_pagina(pagina_dict):
    return [(i["numero"], i["texto"]) for i in _ITENS_POR_SUB[pagina_dict["key"]]]


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
        RespostaQMPI.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n,
            defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    for key, sub in QMPI_SUBESCALAS.items():
        soma = sum(respostas.get(n, 0) for n in sub["itens"])
        setattr(avaliacao, sub["campo"], soma)
    return avaliacao


def _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando, extra=None):
    ctx = {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": pagina_dict,
        "itens": itens_render,
        "opcoes": QMPI_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, QMPI_PAGINAS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": itens_faltando,
    }
    if extra:
        ctx.update(extra)
    return ctx


@login_required
def nova_avaliacao_qmpi(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('qmpi'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo QMPI.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoQMPI.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("qmpi_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def qmpi_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoQMPI, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("qmpi_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("qmpi_form", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = QMPI_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros = [n for n, _ in itens_pagina]
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
                return redirect("qmpi_resultado", avaliacao_id=avaliacao_id)
            return redirect("qmpi_form", avaliacao_id=avaliacao_id, pagina=proxima)

    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": rs.get(n),
         "observacao_salva": obs_render.get(n, os_.get(n, ""))}
        for n, t in itens_pagina
    ]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando))


@login_required
def qmpi_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoQMPI, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("qmpi_form", avaliacao_id=avaliacao_id, pagina=1)

    resultado = []
    for key, sub in QMPI_SUBESCALAS.items():
        score = getattr(avaliacao, sub["campo"]) or 0
        max_s = len(sub["itens"]) * 3
        resultado.append({
            "key": key, "nome": sub["nome"], "cor": sub["cor"],
            "score": score, "max": max_s,
            "pct": int(score / max_s * 100) if max_s else 0,
            "positivo": score >= QMPI_CORTE,
        })

    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_qmpi.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]

    return render(request, "questionario/avaliacoes/qmpi_resultado.html", {
        "avaliacao": avaliacao, "paciente": paciente,
        "resultado": resultado, "corte": QMPI_CORTE,
        "outras_avaliacoes": outras,
        "comparativo_labels": json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av]),
        "comparativo_datasets": json.dumps([
            {"label": sub["nome"], "data": [getattr(av, sub["campo"]) or 0 for av in todas_av],
             "borderColor": sub["cor"], "backgroundColor": sub["cor"] + "33", "tension": 0.3}
            for sub in QMPI_SUBESCALAS.values()
        ]),
        "tem_comparativo": len(todas_av) > 1,
    })


@login_required
def qmpi_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoQMPI, uuid=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("qmpi_visualizar", avaliacao_id=avaliacao_id, pagina=1)
    pagina_dict = QMPI_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros = [n for n, _ in itens_pagina]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": rs.get(n), "observacao_salva": os_.get(n, "")}
        for n, t in itens_pagina
    ]
    ctx = _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, [])
    ctx["progresso"] = int(pagina / TOTAL_PAGINAS * 100)
    ctx["readonly"] = True
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def qmpi_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoQMPI, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "QMPI excluído com sucesso."})
        messages.success(request, "QMPI excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_qmpi(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoQMPI, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("qmpi_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_qmpi(request, avaliacao_id):
    from django.utils import timezone as tz
    from django.urls import reverse
    avaliacao = get_object_or_404(AvaliacaoQMPI, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("qmpi_publico", kwargs={"token": avaliacao.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        enviar_email.delay(subject="QMPI — IntegraMente", message=f"Link: {link}",
            recipient_list=[email_dest], html_message=html, fail_silently=False)
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


def qmpi_publico(request, token, pagina):
    from ..services import notificar_terapeuta
    avaliacao = get_object_or_404(AvaliacaoQMPI, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("qmpi_publico", token=token, pagina=1)
    pagina_dict = QMPI_PAGINAS[pagina - 1]
    itens_pagina = _itens_da_pagina(pagina_dict)
    numeros = [n for n, _ in itens_pagina]
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
                    notificar_terapeuta(avaliacao.paciente, "qmpi", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
            return redirect("qmpi_publico", token=token, pagina=proxima)

    itens_render = [
        {"numero": n, "texto": t, "resposta_salva": rs.get(n),
         "observacao_salva": obs_render.get(n, os_.get(n, ""))}
        for n, t in itens_pagina
    ]
    ctx = _ctx(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando,
               extra={"publico": True, "token": token})
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)
