from django.conf import settings
import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoBDI, RespostaBDI
from ..data.data_bdi import BDI_ITENS, BDI_SUBESCALAS, BDI_CORTE
from ..services import notificar_terapeuta
from ..tasks import enviar_email
from django.templatetags.static import static

# O BDI tem 1 "página" — todos os 21 itens de uma vez (com opções por item)
BDI_PAGINAS = [
    {"key": "total", "nome": "Inventário de Depressão de Beck", "cor": "#6C3483", "campo": "pont_total"},
]
TOTAL_PAGINAS = 1

_URL_NAMES = {
    "url_form_name": "bdi_form",
    "url_publico_name": "bdi_publico",
    "url_visualizar_name": "bdi_visualizar",
    "url_resultado_name": "bdi_resultado",
    "avaliacao_titulo": "BDI — Inventário de Depressão de Beck",
}


def _itens_da_pagina():
    return [(item["numero"], item["texto"]) for item in BDI_ITENS]


def _processar_post_bdi(request):
    valores_validos = {0, 1, 2, 3}
    erros, novas, obs = [], {}, {}
    for item in BDI_ITENS:
        numero = item["numero"]
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


def _salvar_respostas_bdi(avaliacao, novas, obs):
    for numero, valor in novas.items():
        RespostaBDI.objects.update_or_create(
            avaliacao=avaliacao, numero_item=numero,
            defaults={"valor": valor, "observacao": obs.get(numero, "")}
        )


def _calcular_bdi(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    total = sum(respostas.get(item["numero"], 0) for item in BDI_ITENS)
    avaliacao.pont_total = total
    return avaliacao


def _classificar(score, corte_list):
    for label, min_v, max_v in corte_list:
        if min_v <= score <= max_v:
            return label
    return corte_list[-1][0]


def _context_pagina(avaliacao, pagina_dict, pagina, itens_render, respostas_salvas, itens_faltando, extra=None):
    ctx = {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": pagina_dict,
        "itens": itens_render,
        "opcoes": None,  # BDI usa opcoes por item
        "itens_com_opcoes": True,  # sinaliza template para usar opcoes por item
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(1, BDI_PAGINAS[0]["nome"])],
        "pagina_anterior": None,
        "itens_faltando": itens_faltando,
    }
    if extra:
        ctx.update(extra)
    return ctx


@login_required
def nova_avaliacao_bdi(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('bdi'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo BDI.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoBDI.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("bdi_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def bdi_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoBDI, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("bdi_resultado", avaliacao_id=avaliacao_id)
    if pagina != 1:
        return redirect("bdi_form", avaliacao_id=avaliacao_id, pagina=1)

    pagina_dict = BDI_PAGINAS[0]
    numeros = [item["numero"] for item in BDI_ITENS]
    respostas_qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas = {r.numero_item: r.observacao for r in respostas_qs}
    itens_faltando = []
    obs_render = {}

    if request.method == "POST":
        confirmar_incompleto = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_bdi(request)
        obs_render = obs
        if erros and not confirmar_incompleto:
            resp_render = dict(respostas_salvas)
            resp_render.update(novas)
            respostas_salvas = resp_render
            itens_faltando = erros
        else:
            _salvar_respostas_bdi(avaliacao, novas, obs)
            avaliacao = _calcular_bdi(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            return redirect("bdi_resultado", avaliacao_id=avaliacao_id)

    itens_render = [
        {
            "numero": item["numero"], "texto": item["texto"],
            "opcoes": item["opcoes"],
            "resposta_salva": respostas_salvas.get(item["numero"]),
            "observacao_salva": obs_render.get(item["numero"], obs_salvas.get(item["numero"], "")),
        }
        for item in BDI_ITENS
    ]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _context_pagina(avaliacao, pagina_dict, pagina, itens_render, respostas_salvas, itens_faltando))


@login_required
def bdi_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBDI, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("bdi_form", avaliacao_id=avaliacao_id, pagina=1)
    total = avaliacao.pont_total or 0
    class_total = _classificar(total, BDI_CORTE["total"])
    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_bdi.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    comparativo_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av])
    comparativo_datasets = json.dumps([{
        "label": "BDI Total",
        "data": [av.pont_total or 0 for av in todas_av],
        "borderColor": "#6C3483",
        "backgroundColor": "#6C348333",
        "tension": 0.3,
    }])
    return render(request, "questionario/avaliacoes/bdi_resultado.html", {
        "avaliacao": avaliacao, "paciente": paciente,
        "total": total, "max_total": 63, "class_total": class_total,
        "corte": BDI_CORTE["total"],
        "comparativo_labels": comparativo_labels,
        "comparativo_datasets": comparativo_datasets,
        "tem_comparativo": len(todas_av) > 1,
        "outras_avaliacoes": outras,
    })


@login_required
def bdi_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoBDI, uuid=avaliacao_id, paciente__medico=request.user)
    pagina_dict = BDI_PAGINAS[0]
    numeros = [item["numero"] for item in BDI_ITENS]
    respostas_qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas = {r.numero_item: r.observacao for r in respostas_qs}
    itens_render = [
        {
            "numero": item["numero"], "texto": item["texto"],
            "opcoes": item["opcoes"],
            "resposta_salva": respostas_salvas.get(item["numero"]),
            "observacao_salva": obs_salvas.get(item["numero"], ""),
        }
        for item in BDI_ITENS
    ]
    ctx = _context_pagina(avaliacao, pagina_dict, 1, itens_render, respostas_salvas, [])
    ctx["progresso"] = 100
    ctx["readonly"] = True
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def bdi_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBDI, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "BDI excluído com sucesso."})
        messages.success(request, "BDI excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_bdi(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBDI, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("bdi_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_bdi(request, avaliacao_id):
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoBDI, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("bdi_publico", kwargs={"token": avaliacao.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        enviar_email.delay(
            subject="BDI — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário BDI no link: {link}",
            recipient_list=[email_dest], html_message=html, fail_silently=False,
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


def bdi_publico(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoBDI, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    pagina_dict = BDI_PAGINAS[0]
    numeros = [item["numero"] for item in BDI_ITENS]
    respostas_qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    respostas_salvas = {r.numero_item: r.valor for r in respostas_qs}
    obs_salvas = {r.numero_item: r.observacao for r in respostas_qs}
    itens_faltando = []
    obs_render = {}

    if request.method == "POST":
        confirmar_incompleto = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_bdi(request)
        obs_render = obs
        if erros and not confirmar_incompleto:
            resp_render = dict(respostas_salvas)
            resp_render.update(novas)
            respostas_salvas = resp_render
            itens_faltando = erros
        else:
            _salvar_respostas_bdi(avaliacao, novas, obs)
            avaliacao = _calcular_bdi(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            try:
                notificar_terapeuta(avaliacao.paciente, "bdi", request)
            except Exception:
                pass
            return render(request, "questionario/dashboard/concluido.html")

    itens_render = [
        {
            "numero": item["numero"], "texto": item["texto"],
            "opcoes": item["opcoes"],
            "resposta_salva": respostas_salvas.get(item["numero"]),
            "observacao_salva": obs_render.get(item["numero"], obs_salvas.get(item["numero"], "")),
        }
        for item in BDI_ITENS
    ]
    ctx = _context_pagina(avaliacao, pagina_dict, 1, itens_render, respostas_salvas, itens_faltando,
                          extra={"publico": True, "token": token})
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)
