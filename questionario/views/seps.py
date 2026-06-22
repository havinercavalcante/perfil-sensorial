from django.conf import settings
import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoSEPS, RespostaSEPS
from ..data.data_seps import SEPS_ITENS, SEPS_OPCOES, SEPS_SUBESCALAS
from ..services import notificar_terapeuta
from ..tasks import enviar_email
from django.templatetags.static import static

_COR   = "#8E44AD"
_TITULO = "SEPS — Escala de Problemas Sensoriais na Alimentação"
_URL_NAMES = {
    "url_form_name":       "seps_form",
    "url_publico_name":    "seps_publico",
    "url_visualizar_name": "seps_visualizar",
    "url_resultado_name":  "seps_resultado",
    "avaliacao_titulo":    _TITULO,
}
_PAGINA_DICT = {"key": "total", "nome": _TITULO, "cor": _COR, "campo": "pont_aversao_toque"}


def _itens_render(respostas_salvas, obs_salvas, obs_render):
    return [
        {
            "numero": n, "texto": t,
            "opcoes": SEPS_OPCOES,
            "resposta_salva": respostas_salvas.get(n),
            "observacao_salva": obs_render.get(n, obs_salvas.get(n, "")),
        }
        for n, t in SEPS_ITENS
    ]


def _processar(request):
    erros, novas, obs = [], {}, {}
    for n, _ in SEPS_ITENS:
        val = request.POST.get(f"item_{n}")
        if val is None:
            erros.append(n)
        else:
            try:
                v = int(val)
                if 0 <= v <= 4:
                    novas[n] = v
                else:
                    erros.append(n)
            except (ValueError, TypeError):
                erros.append(n)
        obs[n] = request.POST.get(f"obs_{n}", "").strip()
    return erros, novas, obs


def _salvar(avaliacao, novas, obs):
    for n, v in novas.items():
        RespostaSEPS.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n,
            defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    avaliacao.pont_aversao_toque = sum(respostas.get(i, 0) for i in SEPS_SUBESCALAS["aversao_toque"]["itens"])
    avaliacao.pont_foco_unica    = sum(respostas.get(i, 0) for i in SEPS_SUBESCALAS["foco_unica"]["itens"])
    avaliacao.pont_vomito        = sum(respostas.get(i, 0) for i in SEPS_SUBESCALAS["vomito"]["itens"])
    avaliacao.pont_sensib_temp   = sum(respostas.get(i, 0) for i in SEPS_SUBESCALAS["sensib_temp"]["itens"])
    avaliacao.pont_expulsao      = sum(respostas.get(i, 0) for i in SEPS_SUBESCALAS["expulsao"]["itens"])
    avaliacao.pont_encher        = sum(respostas.get(i, 0) for i in SEPS_SUBESCALAS["encher"]["itens"])
    return avaliacao


def _ctx(avaliacao, itens, faltando, readonly=False, publico=False, token=None):
    ctx = {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": _PAGINA_DICT,
        "itens": itens,
        "opcoes": None,
        "itens_com_opcoes": True,
        "pagina": 1,
        "total": 1,
        "progresso": 100 if readonly else 0,
        "paginas_dominios": [(1, _TITULO)],
        "pagina_anterior": None,
        "itens_faltando": faltando,
        "readonly": readonly,
        "publico": publico,
    }
    if token:
        ctx["token"] = token
    return ctx


