from django.conf import settings
import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from ..models import Paciente, AvaliacaoPEDI
from ..data.pedi_data import (
    AUTOCUIDADO_SECOES, MOBILIDADE_SECOES, FUNCAO_SOCIAL_SECOES,
    CA_AUTOCUIDADO_ITENS, CA_MOBILIDADE_ITENS, CA_FUNCAO_SOCIAL_ITENS,
    lookup_escore_continuo,
)
from ..tasks import enviar_email
from django.templatetags.static import static

_PEDI_FS_MAX = {"autocuidado": 73, "mobilidade": 59, "funcao_social": 65}
_PEDI_CA_MAX = {"autocuidado": 40, "mobilidade": 35, "funcao_social": 25}


@login_required
def nova_avaliacao_pedi(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('pedi'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            from django.http import JsonResponse
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo PEDI.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoPEDI.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        from django.http import JsonResponse
        return JsonResponse({"ok": True})
    return redirect("pedi_form", avaliacao_id=av.uuid)


@login_required
def pedi_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoPEDI, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if request.method == "POST":
        def _get_int(name):
            try:
                return int(request.POST.get(name, "").strip())
            except (ValueError, AttributeError):
                return None

        avaliacao.fs_autocuidado = _get_int("fs_autocuidado")
        avaliacao.fs_mobilidade = _get_int("fs_mobilidade")
        avaliacao.fs_funcao_social = _get_int("fs_funcao_social")
        avaliacao.ca_autocuidado = _get_int("ca_autocuidado")
        avaliacao.ca_mobilidade = _get_int("ca_mobilidade")
        avaliacao.ca_funcao_social = _get_int("ca_funcao_social")

        # Escala 0-100 por aproximação (raw/max * 100)
        def _escala(raw, maximo):
            if raw is None or maximo == 0:
                return None
            return round(min(raw, maximo) / maximo * 100, 1)

        avaliacao.fs_autocuidado_escala = _escala(avaliacao.fs_autocuidado, _PEDI_FS_MAX["autocuidado"])
        avaliacao.fs_mobilidade_escala = _escala(avaliacao.fs_mobilidade, _PEDI_FS_MAX["mobilidade"])
        avaliacao.fs_funcao_social_escala = _escala(avaliacao.fs_funcao_social, _PEDI_FS_MAX["funcao_social"])
        avaliacao.ca_autocuidado_escala = _escala(avaliacao.ca_autocuidado, _PEDI_CA_MAX["autocuidado"])
        avaliacao.ca_mobilidade_escala = _escala(avaliacao.ca_mobilidade, _PEDI_CA_MAX["mobilidade"])
        avaliacao.ca_funcao_social_escala = _escala(avaliacao.ca_funcao_social, _PEDI_CA_MAX["funcao_social"])

        avaliacao.save()
        messages.success(request, "PEDI salvo com sucesso.")
        return redirect("pedi_resultado", avaliacao_id=avaliacao_id)

    steps = []
    for s in AUTOCUIDADO_SECOES:
        steps.append({"tipo": "fs", "dom": "ac", "secao": s, "dominio_label": "Autocuidado", "icon": "utensils"})
    for s in MOBILIDADE_SECOES:
        steps.append({"tipo": "fs", "dom": "mob", "secao": s, "dominio_label": "Mobilidade", "icon": "footprints"})
    for s in FUNCAO_SOCIAL_SECOES:
        steps.append({"tipo": "fs", "dom": "fs", "secao": s, "dominio_label": "Função Social", "icon": "users"})
    steps.append({"tipo": "ca", "dom": "ac",  "secao": {"codigo": "CA", "titulo": "Autocuidado"},   "dominio_label": "Assist. Cuidador", "icon": "helping-hand", "ca_itens": CA_AUTOCUIDADO_ITENS,  "ca_max": _PEDI_CA_MAX["autocuidado"]})
    steps.append({"tipo": "ca", "dom": "mob", "secao": {"codigo": "CA", "titulo": "Mobilidade"},    "dominio_label": "Assist. Cuidador", "icon": "helping-hand", "ca_itens": CA_MOBILIDADE_ITENS,   "ca_max": _PEDI_CA_MAX["mobilidade"]})
    steps.append({"tipo": "ca", "dom": "fs",  "secao": {"codigo": "CA", "titulo": "Função Social"}, "dominio_label": "Assist. Cuidador", "icon": "helping-hand", "ca_itens": CA_FUNCAO_SOCIAL_ITENS, "ca_max": _PEDI_CA_MAX["funcao_social"]})

    ac_count  = len(AUTOCUIDADO_SECOES)
    mob_count = len(MOBILIDADE_SECOES)
    fs_count  = len(FUNCAO_SOCIAL_SECOES)
    domain_starts = [0, ac_count, ac_count + mob_count, ac_count + mob_count + fs_count]

    return render(request, "questionario/avaliacoes/pedi_form.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "fs_max": _PEDI_FS_MAX,
        "ca_max": _PEDI_CA_MAX,
        "steps": steps,
        "total_steps": len(steps),
        "domain_starts": domain_starts,
        "salvar_url": reverse("pedi_salvar_progresso", args=[avaliacao_id]),
        "respostas_json": avaliacao.respostas_json or "{}",
        "pagina_atual": avaliacao.pagina_atual or 0,
    })


@login_required
def pedi_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoPEDI, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    def _ec(dominio, raw):
        if raw is None:
            return None, None
        ec, ep = lookup_escore_continuo(dominio, raw)
        return ec, ep

    fs_ac_ec, fs_ac_ep   = _ec("autocuidado",  avaliacao.fs_autocuidado)
    fs_mob_ec, fs_mob_ep = _ec("mobilidade",   avaliacao.fs_mobilidade)
    fs_fs_ec, fs_fs_ep   = _ec("funcao_social", avaliacao.fs_funcao_social)

    dominios_fs = [
        {"nome": "Autocuidado",   "raw": avaliacao.fs_autocuidado,   "max": _PEDI_FS_MAX["autocuidado"],   "escala": avaliacao.fs_autocuidado_escala,   "ec": fs_ac_ec,  "ep": fs_ac_ep},
        {"nome": "Mobilidade",    "raw": avaliacao.fs_mobilidade,    "max": _PEDI_FS_MAX["mobilidade"],    "escala": avaliacao.fs_mobilidade_escala,    "ec": fs_mob_ec, "ep": fs_mob_ep},
        {"nome": "Função Social", "raw": avaliacao.fs_funcao_social, "max": _PEDI_FS_MAX["funcao_social"], "escala": avaliacao.fs_funcao_social_escala, "ec": fs_fs_ec,  "ep": fs_fs_ep},
    ]
    dominios_ca = [
        {"nome": "Autocuidado",   "raw": avaliacao.ca_autocuidado,   "max": _PEDI_CA_MAX["autocuidado"],   "escala": avaliacao.ca_autocuidado_escala},
        {"nome": "Mobilidade",    "raw": avaliacao.ca_mobilidade,    "max": _PEDI_CA_MAX["mobilidade"],    "escala": avaliacao.ca_mobilidade_escala},
        {"nome": "Função Social", "raw": avaliacao.ca_funcao_social, "max": _PEDI_CA_MAX["funcao_social"], "escala": avaliacao.ca_funcao_social_escala},
    ]

    todas_av = list(paciente.avaliacoes_pedi.order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    comparativo_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av])
    dominios_comp = [
        {"nome": "FS Autocuidado",   "campo": "fs_autocuidado_escala"},
        {"nome": "FS Mobilidade",    "campo": "fs_mobilidade_escala"},
        {"nome": "FS Func. Social",  "campo": "fs_funcao_social_escala"},
    ]
    cores_linha = ["#2E7D6B", "#3E73D1", "#E8793A"]
    comparativo_datasets = []
    for i, dom in enumerate(dominios_comp):
        valores = [(getattr(av, dom["campo"]) or 0) for av in todas_av]
        comparativo_datasets.append({"label": dom["nome"], "data": valores, "borderColor": cores_linha[i], "backgroundColor": cores_linha[i] + "33", "tension": 0.3})

    return render(request, "questionario/avaliacoes/pedi_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "dominios_fs": dominios_fs,
        "dominios_ca": dominios_ca,
        "chart_json": json.dumps({
            "labels": ["Autocuidado", "Mobilidade", "Função Social"],
            "fs": [d["escala"] or 0 for d in dominios_fs],
            "ca": [d["escala"] or 0 for d in dominios_ca],
        }),
        "comparativo_labels": comparativo_labels,
        "comparativo_datasets": json.dumps(comparativo_datasets),
        "tem_comparativo": len(todas_av) > 1,
        "outras_avaliacoes": outras,
    })


