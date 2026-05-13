import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Paciente, AvaliacaoEscolar, RespostaEscolar
from ..data_escolar import (
    SECOES as ESCOLAR_SECOES,
    PERGUNTAS as ESCOLAR_PERGUNTAS,
    OPCOES as ESCOLAR_OPCOES,
    DOMINIOS_CONFIG as ESCOLAR_DOMINIOS_CONFIG,
    calcular_pontuacao_escolar,
    classificar_escolar,
)
from ..services import notificar_terapeuta

ESCOLAR_TOTAL_PAGINAS = len(ESCOLAR_SECOES)


@login_required
def nova_avaliacao_escolar(request, paciente_id):
    from django.http import JsonResponse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('escolar'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo Questionário Sensorial Escolar.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoEscolar.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "id": av.id})
    return redirect("escolar_form", avaliacao_id=av.id, pagina=1)


@login_required
def escolar_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoEscolar, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("escolar_resultado", avaliacao_id=avaliacao_id)

    if pagina < 1 or pagina > ESCOLAR_TOTAL_PAGINAS:
        return redirect("escolar_form", avaliacao_id=avaliacao_id, pagina=1)

    secao_atual = ESCOLAR_SECOES[pagina - 1]
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
                    if 0 <= v <= 4:
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
                RespostaEscolar.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={"valor": valor}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, ESCOLAR_TOTAL_PAGINAS)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > ESCOLAR_TOTAL_PAGINAS:
                return redirect("escolar_concluir", avaliacao_id=avaliacao_id)
            return redirect("escolar_form", avaliacao_id=avaliacao_id, pagina=proxima)

    perguntas = [
        {"numero": item, "texto": ESCOLAR_PERGUNTAS.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens
    ]

    return render(request, "questionario/escolar_form.html", {
        "avaliacao": avaliacao,
        "secao": secao_atual,
        "perguntas": perguntas,
        "opcoes": ESCOLAR_OPCOES,
        "pagina": pagina,
        "total": ESCOLAR_TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / ESCOLAR_TOTAL_PAGINAS * 100),
        "paginas_secoes": [(i + 1, ESCOLAR_SECOES[i]["nome"]) for i in range(ESCOLAR_TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    })


@login_required
def escolar_concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoEscolar, id=avaliacao_id, paciente__medico=request.user)
    total_itens = sum(len(s["itens"]) for s in ESCOLAR_SECOES)
    if avaliacao.respostas.count() < total_itens:
        messages.warning(request, "Ainda há itens sem resposta.")
        return redirect("escolar_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    p = calcular_pontuacao_escolar(respostas)
    avaliacao.pont_auditivo = p.get("auditivo", 0)
    avaliacao.pont_visual = p.get("visual", 0)
    avaliacao.pont_tatil = p.get("tatil", 0)
    avaliacao.pont_vestibular = p.get("vestibular", 0)
    avaliacao.pont_social = p.get("social", 0)
    avaliacao.status = "concluida"
    avaliacao.save()
    return redirect("escolar_resultado", avaliacao_id=avaliacao_id)


@login_required
def escolar_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoEscolar, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if avaliacao.status != "concluida":
        return redirect("escolar_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    if avaliacao.pont_auditivo is None:
        respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
        p = calcular_pontuacao_escolar(respostas)
        avaliacao.pont_auditivo = p.get("auditivo", 0)
        avaliacao.pont_visual = p.get("visual", 0)
        avaliacao.pont_tatil = p.get("tatil", 0)
        avaliacao.pont_vestibular = p.get("vestibular", 0)
        avaliacao.pont_social = p.get("social", 0)
        avaliacao.save(update_fields=["pont_auditivo", "pont_visual", "pont_tatil", "pont_vestibular", "pont_social"])

    campo_map = {
        "auditivo": avaliacao.pont_auditivo,
        "visual": avaliacao.pont_visual,
        "tatil": avaliacao.pont_tatil,
        "vestibular": avaliacao.pont_vestibular,
        "social": avaliacao.pont_social,
    }
    dominios = []
    for dom_id, config in ESCOLAR_DOMINIOS_CONFIG.items():
        valor = campo_map.get(dom_id) or 0
        maximo = config["max"]
        classificacao = classificar_escolar(valor, maximo)
        dominios.append({
            "id": dom_id,
            "nome": config["nome"],
            "valor": valor,
            "maximo": maximo,
            "pct": int(valor / maximo * 100) if maximo else 0,
            "classificacao": classificacao,
        })

    return render(request, "questionario/escolar_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "dominios": dominios,
        "dominios_json": json.dumps([{"nome": d["nome"], "pct": d["pct"]} for d in dominios]),
    })


@login_required
def escolar_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoEscolar, id=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > ESCOLAR_TOTAL_PAGINAS:
        return redirect("escolar_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    secao_atual = ESCOLAR_SECOES[pagina - 1]
    itens = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens)}

    perguntas = [
        {"numero": item, "texto": ESCOLAR_PERGUNTAS.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens
    ]
    return render(request, "questionario/escolar_form.html", {
        "avaliacao": avaliacao, "secao": secao_atual, "perguntas": perguntas,
        "opcoes": ESCOLAR_OPCOES, "pagina": pagina, "total": ESCOLAR_TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / ESCOLAR_TOTAL_PAGINAS * 100),
        "paginas_secoes": [(i + 1, ESCOLAR_SECOES[i]["nome"]) for i in range(ESCOLAR_TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "readonly": True,
    })


@login_required
def escolar_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoEscolar, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação Escolar excluída com sucesso."})
        messages.success(request, "Avaliação Escolar excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_escolar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoEscolar, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("escolar_resultado", avaliacao_id=avaliacao_id)
    return redirect("escolar_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_escolar(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.http import JsonResponse
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoEscolar, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    link = request.build_absolute_uri(f"/escolar/publico/{avaliacao.token}/1/")
    send_mail(
        subject="Questionário Sensorial Escolar — CeciSys",
        message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário no link: {link}",
        from_email=None,
        recipient_list=[email_dest],
        fail_silently=False,
    )
    avaliacao.email_enviado_em = tz.now()
    avaliacao.save(update_fields=["email_enviado_em"])
    if is_ajax:
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)


def escolar_publico_view(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoEscolar, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/concluido.html")
    if pagina < 1 or pagina > ESCOLAR_TOTAL_PAGINAS:
        pagina = 1
    secao_atual = ESCOLAR_SECOES[pagina - 1]
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
                    if 0 <= v <= 4:
                        respostas_novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)
        if erros:
            messages.error(request, "Por favor, responda todas as perguntas antes de continuar.")
        else:
            for item, valor in respostas_novas.items():
                RespostaEscolar.objects.update_or_create(avaliacao=avaliacao, numero_item=item, defaults={"valor": valor})
            if pagina < ESCOLAR_TOTAL_PAGINAS:
                avaliacao.pagina_atual = pagina + 1
                avaliacao.save(update_fields=["pagina_atual"])
                return redirect("escolar_publico", token=token, pagina=pagina + 1)
            else:
                respostas_finais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
                p = calcular_pontuacao_escolar(respostas_finais)
                avaliacao.pont_auditivo = p.get("auditivo", 0)
                avaliacao.pont_visual = p.get("visual", 0)
                avaliacao.pont_tatil = p.get("tatil", 0)
                avaliacao.pont_vestibular = p.get("vestibular", 0)
                avaliacao.pont_social = p.get("social", 0)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "escolar", request)
                except Exception:
                    pass
                return render(request, "questionario/concluido.html")
        respostas_salvas.update(respostas_novas)

    perguntas = [
        {"numero": item, "texto": ESCOLAR_PERGUNTAS.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens_secao
    ]
    return render(request, "questionario/escolar_form.html", {
        "avaliacao": avaliacao, "secao": secao_atual, "perguntas": perguntas,
        "opcoes": ESCOLAR_OPCOES, "pagina": pagina, "total": ESCOLAR_TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / ESCOLAR_TOTAL_PAGINAS * 100),
        "paginas_secoes": [(i + 1, ESCOLAR_SECOES[i]["nome"]) for i in range(ESCOLAR_TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
    })