@login_required
def nova_avaliacao_seps(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not request.user.perfil.tem_acesso("seps"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo SEPS.")
        return redirect("detalhe_paciente", paciente_id=paciente_id)
    av = AvaliacaoSEPS.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("seps_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def seps_form(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoSEPS, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status == "concluida":
        return redirect("seps_resultado", avaliacao_id=avaliacao_id)
    qs = list(av.respostas.all())
    respostas_salvas = {r.numero_item: r.valor for r in qs}
    obs_salvas = {r.numero_item: r.observacao for r in qs}
    faltando, obs_render = [], {}

    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar(request)
        obs_render = obs
        if erros and not confirmar:
            respostas_salvas = {**respostas_salvas, **novas}
            faltando = erros
        else:
            _salvar(av, novas, obs)
            av = _calcular(av)
            av.status = "concluida"
            av.save()
            return redirect("seps_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(av, _itens_render(respostas_salvas, obs_salvas, obs_render), faltando))


@login_required
def seps_resultado(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoSEPS, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status != "concluida":
        return redirect("seps_form", avaliacao_id=avaliacao_id, pagina=1)
    todas = list(av.paciente.avaliacoes_seps.filter(status="concluida").order_by("data"))
    outras = [a for a in todas if a.id != av.id]
    subescalas = [
        {"nome": info["nome"], "pont": getattr(av, f"pont_{key}", 0) or 0, "max": info["max"]}
        for key, info in SEPS_SUBESCALAS.items()
    ]
    total_geral = sum(s["pont"] for s in subescalas)
    max_geral = sum(s["max"] for s in subescalas)
    return render(request, "questionario/avaliacoes/seps_resultado.html", {
        "avaliacao": av, "paciente": av.paciente,
        "subescalas": subescalas,
        "total_geral": total_geral, "max_geral": max_geral,
        "cor": _COR,
        "comparativo_labels": json.dumps([a.data.strftime("%d/%m/%Y") for a in todas]),
        "comparativo_datasets": json.dumps([{"label": "SEPS (Total)", "data": [
            sum(filter(None, [a.pont_aversao_toque, a.pont_foco_unica, a.pont_vomito,
                              a.pont_sensib_temp, a.pont_expulsao, a.pont_encher]))
            for a in todas], "borderColor": _COR, "backgroundColor": _COR + "33", "tension": 0.3}]),
        "tem_comparativo": len(todas) > 1, "outras_avaliacoes": outras,
    })


@login_required
def seps_visualizar(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoSEPS, uuid=avaliacao_id, paciente__medico=request.user)
    qs = list(av.respostas.all())
    respostas = {r.numero_item: r.valor for r in qs}
    obs = {r.numero_item: r.observacao for r in qs}
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(av, _itens_render(respostas, obs, {}), [], readonly=True))


@login_required
def seps_deletar(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoSEPS, uuid=avaliacao_id, paciente__medico=request.user)
    pid = av.paciente.uuid
    if request.method == "POST":
        av.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "SEPS excluído com sucesso."})
    return redirect("detalhe_paciente", paciente_id=pid)


@login_required
def salvar_observacoes_seps(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoSEPS, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        av.observacoes = request.POST.get("observacoes", "").strip()
        av.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
    return redirect("seps_resultado", avaliacao_id=avaliacao_id)


def seps_publico(request, token, pagina):
    av = get_object_or_404(AvaliacaoSEPS, token=token)
    if av.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    qs = list(av.respostas.all())
    respostas_salvas = {r.numero_item: r.valor for r in qs}
    obs_salvas = {r.numero_item: r.observacao for r in qs}
    faltando, obs_render = [], {}

    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar(request)
        obs_render = obs
        if erros and not confirmar:
            respostas_salvas = {**respostas_salvas, **novas}
            faltando = erros
        else:
            _salvar(av, novas, obs)
            av = _calcular(av)
            av.status = "concluida"
            av.save()
            try:
                notificar_terapeuta(av.paciente, "seps", request)
            except Exception:
                pass
            return render(request, "questionario/dashboard/concluido.html")

    ctx = _ctx(av, _itens_render(respostas_salvas, obs_salvas, obs_render), faltando, publico=True, token=token)
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def enviar_email_seps(request, avaliacao_id):
    from django.utils import timezone as tz
    from django.template.loader import render_to_string
    av = get_object_or_404(AvaliacaoSEPS, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("seps_publico", kwargs={"token": av.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        enviar_email.delay(subject="SEPS — IntegraMente", message=f"Responda o questionário em: {link}",
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