@login_required
def pedi_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoPEDI, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação PEDI excluída com sucesso."})
        messages.success(request, "Avaliação PEDI excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


def pedi_publico_redirect(request, token):
    return redirect("pedi_publico", token=token, pagina=1)


def pedi_publico(request, token, pagina=1):
    avaliacao = get_object_or_404(AvaliacaoPEDI, token=token)
    paciente = avaliacao.paciente

    if avaliacao.fs_autocuidado is not None:
        return render(request, "questionario/dashboard/concluido.html", {})

    if request.method == "POST":
        def _get_int(name):
            try:
                return int(request.POST.get(name, "").strip())
            except (ValueError, AttributeError):
                return None

        avaliacao.fs_autocuidado = _get_int("fs_autocuidado")
        avaliacao.fs_mobilidade = _get_int("fs_mobilidade")
        avaliacao.fs_funcao_social = _get_int("fs_funcao_social")
        avaliacao.ca_autocuidado = _get_int("ca_autocuidado")
        avaliacao.ca_mobilidade = _get_int("ca_mobilidade")
        avaliacao.ca_funcao_social = _get_int("ca_funcao_social")

        def _escala(raw, maximo):
            if raw is None or maximo == 0:
                return None
            return round(min(raw, maximo) / maximo * 100, 1)

        avaliacao.fs_autocuidado_escala = _escala(avaliacao.fs_autocuidado, _PEDI_FS_MAX["autocuidado"])
        avaliacao.fs_mobilidade_escala = _escala(avaliacao.fs_mobilidade, _PEDI_FS_MAX["mobilidade"])
        avaliacao.fs_funcao_social_escala = _escala(avaliacao.fs_funcao_social, _PEDI_FS_MAX["funcao_social"])
        avaliacao.ca_autocuidado_escala = _escala(avaliacao.ca_autocuidado, _PEDI_CA_MAX["autocuidado"])
        avaliacao.ca_mobilidade_escala = _escala(avaliacao.ca_mobilidade, _PEDI_CA_MAX["mobilidade"])
        avaliacao.ca_funcao_social_escala = _escala(avaliacao.ca_funcao_social, _PEDI_CA_MAX["funcao_social"])

        avaliacao.save()
        return render(request, "questionario/dashboard/concluido.html", {})

    steps = []
    for s in AUTOCUIDADO_SECOES:
        steps.append({"tipo": "fs", "dom": "ac", "secao": s, "dominio_label": "Autocuidado", "icon": "utensils"})
    for s in MOBILIDADE_SECOES:
        steps.append({"tipo": "fs", "dom": "mob", "secao": s, "dominio_label": "Mobilidade", "icon": "footprints"})
    for s in FUNCAO_SOCIAL_SECOES:
        steps.append({"tipo": "fs", "dom": "fs", "secao": s, "dominio_label": "Função Social", "icon": "users"})
    steps.append({"tipo": "ca", "dom": "ac",  "secao": {"codigo": "CA", "titulo": "Autocuidado"},   "dominio_label": "Assist. Cuidador", "icon": "helping-hand", "ca_itens": CA_AUTOCUIDADO_ITENS,  "ca_max": _PEDI_CA_MAX["autocuidado"]})
    steps.append({"tipo": "ca", "dom": "mob", "secao": {"codigo": "CA", "titulo": "Mobilidade"},    "dominio_label": "Assist. Cuidador", "icon": "helping-hand", "ca_itens": CA_MOBILIDADE_ITENS,   "ca_max": _PEDI_CA_MAX["mobilidade"]})
    steps.append({"tipo": "ca", "dom": "fs",  "secao": {"codigo": "CA", "titulo": "Função Social"}, "dominio_label": "Assist. Cuidador", "icon": "helping-hand", "ca_itens": CA_FUNCAO_SOCIAL_ITENS, "ca_max": _PEDI_CA_MAX["funcao_social"]})

    ac_count  = len(AUTOCUIDADO_SECOES)
    mob_count = len(MOBILIDADE_SECOES)
    fs_count  = len(FUNCAO_SOCIAL_SECOES)
    domain_starts = [0, ac_count, ac_count + mob_count, ac_count + mob_count + fs_count]

    return render(request, "questionario/avaliacoes/pedi_form.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "fs_max": _PEDI_FS_MAX,
        "ca_max": _PEDI_CA_MAX,
        "steps": steps,
        "total_steps": len(steps),
        "domain_starts": domain_starts,
        "publico": True,
        "token": token,
        "pagina_url": pagina,
        "salvar_url": reverse("pedi_salvar_progresso_publico", args=[token]),
        "respostas_json": avaliacao.respostas_json or "{}",
        "pagina_atual": avaliacao.pagina_atual or 0,
    })


