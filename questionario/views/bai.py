import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoBAI, RespostaBAI
from ..data.data_bai import BAI_ITENS, BAI_SUBESCALAS, BAI_OPCOES, BAI_CORTE
from ..services import notificar_terapeuta

BAI_PAGINAS = [{"key": "total", "nome": "Inventário de Ansiedade de Beck", "cor": "#C0392B", "campo": "pont_total"}]
TOTAL_PAGINAS = 1

_URL_NAMES = {
    "url_form_name": "bai_form", "url_publico_name": "bai_publico",
    "url_visualizar_name": "bai_visualizar", "url_resultado_name": "bai_resultado",
    "avaliacao_titulo": "BAI — Inventário de Ansiedade de Beck",
}


def _classificar(score, corte_list):
    for label, min_v, max_v in corte_list:
        if min_v <= score <= max_v:
            return label
    return corte_list[-1][0]


def _processar_post(request):
    vals = {0, 1, 2, 3}
    erros, novas, obs = [], {}, {}
    for item in BAI_ITENS:
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
        RespostaBAI.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n, defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    avaliacao.pont_total = sum(respostas.get(item["numero"], 0) for item in BAI_ITENS)
    return avaliacao


def _ctx(avaliacao, pagina_dict, pagina, itens_render, respostas_salvas, itens_faltando, extra=None):
    ctx = {
        **_URL_NAMES, "avaliacao": avaliacao, "paciente": avaliacao.paciente,
        "dominio": pagina_dict, "itens": itens_render, "opcoes": BAI_OPCOES,
        "pagina": pagina, "total": TOTAL_PAGINAS, "progresso": 0,
        "paginas_dominios": [(1, BAI_PAGINAS[0]["nome"])],
        "pagina_anterior": None, "itens_faltando": itens_faltando,
    }
    if extra:
        ctx.update(extra)
    return ctx


@login_required
def nova_avaliacao_bai(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('bai'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo BAI.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoBAI.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("bai_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def bai_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoBAI, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("bai_resultado", avaliacao_id=avaliacao_id)
    pagina_dict = BAI_PAGINAS[0]
    numeros = [i["numero"] for i in BAI_ITENS]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post(request)
        obs_render = obs
        if erros and not confirmar:
            rs.update(novas)
            itens_faltando = erros
        else:
            _salvar(avaliacao, novas, obs)
            avaliacao = _calcular(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            return redirect("bai_resultado", avaliacao_id=avaliacao_id)
    itens_render = [
        {"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]),
         "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))}
        for i in BAI_ITENS
    ]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx(avaliacao, pagina_dict, 1, itens_render, rs, itens_faltando))


@login_required
def bai_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBAI, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("bai_form", avaliacao_id=avaliacao_id, pagina=1)
    total = avaliacao.pont_total or 0
    class_total = _classificar(total, BAI_CORTE["total"])
    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_bai.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    return render(request, "questionario/avaliacoes/bai_resultado.html", {
        "avaliacao": avaliacao, "paciente": paciente,
        "total": total, "max_total": 63, "class_total": class_total,
        "corte": BAI_CORTE["total"],
        "comparativo_labels": json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av]),
        "comparativo_datasets": json.dumps([{"label": "BAI", "data": [av.pont_total or 0 for av in todas_av], "borderColor": "#C0392B", "backgroundColor": "#C0392B33", "tension": 0.3}]),
        "tem_comparativo": len(todas_av) > 1, "outras_avaliacoes": outras,
    })


@login_required
def bai_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoBAI, uuid=avaliacao_id, paciente__medico=request.user)
    pagina_dict = BAI_PAGINAS[0]
    numeros = [i["numero"] for i in BAI_ITENS]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": os_.get(i["numero"], "")} for i in BAI_ITENS]
    ctx = _ctx(avaliacao, pagina_dict, 1, itens_render, rs, [])
    ctx["progresso"] = 100
    ctx["readonly"] = True
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def bai_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBAI, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "BAI excluído com sucesso."})
        messages.success(request, "BAI excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_bai(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBAI, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("bai_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_bai(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoBAI, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("bai_publico", kwargs={"token": avaliacao.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(subject="BAI — IntegraMente", message=f"Link: {link}", from_email=None, recipient_list=[email_dest], html_message=html, fail_silently=False)
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


def bai_publico(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoBAI, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    pagina_dict = BAI_PAGINAS[0]
    numeros = [i["numero"] for i in BAI_ITENS]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post(request)
        obs_render = obs
        if erros and not confirmar:
            rs.update(novas)
            itens_faltando = erros
        else:
            _salvar(avaliacao, novas, obs)
            avaliacao = _calcular(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            try:
                notificar_terapeuta(avaliacao.paciente, "bai", request)
            except Exception:
                pass
            return render(request, "questionario/dashboard/concluido.html")
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))} for i in BAI_ITENS]
    ctx = _ctx(avaliacao, pagina_dict, 1, itens_render, rs, itens_faltando, extra={"publico": True, "token": token})
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)
