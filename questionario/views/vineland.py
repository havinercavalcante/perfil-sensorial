from django.conf import settings
import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Paciente, AvaliacaoVineland, RespostaVineland
from ..data.vineland_data import (
    VINELAND_GRUPOS, VINELAND_PERGUNTAS, VINELAND_CATEGORIA,
    VINELAND_OPCOES, VINELAND_CATEGORIAS_CONFIG,
    calcular_pontuacao_vineland, classificar_qs, grupos_para_idade,
)
from ..services import notificar_terapeuta
from ..tasks import enviar_email
from django.templatetags.static import static


def _calc_idade_meses(data_ref, data_nascimento):
    """Age in months of the patient on data_ref."""
    meses = (data_ref.year - data_nascimento.year) * 12 + (data_ref.month - data_nascimento.month)
    if data_ref.day < data_nascimento.day:
        meses -= 1
    return max(meses, 1)


def _grupos_avaliacao(avaliacao):
    """Groups applicable for the patient's age at assessment date."""
    idade = _calc_idade_meses(avaliacao.data, avaliacao.paciente.data_nascimento)
    return grupos_para_idade(idade)


@login_required
def nova_avaliacao_vineland(request, paciente_id):
    from django.http import JsonResponse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('vineland'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo Vineland.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoVineland.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("vineland_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def vineland_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoVineland, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("vineland_resultado", avaliacao_id=avaliacao_id)

    grupos = _grupos_avaliacao(avaliacao)
    total_paginas = len(grupos)

    if pagina < 1 or pagina > total_paginas:
        return redirect("vineland_form", avaliacao_id=avaliacao_id, pagina=1)

    grupo = grupos[pagina - 1]
    itens = grupo["itens"]
    respostas_salvas = {
        r.numero_item: r.resposta
        for r in avaliacao.respostas.filter(numero_item__in=itens)
    }

    if request.method == "POST":
        novas = {}
        for item in itens:
            val = request.POST.get(f"item_{item}")
            opcoes_validas = [o[0] for o in VINELAND_OPCOES]
            if val in opcoes_validas:
                novas[item] = val

        for item, valor in novas.items():
            RespostaVineland.objects.update_or_create(
                avaliacao=avaliacao, numero_item=item, defaults={"resposta": valor}
            )
        proxima = pagina + 1
        avaliacao.pagina_atual = min(proxima, total_paginas)
        avaliacao.save(update_fields=["pagina_atual"])
        if proxima > total_paginas:
            return redirect("vineland_concluir", avaliacao_id=avaliacao_id)
        return redirect("vineland_form", avaliacao_id=avaliacao_id, pagina=proxima)

    perguntas = [
        {
            "numero": item,
            "texto": VINELAND_PERGUNTAS.get(item, ""),
            "categoria": VINELAND_CATEGORIA.get(item, ""),
            "resposta_salva": respostas_salvas.get(item),
        }
        for item in itens
    ]

    return render(request, "questionario/avaliacoes/vineland_form.html", {
        "avaliacao": avaliacao,
        "grupo": grupo,
        "perguntas": perguntas,
        "opcoes": VINELAND_OPCOES,
        "pagina": pagina,
        "total": total_paginas,
        "progresso": int((pagina - 1) / total_paginas * 100),
        "paginas_grupos": [(i + 1, grupos[i]["nome"]) for i in range(total_paginas)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    })


@login_required
def vineland_concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVineland, uuid=avaliacao_id, paciente__medico=request.user)

    respostas = {r.numero_item: r.resposta for r in avaliacao.respostas.all()}
    p = calcular_pontuacao_vineland(respostas)

    avaliacao.pont_total = p["total"]
    avaliacao.pont_comunicacao = p["C"]
    avaliacao.pont_locomocao = p["L"]
    avaliacao.pont_ocupacao = p["O"]
    avaliacao.pont_socializacao = p["S"]
    avaliacao.pont_autogoverno = p["AG"]
    avaliacao.pont_age = p["AGE"]
    avaliacao.pont_ac = p["AC"]
    avaliacao.pont_av = p["AV"]
    avaliacao.status = "concluida"
    avaliacao.save()
    return redirect("vineland_resultado", avaliacao_id=avaliacao_id)


@login_required
def vineland_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVineland, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if avaliacao.status != "concluida":
        return redirect("vineland_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    if avaliacao.pont_total is None:
        respostas_dict = {r.numero_item: r.resposta for r in avaliacao.respostas.all()}
        p = calcular_pontuacao_vineland(respostas_dict)
        avaliacao.pont_total = p["total"]
        avaliacao.pont_comunicacao = p["C"]
        avaliacao.pont_locomocao = p["L"]
        avaliacao.pont_ocupacao = p["O"]
        avaliacao.pont_socializacao = p["S"]
        avaliacao.pont_autogoverno = p["AG"]
        avaliacao.pont_age = p["AGE"]
        avaliacao.pont_ac = p["AC"]
        avaliacao.pont_av = p["AV"]
        avaliacao.save(update_fields=[
            "pont_total", "pont_comunicacao", "pont_locomocao", "pont_ocupacao",
            "pont_socializacao", "pont_autogoverno", "pont_age", "pont_ac", "pont_av",
        ])

    if request.method == "POST":
        try:
            is_meses = int(request.POST.get("idade_social_meses", "").strip())
            if is_meses <= 0:
                raise ValueError
        except (ValueError, AttributeError):
            messages.error(request, "Digite um valor válido para a Idade Social (número inteiro de meses).")
            is_meses = None

        if is_meses:
            from django.utils import timezone as tz
            hoje = tz.now().date()
            b = paciente.data_nascimento
            ic_meses = (hoje.year - b.year) * 12 + (hoje.month - b.month)
            if hoje.day < b.day:
                ic_meses -= 1
            if ic_meses > 0:
                qs = round(is_meses / ic_meses * 100, 1)
            else:
                qs = None
            avaliacao.idade_social_meses = is_meses
            avaliacao.quociente_social = qs
            avaliacao.save(update_fields=["idade_social_meses", "quociente_social"])
            messages.success(request, "Quociente Social calculado com sucesso.")
            return redirect("vineland_resultado", avaliacao_id=avaliacao_id)

    from django.utils import timezone as tz
    hoje = tz.now().date()
    b = paciente.data_nascimento
    ic_meses = (hoje.year - b.year) * 12 + (hoje.month - b.month)
    if hoje.day < b.day:
        ic_meses -= 1

    CORES_CATEGORIA = {
        "C": "#3E73D1", "L": "#39abcb", "O": "#E8793A", "S": "#9B59B6",
        "AG": "#C0392B", "AGE": "#16A085", "AC": "#D4AC0D", "AV": "#1ABC9C",
    }
    CAMPO_CATEGORIA = {
        "C": "pont_comunicacao", "L": "pont_locomocao",
        "O": "pont_ocupacao", "S": "pont_socializacao",
        "AG": "pont_autogoverno", "AGE": "pont_age",
        "AC": "pont_ac", "AV": "pont_av",
    }

    # Compute age-appropriate max based on groups assessed
    grupos_av = _grupos_avaliacao(avaliacao)
    itens_avaliados = [item for g in grupos_av for item in g["itens"]]
    max_total = len(itens_avaliados)
    max_por_cat = {cod: 0 for cod in VINELAND_CATEGORIAS_CONFIG}
    for item in itens_avaliados:
        cat = VINELAND_CATEGORIA.get(item)
        if cat and cat in max_por_cat:
            max_por_cat[cat] += 1

    faixa_etaria = f"{grupos_av[0]['nome'].split(': ')[1]} → {grupos_av[-1]['nome'].split(': ')[1]}" if len(grupos_av) > 1 else grupos_av[0]['nome'].split(': ')[1]

    categorias = [
        {
            "cod": cod,
            "nome": cfg["nome"],
            "max": max_por_cat[cod],
            "valor": getattr(avaliacao, CAMPO_CATEGORIA[cod]) or 0,
            "cor": CORES_CATEGORIA[cod],
        }
        for cod, cfg in VINELAND_CATEGORIAS_CONFIG.items()
        if max_por_cat[cod] > 0
    ]

    categorias_json = json.dumps([
        {
            "nome": c["nome"],
            "valor": float(c["valor"]),
            "max": c["max"],
            "pct": round(float(c["valor"]) / c["max"] * 100) if c["max"] else 0,
            "cor": c["cor"],
        }
        for c in categorias
    ])

    qs_class = classificar_qs(avaliacao.quociente_social) if avaliacao.quociente_social else None

    todas_av = list(paciente.avaliacoes_vineland.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_av if av.id != avaliacao.id]
    comparativo_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_av])
    dominios_comp = [
        {"nome": "Comunicação",  "campo": "pont_comunicacao",  "max": 28},
        {"nome": "Locomoção",    "campo": "pont_locomocao",    "max": 28},
        {"nome": "Ocupação",     "campo": "pont_ocupacao",     "max": 28},
        {"nome": "Socialização", "campo": "pont_socializacao", "max": 28},
        {"nome": "Autogoverno",  "campo": "pont_autogoverno",  "max": 28},
    ]
    cores_linha = ["#2E7D6B", "#3E73D1", "#E8793A", "#9B59B6", "#E8B84B"]
    comparativo_datasets = []
    for i, dom in enumerate(dominios_comp):
        valores = [round((getattr(av, dom["campo"]) or 0) / dom["max"] * 100) for av in todas_av]
        comparativo_datasets.append({"label": dom["nome"], "data": valores, "borderColor": cores_linha[i], "backgroundColor": cores_linha[i] + "33", "tension": 0.3})

    return render(request, "questionario/avaliacoes/vineland_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "ic_meses": ic_meses,
        "categorias": categorias,
        "categorias_json": categorias_json,
        "max_total": max_total,
        "faixa_etaria": faixa_etaria,
        "qs_classificacao": qs_class,
        "comparativo_labels": comparativo_labels,
        "comparativo_datasets": json.dumps(comparativo_datasets),
        "tem_comparativo": len(todas_av) > 1,
        "outras_avaliacoes": outras,
    })


