import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Paciente, AvaliacaoVineland3, RespostaVineland3
from ..vineland3_data import (
    VINELAND3_SECOES,
    VINELAND3_PERGUNTAS,
    VINELAND3_OPCOES,
    calcular_pontuacao_vineland3,
    VINELAND3_MAXIMOS,
)
from ..services import notificar_terapeuta


def _v3_salvar_pontuacao(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    p = calcular_pontuacao_vineland3(respostas)
    avaliacao.pont_com   = p.get("com", 0)
    avaliacao.pont_avd   = p.get("avd", 0)
    avaliacao.pont_soc   = p.get("soc", 0)
    avaliacao.pont_hmot  = p.get("hmot", 0)
    avaliacao.pont_total = p.get("total_adaptativo", 0)
    avaliacao.pont_pc_a  = p.get("pc_a", 0)
    avaliacao.pont_pc_b  = p.get("pc_b", 0)
    avaliacao.pont_pc_c  = p.get("pc_c", 0)
    return avaliacao


def _v3_build_dominios(avaliacao):
    configs = [
        {"sigla": "COM",  "nome": "Comunicação",                          "cor": "#1D6FA4", "valor": avaliacao.pont_com,  "maximo": VINELAND3_MAXIMOS["com"]},
        {"sigla": "AVD",  "nome": "Atividade de Vida Diária",             "cor": "#27AE60", "valor": avaliacao.pont_avd,  "maximo": VINELAND3_MAXIMOS["avd"]},
        {"sigla": "SOC",  "nome": "Habilidades Sociais e Relacionamentos","cor": "#8E44AD", "valor": avaliacao.pont_soc,  "maximo": VINELAND3_MAXIMOS["soc"]},
        {"sigla": "HMOT", "nome": "Atividade Física / Habilidades Motoras","cor": "#E67E22","valor": avaliacao.pont_hmot, "maximo": VINELAND3_MAXIMOS["hmot"]},
    ]
    for d in configs:
        d["valor"] = d["valor"] or 0
        d["pct"] = int(d["valor"] / d["maximo"] * 100) if d["maximo"] else 0
    return configs


def _v3_build_pc(avaliacao):
    return [
        {"sigla": "PC-A", "nome": "Seção A (Internalização)",      "cor": "#C0392B", "valor": avaliacao.pont_pc_a or 0, "maximo": VINELAND3_MAXIMOS["pc_a"]},
        {"sigla": "PC-B", "nome": "Seção B (Externalização)",       "cor": "#922B21", "valor": avaliacao.pont_pc_b or 0, "maximo": VINELAND3_MAXIMOS["pc_b"]},
        {"sigla": "PC-C", "nome": "Seção C (Outros Problemas)",     "cor": "#7B241C", "valor": avaliacao.pont_pc_c or 0, "maximo": VINELAND3_MAXIMOS["pc_c"]},
    ]


# ── Views autenticadas ────────────────────────────────────────────────────────

@login_required
def nova_avaliacao_vineland3(request, paciente_id):
    from django.http import JsonResponse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('vineland3'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo Vineland-3.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoVineland3.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "id": av.id})
    return redirect("vineland3_form", avaliacao_id=av.id, pagina=1)


@login_required
def vineland3_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoVineland3, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("vineland3_resultado", avaliacao_id=avaliacao_id)

    total_paginas = len(VINELAND3_SECOES)
    if pagina < 1 or pagina > total_paginas:
        return redirect("vineland3_form", avaliacao_id=avaliacao_id, pagina=1)

    secao_atual = VINELAND3_SECOES[pagina - 1]
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
                    if v in (0, 1, 2):
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
                RespostaVineland3.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={"valor": valor}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, total_paginas)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > total_paginas:
                return redirect("vineland3_concluir", avaliacao_id=avaliacao_id)
            return redirect("vineland3_form", avaliacao_id=avaliacao_id, pagina=proxima)

    perguntas = [
        {
            "numero": item,
            "numero_local": item - itens[0] + 1,
            "texto": VINELAND3_PERGUNTAS.get(item, ""),
            "resposta_salva": respostas_salvas.get(item),
        }
        for item in itens
    ]
    return render(request, "questionario/vineland3_form.html", {
        "avaliacao": avaliacao,
        "secao": secao_atual,
        "perguntas": perguntas,
        "opcoes": VINELAND3_OPCOES,
        "pagina": pagina,
        "total": total_paginas,
        "progresso": int((pagina - 1) / total_paginas * 100),
        "paginas_secoes": [(i + 1, VINELAND3_SECOES[i]["nome"]) for i in range(total_paginas)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    })


@login_required
def vineland3_concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVineland3, id=avaliacao_id, paciente__medico=request.user)
    avaliacao = _v3_salvar_pontuacao(avaliacao)
    avaliacao.status = "concluida"
    avaliacao.save()
    return redirect("vineland3_resultado", avaliacao_id=avaliacao_id)


