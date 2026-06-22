from django.conf import settings
import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoSCQ, RespostaSCQ
from ..data.data_scq import SCQ_ITENS, SCQ_SUBESCALAS, SCQ_OPCOES, SCQ_CORTE
from ..services import notificar_terapeuta
from ..tasks import enviar_email
from django.templatetags.static import static

SCQ_PAGINAS = [{"key": "total", "nome": "SCQ — Comunicação Social", "cor": "#1A5276", "campo": "pont_total"}]
TOTAL_PAGINAS = 1

_URL_NAMES = {
    "url_form_name": "scq_form", "url_publico_name": "scq_publico",
    "url_visualizar_name": "scq_visualizar", "url_resultado_name": "scq_resultado",
    "avaliacao_titulo": "SCQ — Comunicação Social",
}


def _classificar(score, corte_list):
    for label, min_v, max_v in corte_list:
        if min_v <= float(score) <= max_v:
            return label
    return corte_list[-1][0]


def _processar_post_scq(request):
    vals = {0,1}
    erros, novas, obs = [], {}, {}
    for item in SCQ_ITENS:
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


def _salvar_scq(avaliacao, novas, obs):
    for n, v in novas.items():
        RespostaSCQ.objects.update_or_create(
            avaliacao=avaliacao, numero_item=n, defaults={"valor": v, "observacao": obs.get(n, "")}
        )


def _calcular_scq(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    total = 0
    for item in SCQ_ITENS:
        n = item['numero']
        val = respostas.get(n, -1)
        if val == item['chave']:
            total += 1
    avaliacao.pont_total = total
    return avaliacao


def _ctx_scq(avaliacao, pagina_dict, pagina, itens_render, rs, itens_faltando, extra=None):
    ctx = {
        **_URL_NAMES, "avaliacao": avaliacao, "paciente": avaliacao.paciente,
        "dominio": pagina_dict, "itens": itens_render, "opcoes": SCQ_OPCOES,
        "pagina": pagina, "total": TOTAL_PAGINAS, "progresso": 0,
        "paginas_dominios": [(1, SCQ_PAGINAS[0]["nome"])],
        "pagina_anterior": None, "itens_faltando": itens_faltando,
    }
    if extra:
        ctx.update(extra)
    return ctx


@login_required
def nova_avaliacao_scq(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('scq'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo SCQ — Comunicação Social.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoSCQ.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("scq_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def scq_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoSCQ, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("scq_resultado", avaliacao_id=avaliacao_id)
    pagina_dict = SCQ_PAGINAS[0]
    numeros = [i["numero"] for i in SCQ_ITENS]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_scq(request)
        obs_render = obs
        if erros and not confirmar:
            rs.update(novas)
            itens_faltando = erros
        else:
            _salvar_scq(avaliacao, novas, obs)
            avaliacao = _calcular_scq(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            return redirect("scq_resultado", avaliacao_id=avaliacao_id)
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))} for i in SCQ_ITENS]
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html",
                  _ctx_scq(avaliacao, pagina_dict, 1, itens_render, rs, itens_faltando))


@login_required
def scq_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSCQ, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("scq_form", avaliacao_id=avaliacao_id, pagina=1)
    total = getattr(avaliacao, "pont_total") or 0
    corte_list = SCQ_CORTE.get("total", [])
    class_total = _classificar(total, corte_list) if corte_list else "—"
    paciente = avaliacao.paciente
    todas_av = list(paciente.avaliacoes_scq.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    return render(request, "questionario/avaliacoes/scq_resultado.html", {
        "avaliacao": avaliacao, "paciente": paciente,
        "total": total, "class_total": class_total, "corte": corte_list,
        "comparativo_labels": json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av]),
        "comparativo_datasets": json.dumps([{"label": "SCQ — Comunicação Social", "data": [getattr(av, "pont_total") or 0 for av in todas_av], "borderColor": "#1A5276", "backgroundColor": "#1A527633", "tension": 0.3}]),
        "tem_comparativo": len(todas_av) > 1, "outras_avaliacoes": outras,
    })


@login_required
def scq_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoSCQ, uuid=avaliacao_id, paciente__medico=request.user)
    pagina_dict = SCQ_PAGINAS[0]
    numeros = [i["numero"] for i in SCQ_ITENS]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": os_.get(i["numero"], "")} for i in SCQ_ITENS]
    ctx = _ctx_scq(avaliacao, pagina_dict, 1, itens_render, rs, [])
    ctx["progresso"] = 100
    ctx["readonly"] = True
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def scq_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSCQ, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "SCQ — Comunicação Social excluído com sucesso."})
        messages.success(request, "SCQ — Comunicação Social excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_scq(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSCQ, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("scq_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_scq(request, avaliacao_id):
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoSCQ, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("scq_publico", kwargs={"token": avaliacao.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        enviar_email.delay(subject="SCQ — Comunicação Social — IntegraMente", message=f"Link: {link}",
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


def scq_publico(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoSCQ, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    pagina_dict = SCQ_PAGINAS[0]
    numeros = [i["numero"] for i in SCQ_ITENS]
    qs = list(avaliacao.respostas.filter(numero_item__in=numeros))
    rs = {r.numero_item: r.valor for r in qs}
    os_ = {r.numero_item: r.observacao for r in qs}
    itens_faltando = []
    obs_render = {}
    if request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        erros, novas, obs = _processar_post_scq(request)
        obs_render = obs
        if erros and not confirmar:
            rs.update(novas)
            itens_faltando = erros
        else:
            _salvar_scq(avaliacao, novas, obs)
            avaliacao = _calcular_scq(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.save()
            try:
                notificar_terapeuta(avaliacao.paciente, "scq", request)
            except Exception:
                pass
            return render(request, "questionario/dashboard/concluido.html")
    itens_render = [{"numero": i["numero"], "texto": i["texto"], "resposta_salva": rs.get(i["numero"]), "observacao_salva": obs_render.get(i["numero"], os_.get(i["numero"], ""))} for i in SCQ_ITENS]
    ctx = _ctx_scq(avaliacao, pagina_dict, 1, itens_render, rs, itens_faltando, extra={"publico": True, "token": token})
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)
