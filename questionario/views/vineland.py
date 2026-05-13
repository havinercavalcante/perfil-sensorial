import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Paciente, AvaliacaoVineland, RespostaVineland
from ..vineland_data import (
    VINELAND_GRUPOS, VINELAND_PERGUNTAS, VINELAND_CATEGORIA,
    VINELAND_OPCOES, VINELAND_CATEGORIAS_CONFIG,
    calcular_pontuacao_vineland, classificar_qs,
)
from ..services import notificar_terapeuta

VINELAND_TOTAL_PAGINAS = len(VINELAND_GRUPOS)


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
        return JsonResponse({"ok": True, "id": av.id})
    return redirect("vineland_form", avaliacao_id=av.id, pagina=1)


@login_required
def vineland_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("vineland_resultado", avaliacao_id=avaliacao_id)

    if pagina < 1 or pagina > VINELAND_TOTAL_PAGINAS:
        return redirect("vineland_form", avaliacao_id=avaliacao_id, pagina=1)

    grupo = VINELAND_GRUPOS[pagina - 1]
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
        avaliacao.pagina_atual = min(proxima, VINELAND_TOTAL_PAGINAS)
        avaliacao.save(update_fields=["pagina_atual"])
        if proxima > VINELAND_TOTAL_PAGINAS:
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

    return render(request, "questionario/vineland_form.html", {
        "avaliacao": avaliacao,
        "grupo": grupo,
        "perguntas": perguntas,
        "opcoes": VINELAND_OPCOES,
        "pagina": pagina,
        "total": VINELAND_TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / VINELAND_TOTAL_PAGINAS * 100),
        "paginas_grupos": [(i + 1, VINELAND_GRUPOS[i]["nome"]) for i in range(VINELAND_TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    })


@login_required
def vineland_concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)

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
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
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

    categorias = [
        {
            "cod": cod,
            "nome": cfg["nome"],
            "max": cfg["max"],
            "valor": getattr(avaliacao, {
                "C": "pont_comunicacao", "L": "pont_locomocao",
                "O": "pont_ocupacao", "S": "pont_socializacao",
                "AG": "pont_autogoverno", "AGE": "pont_age",
                "AC": "pont_ac", "AV": "pont_av",
            }[cod]) or 0,
        }
        for cod, cfg in VINELAND_CATEGORIAS_CONFIG.items()
    ]

    qs_class = classificar_qs(avaliacao.quociente_social) if avaliacao.quociente_social else None

    return render(request, "questionario/vineland_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "ic_meses": ic_meses,
        "categorias": categorias,
        "qs_classificacao": qs_class,
    })


@login_required
def vineland_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > VINELAND_TOTAL_PAGINAS:
        return redirect("vineland_visualizar", avaliacao_id=avaliacao_id, pagina=1)

    grupo = VINELAND_GRUPOS[pagina - 1]
    itens = grupo["itens"]
    respostas_salvas = {r.numero_item: r.resposta for r in avaliacao.respostas.filter(numero_item__in=itens)}

    perguntas = [
        {"numero": item, "texto": VINELAND_PERGUNTAS.get(item, ""), "categoria": VINELAND_CATEGORIA.get(item, ""),
         "resposta_salva": respostas_salvas.get(item)}
        for item in itens
    ]
    return render(request, "questionario/vineland_form.html", {
        "avaliacao": avaliacao, "grupo": grupo, "perguntas": perguntas,
        "opcoes": VINELAND_OPCOES, "pagina": pagina, "total": VINELAND_TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / VINELAND_TOTAL_PAGINAS * 100),
        "paginas_grupos": [(i + 1, VINELAND_GRUPOS[i]["nome"]) for i in range(VINELAND_TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "readonly": True,
    })


@login_required
def vineland_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
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
        return render(request, "questionario/concluido.html")

    if pagina < 1 or pagina > VINELAND_TOTAL_PAGINAS:
        pagina = 1

    grupo = VINELAND_GRUPOS[pagina - 1]
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
        avaliacao.pagina_atual = min(proxima, VINELAND_TOTAL_PAGINAS)
        avaliacao.save(update_fields=["pagina_atual"])
        if proxima > VINELAND_TOTAL_PAGINAS:
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
            return render(request, "questionario/concluido.html")
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

    return render(request, "questionario/vineland_form.html", {
        "avaliacao": avaliacao,
        "grupo": grupo,
        "perguntas": perguntas,
        "opcoes": VINELAND_OPCOES,
        "pagina": pagina,
        "total": VINELAND_TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / VINELAND_TOTAL_PAGINAS * 100),
        "paginas_grupos": [(i + 1, VINELAND_GRUPOS[i]["nome"]) for i in range(VINELAND_TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
        "token": token,
    })


@login_required
def enviar_email_link_vineland(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    link = request.build_absolute_uri(f"/vineland/publico/{avaliacao.token}/1/")
    send_mail(
        subject="Escala Vineland — CeciSys",
        message=f"Olá, {paciente.responsavel}!\n\nResponda a Escala Vineland no link: {link}",
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


@login_required
def salvar_observacoes_vineland(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("vineland_resultado", avaliacao_id=avaliacao_id)
    return redirect("vineland_resultado", avaliacao_id=avaliacao_id)
