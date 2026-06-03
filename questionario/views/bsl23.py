import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoBSL23, RespostaBSL23
from ..data.data_bsl23 import BSL23_ITENS, BSL23_SUBESCALAS, BSL23_OPCOES, BSL23_CORTE
from ..services import notificar_terapeuta

BSL23_PAGINAS = [{"key": "total", "nome": "BSL-23", "cor": "#8E44AD", "campo": "media_total"}]
TOTAL_PAGINAS = 1

_URL_NAMES = {
    "url_form_name": "bsl23_form", "url_publico_name": "bsl23_publico",
    "url_visualizar_name": "bsl23_visualizar", "url_resultado_name": "bsl23_resultado",
    "avaliacao_titulo": "BSL-23",
}


def _classificar(score, corte_list):
    for label, min_v, max_v in corte_list:
        if min_v <= float(score) <= max_v:
            return label
    return corte_list[-1][0]


def _processar_post_bsl23(request):
    vals = {0,1,2,3,4}
    erros, novas, obs = [], {}, {}
    for item in BSL23_ITENS:
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


def _salvar_bsl23(avaliacao, novas, obs):
    for n, v in novas.items():
        RespostaBSL23.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n, defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular_bsl23(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    total = sum(respostas.get(i['numero'], 0) for i in BSL23_ITENS)
    avaliacao.media_total = round(total / 23, 2)
    return avaliacao


def _ctx_bsl23(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando, extra=None):
    ctx = {
        **_URL_NAMES, "avaliacao": avaliacao, "paciente": avaliacao.paciente,
        "dominio": pagina_dict, "itens": itens_render, "opcoes": BSL23_OPCOES,
        "pagina": pagina, "total": TOTAL_PAGINAS, "progresso": 0,
        "paginas_dominios": [(1, BSL23_PAGINAS[0]["nome"])],
        "pagina_anterior": None, "itens_faltando": itens_faltando,
    }
    if extra:
        ctx.update(extra)
    return ctx


@login_required
def nova_avaliacao_bsl23(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('bsl23'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo BSL-23.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoBSL23.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("bsl23_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def bsl23_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoBSL23, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("bsl23_resultado", avaliacao_id=avaliacao_id)
    pagina_dict = BSL23_PAGINAS[0]
    numeros = [i["numero"] for i in BSL23_ITENS]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_bsl23(request)
        obs_render = obs
        if erros and not confirmar:
            rs.update(novas)
            itens_faltando = erros
        else:
            _salvar_bsl23(avaliacao, novas, obs)
            avaliacao = _calcular_bsl23(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            return redirect("bsl23_resultado", avaliacao_id=avaliacao_id)
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))} for i in BSL23_ITENS]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx_bsl23(avaliacao, pagina_dict, 1, itens_render, rs, itens_faltando))


@login_required
def bsl23_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBSL23, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("bsl23_form", avaliacao_id=avaliacao_id, pagina=1)
    total = getattr(avaliacao, "media_total") or 0
    corte_list = BSL23_CORTE.get("total", [])
    class_total = _classificar(total, corte_list) if corte_list else "—"
    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_bsl23.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    return render(request, "questionario/avaliacoes/bsl23_resultado.html", {
        "avaliacao": avaliacao, "paciente": paciente,
        "total": total, "class_total": class_total, "corte": corte_list,
        "comparativo_labels": json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av]),
        "comparativo_datasets": json.dumps([{"label": "BSL-23", "data": [getattr(av, "media_total") or 0 for av in todas_av], "borderColor": "#8E44AD", "backgroundColor": "#8E44AD33", "tension": 0.3}]),
        "tem_comparativo": len(todas_av) > 1, "outras_avaliacoes": outras,
    })


@login_required
def bsl23_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoBSL23, uuid=avaliacao_id, paciente__medico=request.user)
    pagina_dict = BSL23_PAGINAS[0]
    numeros = [i["numero"] for i in BSL23_ITENS]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": os_.get(i["numero"], "")} for i in BSL23_ITENS]
    ctx = _ctx_bsl23(avaliacao, pagina_dict, 1, itens_render, rs, [])
    ctx["progresso"] = 100
    ctx["readonly"] = True
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def bsl23_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBSL23, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "BSL-23 excluído com sucesso."})
        messages.success(request, "BSL-23 excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_bsl23(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBSL23, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("bsl23_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_bsl23(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoBSL23, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("bsl23_publico", kwargs={"token": avaliacao.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(subject="BSL-23 — IntegraMente", message=f"Link: {link}", from_email=None, recipient_list=[email_dest], html_message=html, fail_silently=False)
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


def bsl23_publico(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoBSL23, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    pagina_dict = BSL23_PAGINAS[0]
    numeros = [i["numero"] for i in BSL23_ITENS]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_bsl23(request)
        obs_render = obs
        if erros and not confirmar:
            rs.update(novas)
            itens_faltando = erros
        else:
            _salvar_bsl23(avaliacao, novas, obs)
            avaliacao = _calcular_bsl23(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            try:
                notificar_terapeuta(avaliacao.paciente, "bsl23", request)
            except Exception:
                pass
            return render(request, "questionario/dashboard/concluido.html")
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))} for i in BSL23_ITENS]
    ctx = _ctx_bsl23(avaliacao, pagina_dict, 1, itens_render, rs, itens_faltando, extra={"publico": True, "token": token})
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)