@login_required
def pedi_salvar_progresso(request, avaliacao_id):
    from django.http import JsonResponse
    import json as _json
    avaliacao = get_object_or_404(AvaliacaoPEDI, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        data = _json.loads(request.body)
        avaliacao.respostas_json = _json.dumps(data.get("respostas", {}))
        avaliacao.pagina_atual = int(data.get("step", 0))
        avaliacao.save(update_fields=["respostas_json", "pagina_atual"])
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False}, status=405)


def pedi_salvar_progresso_publico(request, token):
    from django.http import JsonResponse
    import json as _json
    avaliacao = get_object_or_404(AvaliacaoPEDI, token=token)
    if avaliacao.fs_autocuidado is not None:
        return JsonResponse({"ok": False}, status=403)
    if request.method == "POST":
        data = _json.loads(request.body)
        avaliacao.respostas_json = _json.dumps(data.get("respostas", {}))
        avaliacao.pagina_atual = int(data.get("step", 0))
        avaliacao.save(update_fields=["respostas_json", "pagina_atual"])
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False}, status=405)


@login_required
def salvar_observacoes_pedi(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoPEDI, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("pedi_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_pedi(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoPEDI, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    from django.template.loader import render_to_string
    link = request.build_absolute_uri(f"/pedi/publico/{avaliacao.token}/1/")
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        enviar_email.delay(
            subject="PEDI — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário PEDI no link: {link}",
            recipient_list=[email_dest],
            html_message=html,
            fail_silently=False,
        )
    except Exception as exc:
        if is_ajax:
            return JsonResponse({"ok": False, "message": f"Falha ao enviar e-mail: {exc}"})
        messages.error(request, f"Falha ao enviar e-mail: {exc}")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    if is_ajax:
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)


@login_required
def pedi_visualizar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoPEDI, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    steps = []
    for s in AUTOCUIDADO_SECOES:
        steps.append({"tipo": "fs", "dom": "ac", "secao": s, "dominio_label": "Autocuidado", "icon": "utensils"})
    for s in MOBILIDADE_SECOES:
        steps.append({"tipo": "fs", "dom": "mob", "secao": s, "dominio_label": "Mobilidade", "icon": "footprints"})
    for s in FUNCAO_SOCIAL_SECOES:
        steps.append({"tipo": "fs", "dom": "fs", "secao": s, "dominio_label": "Função Social", "icon": "users"})
    steps.append({"tipo": "ca", "dom": "ac",  "secao": {"codigo": "CA", "titulo": "Autocuidado"},   "dominio_label": "Assist. Cuidador", "icon": "helping-hand", "ca_itens": CA_AUTOCUIDADO_ITENS,  "ca_max": _PEDI_CA_MAX["autocuidado"]})
    steps.append({"tipo": "ca", "dom": "mob", "secao": {"codigo": "CA", "titulo": "Mobilidade"},    "dominio_label": "Assist. Cuidador", "icon": "helping-hand", "ca_itens": CA_MOBILIDADE_ITENS,   "ca_max": _PEDI_CA_MAX["mobilidade"]})
    steps.append({"tipo": "ca", "dom": "fs",  "secao": {"codigo": "CA", "titulo": "Função Social"}, "dominio_label": "Assist. Cuidador", "icon": "helping-hand", "ca_itens": CA_FUNCAO_SOCIAL_ITENS, "ca_max": _PEDI_CA_MAX["funcao_social"]})

    ac_count  = len(AUTOCUIDADO_SECOES)
    mob_count = len(MOBILIDADE_SECOES)
    fs_count  = len(FUNCAO_SOCIAL_SECOES)
    domain_starts = [0, ac_count, ac_count + mob_count, ac_count + mob_count + fs_count]

    return render(request, "questionario/avaliacoes/pedi_form.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "fs_max": _PEDI_FS_MAX,
        "ca_max": _PEDI_CA_MAX,
        "steps": steps,
        "total_steps": len(steps),
        "domain_starts": domain_starts,
        "salvar_url": "",
        "respostas_json": avaliacao.respostas_json or "{}",
        "pagina_atual": avaliacao.pagina_atual or 0,
        "readonly": True,
    })