@login_required
def vineland_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoVineland, uuid=avaliacao_id, paciente__medico=request.user)
    grupos = _grupos_avaliacao(avaliacao)
    total_paginas = len(grupos)

    if pagina < 1 or pagina > total_paginas:
        return redirect("vineland_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    grupo = grupos[pagina - 1]
    itens = grupo["itens"]
    respostas_salvas = {r.numero_item: r.resposta for r in avaliacao.respostas.filter(numero_item__in=itens)}

    perguntas = [
        {"numero": item, "texto": VINELAND_PERGUNTAS.get(item, ""), "categoria": VINELAND_CATEGORIA.get(item, ""),
         "resposta_salva": respostas_salvas.get(item)}
        for item in itens
    ]
    return render(request, "questionario/avaliacoes/vineland_form.html", {
        "avaliacao": avaliacao, "grupo": grupo, "perguntas": perguntas,
        "opcoes": VINELAND_OPCOES, "pagina": pagina, "total": total_paginas,
        "progresso": int((pagina - 1) / total_paginas * 100),
        "paginas_grupos": [(i + 1, grupos[i]["nome"]) for i in range(total_paginas)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "readonly": True,
    })


@login_required
def vineland_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoVineland, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação Vineland excluída com sucesso."})
        messages.success(request, "Avaliação Vineland excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


def vineland_publico_view(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoVineland, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")

    grupos = _grupos_avaliacao(avaliacao)
    total_paginas = len(grupos)

    if pagina < 1 or pagina > total_paginas:
        pagina = 1

    grupo = grupos[pagina - 1]
    itens = grupo["itens"]
    respostas_salvas = {
        r.numero_item: r.resposta
        for r in avaliacao.respostas.filter(numero_item__in=itens)
    }

    if request.method == "POST":
        novas = {}
        for item in itens:
            val = request.POST.get(f"item_{item}")
            opcoes_validas = [o[0] for o in VINELAND_OPCOES]
            if val in opcoes_validas:
                novas[item] = val

        for item, valor in novas.items():
            RespostaVineland.objects.update_or_create(
                avaliacao=avaliacao, numero_item=item, defaults={"resposta": valor}
            )
        proxima = pagina + 1
        avaliacao.pagina_atual = min(proxima, total_paginas)
        avaliacao.save(update_fields=["pagina_atual"])
        if proxima > total_paginas:
            respostas_dict = {r.numero_item: r.resposta for r in avaliacao.respostas.all()}
            p = calcular_pontuacao_vineland(respostas_dict)
            avaliacao.pont_total = p["total"]
            avaliacao.pont_comunicacao = p["C"]
            avaliacao.pont_locomocao = p["L"]
            avaliacao.pont_ocupacao = p["O"]
            avaliacao.pont_socializacao = p["S"]
            avaliacao.pont_autogoverno = p["AG"]
            avaliacao.pont_age = p["AGE"]
            avaliacao.pont_ac = p["AC"]
            avaliacao.pont_av = p["AV"]
            avaliacao.status = "concluida"
            avaliacao.save()
            try:
                notificar_terapeuta(avaliacao.paciente, "vineland", request)
            except Exception:
                pass
            return render(request, "questionario/dashboard/concluido.html")
        return redirect("vineland_publico", token=token, pagina=proxima)

    perguntas = [
        {
            "numero": item,
            "texto": VINELAND_PERGUNTAS.get(item, ""),
            "categoria": VINELAND_CATEGORIA.get(item, ""),
            "resposta_salva": respostas_salvas.get(item),
        }
        for item in itens
    ]

    return render(request, "questionario/avaliacoes/vineland_form.html", {
        "avaliacao": avaliacao,
        "grupo": grupo,
        "perguntas": perguntas,
        "opcoes": VINELAND_OPCOES,
        "pagina": pagina,
        "total": total_paginas,
        "progresso": int((pagina - 1) / total_paginas * 100),
        "paginas_grupos": [(i + 1, grupos[i]["nome"]) for i in range(total_paginas)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
        "token": token,
    })


@login_required
def enviar_email_link_vineland(request, avaliacao_id):
    from django.utils import timezone as tz
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoVineland, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    from django.template.loader import render_to_string
    link = request.build_absolute_uri(f"/vineland/publico/{avaliacao.token}/1/")
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        enviar_email.delay(
            subject="Escala Vineland — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nResponda a Escala Vineland no link: {link}",
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


@login_required
def salvar_observacoes_vineland(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoVineland, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("vineland_resultado", avaliacao_id=avaliacao_id)
    return redirect("vineland_resultado", avaliacao_id=avaliacao_id)
