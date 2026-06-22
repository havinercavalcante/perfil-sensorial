from django.conf import settings
import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoGHQ12, RespostaGHQ12
from ..data.data_ghq12 import GHQ12_ITENS, GHQ12_CORTE
from ..services import notificar_terapeuta
from ..tasks import enviar_email
from django.templatetags.static import static

_COR    = "#C0392B"
_TITULO = "GHQ12 — Escala de Depressão Pós-Parto de Edinburgh"
_URL_NAMES = {
    "url_form_name":       "ghq12_form",
    "url_publico_name":    "ghq12_publico",
    "url_visualizar_name": "ghq12_visualizar",
    "url_resultado_name":  "ghq12_resultado",
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
        for item in GHQ12_ITENS
    ]


def _processar(request):
    erros, novas, obs = [], {}, {}
    for item in GHQ12_ITENS:
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
        RespostaGHQ12.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n,
            defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    avaliacao.pont_total = sum(respostas.get(item["numero"], 0) for item in GHQ12_ITENS)
    return avaliacao


def _classificar(score):
    for label, mn, mx in GHQ12_CORTE:
        if mn <= score <= mx:
            return label
    return GHQ12_CORTE[-1][0]


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
def nova_avaliacao_ghq12(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not request.user.perfil.tem_acesso("ghq12"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo GHQ12.")
        return redirect("detalhe_paciente", paciente_id=paciente_id)
    av = AvaliacaoGHQ12.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("ghq12_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def ghq12_form(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoGHQ12, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status == "concluida":
        return redirect("ghq12_resultado", avaliacao_id=avaliacao_id)
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
            return redirect("ghq12_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(av, _itens_render(respostas_salvas, obs_salvas, obs_render), faltando))


@login_required
def ghq12_resultado(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoGHQ12, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status != "concluida":
        return redirect("ghq12_form", avaliacao_id=avaliacao_id, pagina=1)
    total = av.pont_total or 0
    todas = list(av.paciente.avaliacoes_ghq12.filter(status="concluida").order_by("data"))
    outras = [a for a in todas if a.id != av.id]
    return render(request, "questionario/avaliacoes/ghq12_resultado.html", {
        "avaliacao": av, "paciente": av.paciente,
        "total": total, "max_total": 12,
        "classificacao": _classificar(total),
        "corte": GHQ12_CORTE, "cor": _COR,
        "comparativo_labels": json.dumps([a.data.strftime("%d/%m/%Y") for a in todas]),
        "comparativo_datasets": json.dumps([{"label": "GHQ12", "data": [a.pont_total or 0 for a in todas], "borderColor": _COR, "backgroundColor": _COR + "33", "tension": 0.3}]),
        "tem_comparativo": len(todas) > 1, "outras_avaliacoes": outras,
    })


@login_required
def ghq12_visualizar(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoGHQ12, uuid=avaliacao_id, paciente__medico=request.user)
    qs = list(av.respostas.all())
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(av, _itens_render({r.numero_item: r.valor for r in qs}, {r.numero_item: r.observacao for r in qs}, {}), [], readonly=True))


@login_required
def ghq12_deletar(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoGHQ12, uuid=avaliacao_id, paciente__medico=request.user)
    pid = av.paciente.uuid
    if request.method == "POST":
        av.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "GHQ12 excluído com sucesso."})
    return redirect("detalhe_paciente", paciente_id=pid)


@login_required
def salvar_observacoes_ghq12(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoGHQ12, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        av.observacoes = request.POST.get("observacoes", "").strip()
        av.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
    return redirect("ghq12_resultado", avaliacao_id=avaliacao_id)


def ghq12_publico(request, token, pagina):
    av = get_object_or_404(AvaliacaoGHQ12, token=token)
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
                notificar_terapeuta(av.paciente, "ghq12", request)
            except Exception:
                pass
            return render(request, "questionario/dashboard/concluido.html")

    ctx = _ctx(av, _itens_render(respostas_salvas, obs_salvas, obs_render), faltando, publico=True, token=token)
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def enviar_email_ghq12(request, avaliacao_id):
    from django.utils import timezone as tz
    from django.template.loader import render_to_string
    av = get_object_or_404(AvaliacaoGHQ12, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("ghq12_publico", kwargs={"token": av.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        enviar_email.delay(subject="GHQ12 — IntegraMente", message=f"Responda o questionário em: {link}",
            recipient_list=[email_dest], html_message=html, fail_silently=False)
    except Exception as exc:
        if is_ajax:
            return JsonResponse({"ok": False, "message": f"Falha: {exc}"})
    av.email_enviado_em = tz.now()
    av.save(update_fields=["email_enviado_em"])
    if is_ajax:
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)
