import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoEPDS, RespostaEPDS
from ..data.data_epds import EPDS_ITENS, EPDS_CORTE
from ..services import notificar_terapeuta

_COR    = "#C0392B"
_TITULO = "EPDS — Escala de Depressão Pós-Parto de Edinburgh"
_URL_NAMES = {
    "url_form_name":       "epds_form",
    "url_publico_name":    "epds_publico",
    "url_visualizar_name": "epds_visualizar",
    "url_resultado_name":  "epds_resultado",
    "avaliacao_titulo":    _TITULO,
}
_PAGINA_DICT = {"key": "total", "nome": _TITULO, "cor": _COR, "campo": "pont_total"}


def _itens_render(respostas_salvas, obs_salvas, obs_render):
    return [
        {
            "numero": item["numero"],
            "texto":  item["texto"],
            "opcoes": item["opcoes"],
            "resposta_salva": respostas_salvas.get(item["numero"]),
            "observacao_salva": obs_render.get(item["numero"], obs_salvas.get(item["numero"], "")),
        }
        for item in EPDS_ITENS
    ]


def _processar(request):
    erros, novas, obs = [], {}, {}
    for item in EPDS_ITENS:
        n = item["numero"]
        val = request.POST.get(f"item_{n}")
        if val is None:
            erros.append(n)
        else:
            try:
                v = int(val)
                if v in {o["valor"] for o in item["opcoes"]}:
                    novas[n] = v
                else:
                    erros.append(n)
            except (ValueError, TypeError):
                erros.append(n)
        obs[n] = request.POST.get(f"obs_{n}", "").strip()
    return erros, novas, obs


def _salvar(avaliacao, novas, obs):
    for n, v in novas.items():
        RespostaEPDS.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n,
            defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    avaliacao.pont_total = sum(respostas.get(item["numero"], 0) for item in EPDS_ITENS)
    return avaliacao


def _classificar(score):
    for label, mn, mx in EPDS_CORTE:
        if mn <= score <= mx:
            return label
    return EPDS_CORTE[-1][0]


def _ctx(av, itens, faltando, readonly=False, publico=False, token=None):
    ctx = {
        **_URL_NAMES,
        "avaliacao": av, "paciente": av.paciente,
        "dominio": _PAGINA_DICT, "itens": itens,
        "opcoes": None, "itens_com_opcoes": True,
        "pagina": 1, "total": 1,
        "progresso": 100 if readonly else 0,
        "paginas_dominios": [(1, _TITULO)],
        "pagina_anterior": None,
        "itens_faltando": faltando,
        "readonly": readonly, "publico": publico,
    }
    if token:
        ctx["token"] = token
    return ctx


@login_required
def nova_avaliacao_epds(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not request.user.perfil.tem_acesso("epds"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo EPDS.")
        return redirect("detalhe_paciente", paciente_id=paciente_id)
    av = AvaliacaoEPDS.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("epds_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def epds_form(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoEPDS, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status == "concluida":
        return redirect("epds_resultado", avaliacao_id=avaliacao_id)
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
            return redirect("epds_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(av, _itens_render(respostas_salvas, obs_salvas, obs_render), faltando))


@login_required
def epds_resultado(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoEPDS, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status != "concluida":
        return redirect("epds_form", avaliacao_id=avaliacao_id, pagina=1)
    total = av.pont_total or 0
    todas = list(av.paciente.avaliacoes_epds.filter(status="concluida").order_by("data"))
    outras = [a for a in todas if a.id != av.id]
    return render(request, "questionario/avaliacoes/epds_resultado.html", {
        "avaliacao": av, "paciente": av.paciente,
        "total": total, "max_total": 30,
        "classificacao": _classificar(total),
        "corte": EPDS_CORTE, "cor": _COR,
        "comparativo_labels": json.dumps([a.data.strftime("%d/%m/%Y") for a in todas]),
        "comparativo_datasets": json.dumps([{"label": "EPDS", "data": [a.pont_total or 0 for a in todas], "borderColor": _COR, "backgroundColor": _COR + "33", "tension": 0.3}]),
        "tem_comparativo": len(todas) > 1, "outras_avaliacoes": outras,
    })


@login_required
def epds_visualizar(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoEPDS, uuid=avaliacao_id, paciente__medico=request.user)
    qs = list(av.respostas.all())
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(av, _itens_render({r.numero_item: r.valor for r in qs}, {r.numero_item: r.observacao for r in qs}, {}), [], readonly=True))


@login_required
def epds_deletar(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoEPDS, uuid=avaliacao_id, paciente__medico=request.user)
    pid = av.paciente.uuid
    if request.method == "POST":
        av.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "EPDS excluído com sucesso."})
    return redirect("detalhe_paciente", paciente_id=pid)


@login_required
def salvar_observacoes_epds(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoEPDS, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        av.observacoes = request.POST.get("observacoes", "").strip()
        av.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
    return redirect("epds_resultado", avaliacao_id=avaliacao_id)


def epds_publico(request, token, pagina):
    av = get_object_or_404(AvaliacaoEPDS, token=token)
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
                notificar_terapeuta(av.paciente, "epds", request)
            except Exception:
                pass
            return render(request, "questionario/dashboard/concluido.html")

    ctx = _ctx(av, _itens_render(respostas_salvas, obs_salvas, obs_render), faltando, publico=True, token=token)
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def enviar_email_epds(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    from django.template.loader import render_to_string
    av = get_object_or_404(AvaliacaoEPDS, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = av.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado."})
        messages.error(request, "Nenhum e-mail cadastrado.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    if not av.token:
        av.token = str(uuid.uuid4())
        av.save(update_fields=["token"])
    link = request.build_absolute_uri(reverse("epds_publico", kwargs={"token": av.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(subject="EPDS — IntegraMente", message=f"Responda o questionário em: {link}",
                  from_email=None, recipient_list=[email_dest], html_message=html, fail_silently=False)
    except Exception as exc:
        if is_ajax:
            return JsonResponse({"ok": False, "message": f"Falha: {exc}"})
    av.email_enviado_em = tz.now()
    av.save(update_fields=["email_enviado_em"])
    if is_ajax:
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)
