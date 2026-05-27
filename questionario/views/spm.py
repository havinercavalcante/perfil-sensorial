import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Paciente, AvaliacaoSPM, RespostaSPM
from ..data.data_spm import (
    SECOES_SPM_P, SECOES_SPM_CASA,
    PERGUNTAS_SPM_P, PERGUNTAS_SPM_CASA,
    OPCOES_SPM,
    REVERSED_SPM_P, REVERSED_SPM_CASA,
    SECOES_CONFIG_SPM,
    calcular_pontuacao_spm,
    max_score_spm,
    classificar_spm_pct,
    tscore_spm,
    classificar_tscore_spm,
)
from ..services import notificar_terapeuta


def _spm_dados(faixa):
    if faixa == "spm_p":
        return SECOES_SPM_P, PERGUNTAS_SPM_P
    return SECOES_SPM_CASA, PERGUNTAS_SPM_CASA


def _spm_salvar_pontuacao(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    p = calcular_pontuacao_spm(respostas, avaliacao.faixa)
    avaliacao.pont_soc = p.get("soc", 0)
    avaliacao.pont_vis = p.get("vis", 0)
    avaliacao.pont_hea = p.get("hea", 0)
    avaliacao.pont_tou = p.get("tou", 0)
    avaliacao.pont_sme = p.get("sme", 0)
    avaliacao.pont_bod = p.get("bod", 0)
    avaliacao.pont_bal = p.get("bal", 0)
    avaliacao.pont_pla = p.get("pla", 0)
    avaliacao.pont_tot = p.get("tot", 0)
    return avaliacao


def _spm_build_secoes(avaliacao):
    faixa = avaliacao.faixa
    campo_map = {
        "soc": avaliacao.pont_soc, "vis": avaliacao.pont_vis,
        "hea": avaliacao.pont_hea, "tou": avaliacao.pont_tou,
        "sme": avaliacao.pont_sme, "bod": avaliacao.pont_bod,
        "bal": avaliacao.pont_bal, "pla": avaliacao.pont_pla,
    }
    secoes = []
    for sec_id, config in SECOES_CONFIG_SPM.items():
        raw = campo_map.get(sec_id) or 0
        t = tscore_spm(raw, sec_id, faixa)
        # barra de 0–100% mapeada de T=40 (0%) a T=80 (100%)
        t_pct = max(0, min(100, int((t - 40) / 40 * 100))) if t is not None else 0
        secoes.append({
            "id": sec_id,
            "nome": config["nome"],
            "sigla": config["sigla"],
            "cor": config["cor"],
            "valor": raw,
            "t_score": t,
            "t_pct": t_pct,
            "classificacao": classificar_tscore_spm(t) if t is not None else None,
        })
    return secoes


@login_required
def nova_avaliacao_spm(request, paciente_id):
    from django.http import JsonResponse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('spm'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo SPM.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    faixa = request.GET.get("faixa", "spm_p")
    if faixa not in ("spm_p", "spm_casa"):
        faixa = "spm_p"
    av = AvaliacaoSPM.objects.create(paciente=paciente, faixa=faixa, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("spm_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def spm_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoSPM, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("spm_resultado", avaliacao_id=avaliacao_id)

    secoes, perguntas_data = _spm_dados(avaliacao.faixa)
    total_paginas = len(secoes)
    if pagina < 1 or pagina > total_paginas:
        return redirect("spm_form", avaliacao_id=avaliacao_id, pagina=1)

    secao_atual = secoes[pagina - 1]
    itens = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens)}

    if request.method == "POST":
        erros = []
        novas = {}
        for item in itens:
            val = request.POST.get(f"item_{item}")
            if val is None:
                erros.append(item)
            else:
                try:
                    v = int(val)
                    if 1 <= v <= 4:
                        novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)

        if erros:
            messages.error(request, "Por favor, responda todos os itens antes de continuar.")
            respostas_salvas.update(novas)
        else:
            for item, valor in novas.items():
                RespostaSPM.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={"valor": valor}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, total_paginas)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > total_paginas:
                return redirect("spm_concluir", avaliacao_id=avaliacao_id)
            return redirect("spm_form", avaliacao_id=avaliacao_id, pagina=proxima)

    perguntas = [
        {"numero": item, "texto": perguntas_data.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens
    ]
    return render(request, "questionario/avaliacoes/spm_form.html", {
        "avaliacao": avaliacao,
        "secao": secao_atual,
        "perguntas": perguntas,
        "opcoes": OPCOES_SPM,
        "pagina": pagina,
        "total": total_paginas,
        "progresso": int((pagina - 1) / total_paginas * 100),
        "paginas_secoes": [(i + 1, secoes[i]["nome"]) for i in range(total_paginas)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    })


@login_required
def spm_concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSPM, uuid=avaliacao_id, paciente__medico=request.user)
    secoes, _ = _spm_dados(avaliacao.faixa)
    total_itens = sum(len(s["itens"]) for s in secoes)
    if avaliacao.respostas.count() < total_itens:
        messages.warning(request, "Ainda há itens sem resposta.")
        return redirect("spm_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    avaliacao = _spm_salvar_pontuacao(avaliacao)
    avaliacao.status = "concluida"
    avaliacao.save()
    return redirect("spm_resultado", avaliacao_id=avaliacao_id)


@login_required
def spm_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSPM, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if avaliacao.status != "concluida":
        return redirect("spm_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    if avaliacao.pont_tot is None:
        avaliacao = _spm_salvar_pontuacao(avaliacao)
        avaliacao.save(update_fields=["pont_soc", "pont_vis", "pont_hea", "pont_tou",
                                      "pont_sme", "pont_bod", "pont_bal", "pont_pla", "pont_tot"])

    secoes = _spm_build_secoes(avaliacao)
    raw_tot = avaliacao.pont_tot or 0
    t_tot = tscore_spm(raw_tot, "tot", avaliacao.faixa)
    t_tot_pct = max(0, min(100, int((t_tot - 40) / 40 * 100))) if t_tot else 0

    todas_av = list(paciente.avaliacoes_spm.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    comparativo_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av])
    _max_scores = max_score_spm(avaliacao.faixa)
    dominios_comp = [
        {"nome": "Social",       "campo": "pont_soc", "max": _max_scores.get("soc", 1)},
        {"nome": "Visão",        "campo": "pont_vis", "max": _max_scores.get("vis", 1)},
        {"nome": "Audição",      "campo": "pont_hea", "max": _max_scores.get("hea", 1)},
        {"nome": "Tato",         "campo": "pont_tou", "max": _max_scores.get("tou", 1)},
        {"nome": "Sensorial",    "campo": "pont_sme", "max": _max_scores.get("sme", 1)},
        {"nome": "Corporal",     "campo": "pont_bod", "max": _max_scores.get("bod", 1)},
        {"nome": "Equilíbrio",   "campo": "pont_bal", "max": _max_scores.get("bal", 1)},
        {"nome": "Planejamento", "campo": "pont_pla", "max": _max_scores.get("pla", 1)},
        {"nome": "Total",        "campo": "pont_tot", "max": _max_scores.get("tot", 1)},
    ]
    cores_linha = ["#2E7D6B", "#3E73D1", "#E8793A", "#9B59B6", "#E8B84B", "#C0392B", "#16A085", "#1ABC9C", "#7DB87D"]
    comparativo_datasets = []
    for i, dom in enumerate(dominios_comp):
        mx = dom["max"] or 1
        valores = [round((getattr(av, dom["campo"]) or 0) / mx * 100) for av in todas_av]
        comparativo_datasets.append({"label": dom["nome"], "data": valores, "borderColor": cores_linha[i], "backgroundColor": cores_linha[i] + "33", "tension": 0.3})

    return render(request, "questionario/avaliacoes/spm_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "secoes": secoes,
        "raw_tot": raw_tot,
        "t_tot": t_tot,
        "t_tot_pct": t_tot_pct,
        "class_tot": classificar_tscore_spm(t_tot),
        "secoes_json": json.dumps([
            {"nome": s["sigla"], "t_score": s["t_score"], "cor": s["cor"]}
            for s in secoes if s["t_score"] is not None
        ]),
        "comparativo_labels": comparativo_labels,
        "comparativo_datasets": json.dumps(comparativo_datasets),
        "tem_comparativo": len(todas_av) > 1,
        "outras_avaliacoes": outras,
    })


@login_required
def spm_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoSPM, uuid=avaliacao_id, paciente__medico=request.user)
    secoes, perguntas_data = _spm_dados(avaliacao.faixa)
    total_paginas = len(secoes)

    if pagina < 1 or pagina > total_paginas:
        return redirect("spm_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    secao_atual = secoes[pagina - 1]
    itens = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens)}

    perguntas = [
        {"numero": item, "texto": perguntas_data.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens
    ]
    return render(request, "questionario/avaliacoes/spm_form.html", {
        "avaliacao": avaliacao, "secao": secao_atual, "perguntas": perguntas,
        "opcoes": OPCOES_SPM, "pagina": pagina, "total": total_paginas,
        "progresso": int((pagina - 1) / total_paginas * 100),
        "paginas_secoes": [(i + 1, secoes[i]["nome"]) for i in range(total_paginas)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "readonly": True,
    })


@login_required
def spm_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoSPM, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação SPM excluída com sucesso."})
        messages.success(request, "Avaliação SPM excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_spm(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoSPM, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("spm_resultado", avaliacao_id=avaliacao_id)
    return redirect("spm_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_spm(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.http import JsonResponse
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoSPM, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    from django.template.loader import render_to_string
    link = request.build_absolute_uri(f"/spm/publico/{avaliacao.token}/1/")
    nome_instrumento = avaliacao.get_faixa_display()
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(
            subject=f"{nome_instrumento} — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário no link: {link}",
            from_email=None,
            recipient_list=[email_dest],
            html_message=html,
            fail_silently=False,
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


def spm_publico_view(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoSPM, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")

    secoes, perguntas_dict = _spm_dados(avaliacao.faixa)
    total = len(secoes)
    if pagina < 1 or pagina > total:
        pagina = 1
    secao_atual = secoes[pagina - 1]
    itens_secao = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens_secao)}

    if request.method == "POST":
        erros = []
        respostas_novas = {}
        for item in itens_secao:
            val = request.POST.get(f"item_{item}")
            if val is None:
                erros.append(item)
            else:
                try:
                    v = int(val)
                    if 1 <= v <= 4:
                        respostas_novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)
        if erros:
            messages.error(request, "Por favor, responda todas as perguntas antes de continuar.")
        else:
            for item, valor in respostas_novas.items():
                RespostaSPM.objects.update_or_create(avaliacao=avaliacao, numero_item=item, defaults={"valor": valor})
            if pagina < total:
                avaliacao.pagina_atual = pagina + 1
                avaliacao.save(update_fields=["pagina_atual"])
                return redirect("spm_publico", token=token, pagina=pagina + 1)
            else:
                avaliacao = _spm_salvar_pontuacao(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "spm", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
        respostas_salvas.update(respostas_novas)

    perguntas = [
        {"numero": item, "texto": perguntas_dict.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens_secao
    ]
    return render(request, "questionario/avaliacoes/spm_form.html", {
        "avaliacao": avaliacao, "secao": secao_atual, "perguntas": perguntas,
        "opcoes": OPCOES_SPM, "pagina": pagina, "total": total,
        "progresso": int((pagina - 1) / total * 100),
        "paginas_secoes": [(i + 1, secoes[i]["nome"]) for i in range(total)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
    })
