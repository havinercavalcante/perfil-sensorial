import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Paciente, AvaliacaoBebe, RespostaBebe
from ..data.data_bebe import (
    SECOES_BEBE, SECOES_PEQUENA,
    PERGUNTAS_BEBE, PERGUNTAS_PEQUENA,
    OPCOES_BEBE,
    QUADRANTE_BEBE, QUADRANTE_PEQUENA,
    QUADRANTES_CONFIG as BEBE_QUADRANTES_CONFIG,
    calcular_pontuacao_bebe,
    classificar_bebe,
)
from ..services import notificar_terapeuta


@login_required
def nova_avaliacao_bebe(request, paciente_id):
    from django.http import JsonResponse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('bebe'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo Perfil Sensorial Bebê.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    faixa = request.GET.get("faixa", "bebe")
    if faixa not in ("bebe", "crianca_pequena"):
        faixa = "bebe"
    av = AvaliacaoBebe.objects.create(paciente=paciente, faixa=faixa, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("bebe_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def bebe_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoBebe, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("bebe_resultado", avaliacao_id=avaliacao_id)

    if avaliacao.faixa == "bebe":
        secoes = SECOES_BEBE
        perguntas_data = PERGUNTAS_BEBE
    else:
        secoes = SECOES_PEQUENA
        perguntas_data = PERGUNTAS_PEQUENA

    total_paginas = len(secoes)
    if pagina < 1 or pagina > total_paginas:
        return redirect("bebe_form", avaliacao_id=avaliacao_id, pagina=1)

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
                    if 1 <= v <= 5:
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
                RespostaBebe.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={"valor": valor}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, total_paginas)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > total_paginas:
                return redirect("bebe_concluir", avaliacao_id=avaliacao_id)
            return redirect("bebe_form", avaliacao_id=avaliacao_id, pagina=proxima)

    perguntas = [
        {"numero": item, "texto": perguntas_data.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens
    ]

    return render(request, "questionario/avaliacoes/bebe_form.html", {
        "avaliacao": avaliacao,
        "secao": secao_atual,
        "perguntas": perguntas,
        "opcoes": OPCOES_BEBE,
        "pagina": pagina,
        "total": total_paginas,
        "progresso": int((pagina - 1) / total_paginas * 100),
        "paginas_secoes": [(i + 1, secoes[i]["nome"]) for i in range(total_paginas)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    })


@login_required
def bebe_concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBebe, uuid=avaliacao_id, paciente__medico=request.user)
    secoes = SECOES_BEBE if avaliacao.faixa == "bebe" else SECOES_PEQUENA
    total_itens = sum(len(s["itens"]) for s in secoes)
    if avaliacao.respostas.count() < total_itens:
        messages.warning(request, "Ainda há itens sem resposta.")
        return redirect("bebe_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    p = calcular_pontuacao_bebe(respostas, avaliacao.faixa)
    avaliacao.pont_busca = p.get("busca", 0)
    avaliacao.pont_evitamento = p.get("evitamento", 0)
    avaliacao.pont_sensibilidade = p.get("sensibilidade", 0)
    avaliacao.pont_registro = p.get("registro", 0)
    avaliacao.status = "concluida"
    avaliacao.save()
    return redirect("bebe_resultado", avaliacao_id=avaliacao_id)


@login_required
def bebe_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBebe, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if avaliacao.status != "concluida":
        return redirect("bebe_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    if avaliacao.pont_busca is None:
        respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
        p = calcular_pontuacao_bebe(respostas, avaliacao.faixa)
        avaliacao.pont_busca = p.get("busca", 0)
        avaliacao.pont_evitamento = p.get("evitamento", 0)
        avaliacao.pont_sensibilidade = p.get("sensibilidade", 0)
        avaliacao.pont_registro = p.get("registro", 0)
        avaliacao.save(update_fields=["pont_busca", "pont_evitamento", "pont_sensibilidade", "pont_registro"])

    faixa_key = "max_bebe" if avaliacao.faixa == "bebe" else "max_pequena"
    campo_map = {
        "busca": avaliacao.pont_busca,
        "evitamento": avaliacao.pont_evitamento,
        "sensibilidade": avaliacao.pont_sensibilidade,
        "registro": avaliacao.pont_registro,
    }
    quadrantes = []
    for quad_id, config in BEBE_QUADRANTES_CONFIG.items():
        valor = campo_map.get(quad_id) or 0
        maximo = config[faixa_key]
        classificacao = classificar_bebe(valor, maximo)
        quadrantes.append({
            "id": quad_id,
            "nome": config["nome"],
            "cor": config["cor"],
            "valor": valor,
            "maximo": maximo,
            "pct": int(valor / maximo * 100) if maximo else 0,
            "classificacao": classificacao,
        })

    todas_av = list(paciente.avaliacoes_bebe.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    comparativo_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av])
    dominios_comp = [
        {"nome": q["nome"], "campo": f"pont_{q['id']}", "max": q["maximo"]}
        for q in quadrantes
    ]
    cores_linha = ["#2E7D6B", "#3E73D1", "#E8793A", "#9B59B6"]
    comparativo_datasets = []
    for i, dom in enumerate(dominios_comp):
        valores = [round((getattr(av, dom["campo"]) or 0) / dom["max"] * 100) if dom["max"] else 0 for av in todas_av]
        comparativo_datasets.append({"label": dom["nome"], "data": valores, "borderColor": cores_linha[i], "backgroundColor": cores_linha[i] + "33", "tension": 0.3})

    return render(request, "questionario/avaliacoes/bebe_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "quadrantes": quadrantes,
        "quadrantes_json": json.dumps([{"nome": q["nome"], "pct": q["pct"], "cor": q["cor"]} for q in quadrantes]),
        "comparativo_labels": comparativo_labels,
        "comparativo_datasets": json.dumps(comparativo_datasets),
        "tem_comparativo": len(todas_av) > 1,
        "outras_avaliacoes": outras,
    })


@login_required
def bebe_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoBebe, uuid=avaliacao_id, paciente__medico=request.user)
    secoes = SECOES_BEBE if avaliacao.faixa == "bebe" else SECOES_PEQUENA
    perguntas_data = PERGUNTAS_BEBE if avaliacao.faixa == "bebe" else PERGUNTAS_PEQUENA
    total_paginas = len(secoes)

    if pagina < 1 or pagina > total_paginas:
        return redirect("bebe_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    secao_atual = secoes[pagina - 1]
    itens = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens)}

    perguntas = [
        {"numero": item, "texto": perguntas_data.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens
    ]
    return render(request, "questionario/avaliacoes/bebe_form.html", {
        "avaliacao": avaliacao, "secao": secao_atual, "perguntas": perguntas,
        "opcoes": OPCOES_BEBE, "pagina": pagina, "total": total_paginas,
        "progresso": int((pagina - 1) / total_paginas * 100),
        "paginas_secoes": [(i + 1, secoes[i]["nome"]) for i in range(total_paginas)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "readonly": True,
    })


@login_required
def bebe_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoBebe, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação Bebê excluída com sucesso."})
        messages.success(request, "Avaliação Bebê excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_bebe(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoBebe, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("bebe_resultado", avaliacao_id=avaliacao_id)
    return redirect("bebe_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_bebe(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.http import JsonResponse
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoBebe, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    from django.template.loader import render_to_string
    link = request.build_absolute_uri(f"/bebe/publico/{avaliacao.token}/1/")
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        send_mail(
            subject="Perfil Sensorial Bebê — IntegraMente",
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


def bebe_publico_view(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoBebe, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    faixa = avaliacao.faixa
    secoes = SECOES_BEBE if faixa == "bebe" else SECOES_PEQUENA
    perguntas_dict = PERGUNTAS_BEBE if faixa == "bebe" else PERGUNTAS_PEQUENA
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
                    if 1 <= v <= 5:
                        respostas_novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)
        if erros:
            messages.error(request, "Por favor, responda todas as perguntas antes de continuar.")
        else:
            for item, valor in respostas_novas.items():
                RespostaBebe.objects.update_or_create(avaliacao=avaliacao, numero_item=item, defaults={"valor": valor})
            if pagina < total:
                avaliacao.pagina_atual = pagina + 1
                avaliacao.save(update_fields=["pagina_atual"])
                return redirect("bebe_publico", token=token, pagina=pagina + 1)
            else:
                respostas_finais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
                p = calcular_pontuacao_bebe(respostas_finais, faixa)
                avaliacao.pont_busca = p.get("busca", 0)
                avaliacao.pont_evitamento = p.get("evitamento", 0)
                avaliacao.pont_sensibilidade = p.get("sensibilidade", 0)
                avaliacao.pont_registro = p.get("registro", 0)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "bebe", request)
                except Exception:
                    pass
                return render(request, "questionario/dashboard/concluido.html")
        respostas_salvas.update(respostas_novas)

    perguntas = [
        {"numero": item, "texto": perguntas_dict.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens_secao
    ]
    return render(request, "questionario/avaliacoes/bebe_form.html", {
        "avaliacao": avaliacao, "secao": secao_atual, "perguntas": perguntas,
        "opcoes": OPCOES_BEBE, "pagina": pagina, "total": total,
        "progresso": int((pagina - 1) / total * 100),
        "paginas_secoes": [(i + 1, secoes[i]["nome"]) for i in range(total)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
    })
