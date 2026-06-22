from django.conf import settings
import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from ..models import Paciente, AvaliacaoPCL5, RespostaPCL5
from ..data.data_pcl5 import PCL5_DOMINIOS, PCL5_OPCOES, PCL5_CORTE
from ..services import notificar_terapeuta
from ..tasks import enviar_email
from django.templatetags.static import static

TOTAL_PAGINAS = len(PCL5_DOMINIOS)

_URL_NAMES = {
    "url_form_name":       "pcl5_form",
    "url_publico_name":    "pcl5_publico",
    "url_visualizar_name": "pcl5_visualizar",
    "url_resultado_name":  "pcl5_resultado",
    "avaliacao_titulo":    "PCL-5 — Lista de Verificação de PTSD (DSM-5)",
}


def _numero_global(idx_dom, numero_local):
    return (idx_dom * 100) + numero_local


def _calcular(avaliacao):
    for idx, dom in enumerate(PCL5_DOMINIOS):
        nums = [_numero_global(idx, n) for n, _ in dom["itens"]]
        total = sum(r.valor for r in avaliacao.respostas.filter(numero_item__in=nums))
        setattr(avaliacao, dom["campo"], total)
    avaliacao.pont_total = sum(
        getattr(avaliacao, dom["campo"]) or 0 for dom in PCL5_DOMINIOS
    )
    return avaliacao


