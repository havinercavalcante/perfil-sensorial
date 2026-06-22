from django.conf import settings
import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoEBAI, RespostaEBAI
from ..data.data_ebai import EBAI_ITENS, EBAI_ITENS_INVERTIDOS, EBAI_TABELA_T
from ..services import notificar_terapeuta
from ..tasks import enviar_email
from django.templatetags.static import static

_COR   = "#E67E22"
_TITULO = "EBAI — Escala Brasileira de Alimentação Infantil"
_URL_NAMES = {
    "url_form_name":       "ebai_form",
    "url_publico_name":    "ebai_publico",
    "url_visualizar_name": "ebai_visualizar",
    "url_resultado_name":  "ebai_resultado",
    "avaliacao_titulo":    _TITULO,
}
_PAGINA_DICT = {"key": "total", "nome": _TITULO, "cor": _COR, "campo": "pont_bruto"}


def _itens_render(respostas_salvas, obs_salvas, obs_render):
    return [
        {
            "numero": n,
            "texto": t,
            "polo_esq": polo_esq,
            "polo_dir": polo_dir,
            "resposta_salva": respostas_salvas.get(n),
            "observacao_salva": obs_render.get(n, obs_salvas.get(n, "")),
        }
        for n, t, polo_esq, polo_dir in EBAI_ITENS
    ]


_TEMPLATE_FORM = "questionario/avaliacoes/ebai_form.html"
_TEMPLATE_VIZ  = "questionario/avaliacoes/ebai_form.html"


def _processar(request):
    erros, novas, obs = [], {}, {}
    for n, *_ in EBAI_ITENS:
        val = request.POST.get(f"item_{n}")
        if val is None:
            erros.append(n)
        else:
            try:
                v = int(val)
                if 1 <= v <= 7:
                    novas[n] = v
                else:
                    erros.append(n)
            except (ValueError, TypeError):
                erros.append(n)
        obs[n] = request.POST.get(f"obs_{n}", "").strip()
    return erros, novas, obs


def _salvar(avaliacao, novas, obs):
    for n, v in novas.items():
        RespostaEBAI.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n,
            defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    pont_bruto = 0
    for n, *_ in EBAI_ITENS:
        v = respostas.get(n, 1)
        if n in EBAI_ITENS_INVERTIDOS:
            v = 8 - v
        pont_bruto += v
    avaliacao.pont_bruto = pont_bruto
    avaliacao.escore_t = EBAI_TABELA_T.get(pont_bruto)
    return avaliacao


def _classificar(escore_t):
    if escore_t is None:
        return "Sem dificuldades significativas"
    if escore_t >= 71:
        return "Dificuldades severas"
    elif escore_t >= 66:
        return "Dificuldades moderadas"
    elif escore_t >= 61:
        return "Dificuldades leves"
    else:
        return "Sem dificuldades significativas"


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
        "ebai_escala": [1, 2, 3, 4, 5, 6, 7],
    }
    if token:
        ctx["token"] = token
    return ctx


@login_required
def nova_avaliacao_ebai(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not request.user.perfil.tem_acesso("ebai"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo EBAI.")
        return redirect("detalhe_paciente", paciente_id=paciente_id)
    av = AvaliacaoEBAI.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("ebai_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def ebai_form(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoEBAI, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status == "concluida":
        return redirect("ebai_resultado", avaliacao_id=avaliacao_id)
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
            return redirect("ebai_resultado", avaliacao_id=avaliacao_id)

    return render(request, _TEMPLATE_FORM,
                  _ctx(av, _itens_render(respostas_salvas, obs_salvas, obs_render), faltando))


@login_required
def ebai_resultado(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoEBAI, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status != "concluida":
        return redirect("ebai_form", avaliacao_id=avaliacao_id, pagina=1)
    pont_bruto = av.pont_bruto or 0
    escore_t = av.escore_t
    todas = list(av.paciente.avaliacoes_ebai.filter(status="concluida").order_by("data"))
    outras = [a for a in todas if a.id != av.id]
    return render(request, "questionario/avaliacoes/ebai_resultado.html", {
        "avaliacao": av, "paciente": av.paciente,
        "pont_bruto": pont_bruto, "escore_t": escore_t,
        "classificacao": _classificar(escore_t),
        "cor": _COR,
        "comparativo_labels": json.dumps([a.data.strftime("%d/%m/%Y") for a in todas]),
        "comparativo_datasets": json.dumps([{"label": "EBAI (Escore T)", "data": [a.escore_t or 0 for a in todas], "borderColor": _COR, "backgroundColor": _COR + "33", "tension": 0.3}]),
        "tem_comparativo": len(todas) > 1, "outras_avaliacoes": outras,
    })


@login_required
def ebai_visualizar(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoEBAI, uuid=avaliacao_id, paciente__medico=request.user)
    qs = list(av.respostas.all())
    respostas = {r.numero_item: r.valor for r in qs}
    obs = {r.numero_item: r.observacao for r in qs}
    return render(request, _TEMPLATE_VIZ,
                  _ctx(av, _itens_render(respostas, obs, {}), [], readonly=True))


@login_required
def ebai_deletar(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoEBAI, uuid=avaliacao_id, paciente__medico=request.user)
    pid = av.paciente.uuid
    if request.method == "POST":
        av.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "EBAI excluído com sucesso."})
    return redirect("detalhe_paciente", paciente_id=pid)


@login_required
def salvar_observacoes_ebai(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoEBAI, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        av.observacoes = request.POST.get("observacoes", "").strip()
        av.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
    return redirect("ebai_resultado", avaliacao_id=avaliacao_id)


def ebai_publico(request, token, pagina):
    av = get_object_or_404(AvaliacaoEBAI, token=token)
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
                notificar_terapeuta(av.paciente, "ebai", request)
            except Exception:
                pass
            return render(request, "questionario/dashboard/concluido.html")

    ctx = _ctx(av, _itens_render(respostas_salvas, obs_salvas, obs_render), faltando, publico=True, token=token)
    return render(request, _TEMPLATE_FORM, ctx)


@login_required
def enviar_email_ebai(request, avaliacao_id):
    from django.utils import timezone as tz
    from django.template.loader import render_to_string
    av = get_object_or_404(AvaliacaoEBAI, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("ebai_publico", kwargs={"token": av.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        enviar_email.delay(subject="EBAI — IntegraMente", message=f"Responda o questionário em: {link}",
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