@login_required
def vineland3_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVineland3, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if avaliacao.status != "concluida":
        return redirect("vineland3_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    if avaliacao.pont_total is None:
        avaliacao = _v3_salvar_pontuacao(avaliacao)
        avaliacao.save(update_fields=[
            "pont_com", "pont_avd", "pont_soc", "pont_hmot",
            "pont_total", "pont_pc_a", "pont_pc_b", "pont_pc_c",
        ])

    dominios = _v3_build_dominios(avaliacao)
    pc = _v3_build_pc(avaliacao)
    max_total = VINELAND3_MAXIMOS["com"] + VINELAND3_MAXIMOS["avd"] + VINELAND3_MAXIMOS["soc"] + VINELAND3_MAXIMOS["hmot"]
    pct_total = int((avaliacao.pont_total or 0) / max_total * 100) if max_total else 0

    return render(request, "questionario/vineland3_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "dominios": dominios,
        "pc": pc,
        "pct_total": pct_total,
        "max_total": max_total,
        "dominios_json": json.dumps([{"nome": d["sigla"], "pct": d["pct"], "cor": d["cor"]} for d in dominios]),
    })


@login_required
def vineland3_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoVineland3, id=avaliacao_id, paciente__medico=request.user)
    total_paginas = len(VINELAND3_SECOES)

    if pagina < 1 or pagina > total_paginas:
        return redirect("vineland3_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    secao_atual = VINELAND3_SECOES[pagina - 1]
    itens = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens)}

    perguntas = [
        {
            "numero": item,
            "numero_local": item - itens[0] + 1,
            "texto": VINELAND3_PERGUNTAS.get(item, ""),
            "resposta_salva": respostas_salvas.get(item),
        }
        for item in itens
    ]
    return render(request, "questionario/vineland3_form.html", {
        "avaliacao": avaliacao,
        "secao": secao_atual,
        "perguntas": perguntas,
        "opcoes": VINELAND3_OPCOES,
        "pagina": pagina,
        "total": total_paginas,
        "progresso": int((pagina - 1) / total_paginas * 100),
        "paginas_secoes": [(i + 1, VINELAND3_SECOES[i]["nome"]) for i in range(total_paginas)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "readonly": True,
    })


@login_required
def vineland3_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoVineland3, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação Vineland-3 excluída com sucesso."})
        messages.success(request, "Avaliação Vineland-3 excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_vineland3(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoVineland3, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("vineland3_resultado", avaliacao_id=avaliacao_id)
    return redirect("vineland3_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_vineland3(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.http import JsonResponse
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoVineland3, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    link = request.build_absolute_uri(f"/vineland3/publico/{avaliacao.token}/1/")
    send_mail(
        subject="Vineland-3 — IntegraMente",
        message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário Vineland-3 no link: {link}",
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


# ── View pública (sem login) ──────────────────────────────────────────────────

def vineland3_publico_view(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoVineland3, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/concluido.html")

    total = len(VINELAND3_SECOES)
    if pagina < 1 or pagina > total:
        pagina = 1
    secao_atual = VINELAND3_SECOES[pagina - 1]
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
                    if v in (0, 1, 2):
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
                RespostaVineland3.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={"valor": valor}
                )
            if pagina < total:
                avaliacao.pagina_atual = pagina + 1
                avaliacao.save(update_fields=["pagina_atual"])
                return redirect("vineland3_publico", token=token, pagina=pagina + 1)
            else:
                avaliacao = _v3_salvar_pontuacao(avaliacao)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    notificar_terapeuta(avaliacao.paciente, "vineland3", request)
                except Exception:
                    pass
                return render(request, "questionario/concluido.html")

    perguntas = [
        {
            "numero": item,
            "numero_local": item - itens[0] + 1,
            "texto": VINELAND3_PERGUNTAS.get(item, ""),
            "resposta_salva": respostas_salvas.get(item),
        }
        for item in itens
    ]
    return render(request, "questionario/vineland3_form.html", {
        "avaliacao": avaliacao,
        "secao": secao_atual,
        "perguntas": perguntas,
        "opcoes": VINELAND3_OPCOES,
        "pagina": pagina,
        "total": total,
        "progresso": int((pagina - 1) / total * 100),
        "paginas_secoes": [(i + 1, VINELAND3_SECOES[i]["nome"]) for i in range(total)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
    })