def _render_form(request, avaliacao, pagina, readonly=False, publico=False, token=None):
    idx = pagina - 1
    dom = PCL5_DOMINIOS[idx]
    nums_glob = [_numero_global(idx, n) for n, _ in dom["itens"]]
    qs = list(avaliacao.respostas.filter(numero_item__in=nums_glob))
    respostas_salvas = {r.numero_item: r.valor for r in qs}
    obs_salvas       = {r.numero_item: r.observacao for r in qs}
    faltando, obs_render = [], {}

    if not readonly and request.method == "POST":
        confirmar = request.POST.get("confirmar_incompleto") == "1"
        vals_validos = {o["valor"] for o in PCL5_OPCOES}
        erros, novas, obs = [], {}, {}
        for numero, _ in dom["itens"]:
            val = request.POST.get(f"item_{numero}")
            if val is None:
                erros.append(numero)
            else:
                try:
                    v = int(val)
                    if v in vals_validos:
                        novas[numero] = v
                    else:
                        erros.append(numero)
                except (ValueError, TypeError):
                    erros.append(numero)
            obs[numero] = request.POST.get(f"obs_{numero}", "").strip()
        obs_render = obs

        if erros and not confirmar:
            respostas_salvas = {**respostas_salvas, **novas}
            faltando = erros
        else:
            for numero, valor in novas.items():
                RespostaPCL5.objects.update_or_create(
                    avaliacao=avaliacao,
                    numero_item=_numero_global(idx, numero),
                    defaults={"valor": valor, "observacao": obs.get(numero, "")}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, TOTAL_PAGINAS)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > TOTAL_PAGINAS:
                avaliacao = _calcular(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                if publico:
                    try:
                        notificar_terapeuta(avaliacao.paciente, "pcl5", request)
                    except Exception:
                        pass
                    return render(request, "questionario/dashboard/concluido.html")
                return redirect("pcl5_resultado", avaliacao_id=avaliacao.uuid)
            if publico:
                return redirect("pcl5_publico", token=token, pagina=proxima)
            return redirect("pcl5_form", avaliacao_id=avaliacao.uuid, pagina=proxima)

    respostas_locais = {n: respostas_salvas.get(_numero_global(idx, n)) for n, _ in dom["itens"]}
    obs_locais = {n: obs_salvas.get(_numero_global(idx, n), "") for n, _ in dom["itens"]}

    itens_render = [
        {
            "numero": n, "texto": t,
            "resposta_salva": respostas_locais.get(n),
            "observacao_salva": obs_render.get(n, obs_locais.get(n, "")),
        }
        for n, t in dom["itens"]
    ]

    ctx = {
        **_URL_NAMES,
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominio": dom,
        "itens": itens_render,
        "opcoes": PCL5_OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_dominios": [(i + 1, PCL5_DOMINIOS[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "itens_faltando": faltando,
        "readonly": readonly,
        "publico": publico,
    }
    if token:
        ctx["token"] = token
    return render(request, "questionario/avaliacoes/avaliacao_dominio_form.html", ctx)


@login_required
def nova_avaliacao_pcl5(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not request.user.perfil.tem_acesso("pcl5"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo PCL-5.")
        return redirect("detalhe_paciente", paciente_id=paciente_id)
    av = AvaliacaoPCL5.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("pcl5_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def pcl5_form(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoPCL5, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status == "concluida":
        return redirect("pcl5_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("pcl5_form", avaliacao_id=avaliacao_id, pagina=1)
    return _render_form(request, av, pagina)


@login_required
def pcl5_resultado(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoPCL5, uuid=avaliacao_id, paciente__medico=request.user)
    if av.status != "concluida":
        return redirect("pcl5_form", avaliacao_id=avaliacao_id, pagina=av.pagina_atual)
    total = av.pont_total or 0
    classificacao = "Indicativo provável de TEPT" if total >= 31 else "Sem indicativo de TEPT"
    todas = list(av.paciente.avaliacoes_pcl5.filter(status="concluida").order_by("data"))
    outras = [a for a in todas if a.id != av.id]
    resultado = [
        {
            "key":   dom["key"],
            "nome":  dom["nome"],
            "cor":   dom["cor"],
            "score": getattr(av, dom["campo"]) or 0,
            "max":   len(dom["itens"]) * 4,
        }
        for dom in PCL5_DOMINIOS
    ]
    for r in resultado:
        r["pct"] = int(r["score"] / r["max"] * 100) if r["max"] else 0
    cores = [dom["cor"] for dom in PCL5_DOMINIOS]
    datasets = []
    for i, dom in enumerate(PCL5_DOMINIOS):
        mx = len(dom["itens"]) * 4
        datasets.append({
            "label": dom["nome"],
            "data": [round((getattr(a, dom["campo"]) or 0) / mx * 100) for a in todas],
            "borderColor": cores[i], "backgroundColor": cores[i] + "33", "tension": 0.3,
        })
    return render(request, "questionario/avaliacoes/pcl5_resultado.html", {
        "avaliacao": av, "paciente": av.paciente,
        "total": total, "max_total": 80,
        "classificacao": classificacao,
        "resultado": resultado,
        "comparativo_labels": json.dumps([a.data.strftime("%d/%m/%Y") for a in todas]),
        "comparativo_datasets": json.dumps(datasets),
        "tem_comparativo": len(todas) > 1, "outras_avaliacoes": outras,
    })


@login_required
def pcl5_visualizar(request, avaliacao_id, pagina):
    av = get_object_or_404(AvaliacaoPCL5, uuid=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("pcl5_visualizar", avaliacao_id=avaliacao_id, pagina=1)
    return _render_form(request, av, pagina, readonly=True)


@login_required
def pcl5_deletar(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoPCL5, uuid=avaliacao_id, paciente__medico=request.user)
    pid = av.paciente.uuid
    if request.method == "POST":
        av.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "PCL-5 excluído com sucesso."})
    return redirect("detalhe_paciente", paciente_id=pid)


@login_required
def salvar_observacoes_pcl5(request, avaliacao_id):
    av = get_object_or_404(AvaliacaoPCL5, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        av.observacoes = request.POST.get("observacoes", "").strip()
        av.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
    return redirect("pcl5_resultado", avaliacao_id=avaliacao_id)


def pcl5_publico(request, token, pagina):
    av = get_object_or_404(AvaliacaoPCL5, token=token)
    if av.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("pcl5_publico", token=token, pagina=1)
    return _render_form(request, av, pagina, publico=True, token=token)


@login_required
def enviar_email_pcl5(request, avaliacao_id):
    from django.utils import timezone as tz
    from django.template.loader import render_to_string
    av = get_object_or_404(AvaliacaoPCL5, uuid=avaliacao_id, paciente__medico=request.user)
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
    link = request.build_absolute_uri(reverse("pcl5_publico", kwargs={"token": av.token, "pagina": 1}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        enviar_email.delay(subject="PCL-5 — IntegraMente", message=f"Responda em: {link}",
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
