"""
Utilitários compartilhados para os módulos de psicologia.
Reduz duplicação de código entre os 21 novos módulos.
"""
import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.core.mail import send_mail
from django.utils import timezone as tz


def classificar(score, corte_list):
    """Classifica um score baseado em lista de (label, min, max)."""
    for label, min_v, max_v in corte_list:
        if min_v <= score <= max_v:
            return label
    return corte_list[-1][0]


def processar_post_escala(request, itens, valores_validos):
    """Processa POST genérico para escala com itens numerados."""
    erros, novas, obs = [], {}, {}
    for item in itens:
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


def salvar_respostas(ModelResposta, avaliacao, novas, obs):
    """Salva respostas de forma genérica."""
    for numero, valor in novas.items():
        ModelResposta.objects.update_or_create(
            avaliacao=avaliacao, numero_item=numero,
            defaults={"valor": valor, "observacao": obs.get(numero, "")}
        )


def calcular_por_subescalas(avaliacao, itens, subescalas, valores_validos_min=0):
    """Calcula pontuações por subescala e campo no model."""
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    for key, sub in subescalas.items():
        total = sum(respostas.get(n, valores_validos_min) for n in sub["itens"])
        setattr(avaliacao, sub["campo"], total)
    return avaliacao


def enviar_email_avaliacao(request, avaliacao, url_name, label, pagina=1):
    """Envia e-mail com link para avaliação pública."""
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
    try:
        link = request.build_absolute_uri(
            reverse(url_name, kwargs={"token": avaliacao.token, "pagina": pagina})
        )
    except Exception:
        link = request.build_absolute_uri(
            reverse(url_name, kwargs={"token": avaliacao.token})
        )
    html = render_to_string(
        "questionario/emails/email_link_avaliacao.html",
        {"paciente": paciente, "link": link}
    )
    try:
        send_mail(
            subject=f"{label} — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário no link: {link}",
            from_email=None, recipient_list=[email_dest], html_message=html, fail_silently=False,
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
