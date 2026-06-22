from django.conf import settings
import uuid as _uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import (
    Paciente,
    AvaliacaoRecordatorio,
    EntradaRecordatorio,
    InventarioAlimento,
    AvaliacaoAnamnese,
    REFEICAO_CHOICES,
)
from ..tasks import enviar_email
from django.templatetags.static import static

TOTAL_PAGINAS_RECORDATORIO = 6
TOTAL_PAGINAS_ANAMNESE = 2

TIPO_MAP = {"4": "recusado", "5": "familiar", "6": "aceito"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _salvar_pagina_recordatorio(request, avaliacao, pagina):
    """Save form data for a single recordatorio page."""
    if pagina <= 3:
        dia = str(pagina)
        for refeicao, _ in REFEICAO_CHOICES:
            horario = request.POST.get(f"{refeicao}_horario", "").strip()
            o_que = request.POST.get(f"{refeicao}_o_que", "").strip()
            onde = request.POST.get(f"{refeicao}_onde", "").strip()
            com_quem = request.POST.get(f"{refeicao}_com_quem", "").strip()
            EntradaRecordatorio.objects.update_or_create(
                avaliacao=avaliacao, dia=dia, refeicao=refeicao,
                defaults={"horario": horario, "o_que_comeu": o_que, "onde": onde, "com_quem": com_quem}
            )
    else:
        tipo = TIPO_MAP[str(pagina)]
        avaliacao.inventario.filter(tipo=tipo).delete()
        rows = []
        i = 0
        while True:
            alimento = request.POST.get(f"alimento_{i}", "").strip()
            if not alimento and i >= 5:
                break
            if alimento:
                rows.append(InventarioAlimento(
                    avaliacao=avaliacao, tipo=tipo, ordem=i,
                    alimento=alimento,
                    preparo=request.POST.get(f"preparo_{i}", ""),
                    horario=request.POST.get(f"horario_{i}", ""),
                    observacao=request.POST.get(f"observacao_{i}", ""),
                    tempo=request.POST.get(f"tempo_{i}", "") if tipo == "recusado" else "",
                ))
            i += 1
            if i > 50:
                break
        InventarioAlimento.objects.bulk_create(rows)


def _get_entradas_dia(avaliacao, dia):
    """Return a dict of refeicao -> EntradaRecordatorio for a given dia."""
    entradas = {e.refeicao: e for e in avaliacao.entradas.filter(dia=str(dia))}
    return entradas


def _get_inventario_tipo(avaliacao, tipo):
    return list(avaliacao.inventario.filter(tipo=tipo).order_by("ordem"))


# ── Recordatório: views autenticadas ─────────────────────────────────────────

@login_required
def nova_avaliacao_recordatorio(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('recordatorio_alimentar'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo Recordatório Alimentar.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoRecordatorio.objects.create(paciente=paciente, token=str(_uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("recordatorio_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def recordatorio_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoRecordatorio, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("recordatorio_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS_RECORDATORIO:
        return redirect("recordatorio_form", avaliacao_id=avaliacao_id, pagina=1)

    if request.method == "POST":
        _salvar_pagina_recordatorio(request, avaliacao, pagina)
        proxima = pagina + 1
        avaliacao.pagina_atual = min(proxima, TOTAL_PAGINAS_RECORDATORIO)
        avaliacao.save(update_fields=["pagina_atual"])
        if proxima > TOTAL_PAGINAS_RECORDATORIO:
            avaliacao.status = "concluida"
            avaliacao.save(update_fields=["status"])
            return redirect("recordatorio_resultado", avaliacao_id=avaliacao_id)
        return redirect("recordatorio_form", avaliacao_id=avaliacao_id, pagina=proxima)

    ctx = _build_recordatorio_context(avaliacao, pagina, readonly=False, publico=False)
    return render(request, "questionario/avaliacoes/recordatorio_form.html", ctx)


@login_required
def recordatorio_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoRecordatorio, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("recordatorio_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)
    ctx = _build_resultado_recordatorio(avaliacao)
    return render(request, "questionario/avaliacoes/recordatorio_resultado.html", ctx)


@login_required
def recordatorio_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoRecordatorio, uuid=avaliacao_id, paciente__medico=request.user)
    if pagina < 1 or pagina > TOTAL_PAGINAS_RECORDATORIO:
        return redirect("recordatorio_visualizar", avaliacao_id=avaliacao_id, pagina=1)
    ctx = _build_recordatorio_context(avaliacao, pagina, readonly=True, publico=False)
    return render(request, "questionario/avaliacoes/recordatorio_form.html", ctx)


@login_required
def recordatorio_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoRecordatorio, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Recordatório excluído com sucesso."})
        messages.success(request, "Recordatório excluído com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def enviar_email_recordatorio(request, avaliacao_id):
    from django.utils import timezone as tz
    from django.template.loader import render_to_string

    avaliacao = get_object_or_404(AvaliacaoRecordatorio, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)

    link = request.build_absolute_uri(f"/recordatorio/publico/{avaliacao.token}/1/")
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        enviar_email.delay(
            subject="Recordatório Alimentar — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nPreencha o Recordatório Alimentar no link: {link}",
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
def salvar_observacoes_recordatorio(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoRecordatorio, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("recordatorio_resultado", avaliacao_id=avaliacao_id)


# ── Recordatório: link público ────────────────────────────────────────────────

def recordatorio_publico_view(request, token, pagina):
    from ..services import notificar_terapeuta
    avaliacao = get_object_or_404(AvaliacaoRecordatorio, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/dashboard/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS_RECORDATORIO:
        return redirect("recordatorio_publico", token=token, pagina=1)

    if request.method == "POST":
        _salvar_pagina_recordatorio(request, avaliacao, pagina)
        proxima = pagina + 1
        avaliacao.pagina_atual = min(proxima, TOTAL_PAGINAS_RECORDATORIO)
        avaliacao.save(update_fields=["pagina_atual"])
        if proxima > TOTAL_PAGINAS_RECORDATORIO:
            avaliacao.status = "concluida"
            avaliacao.save(update_fields=["status"])
            try:
                notificar_terapeuta(avaliacao.paciente, "recordatorio_alimentar", request)
            except Exception:
                pass
            return render(request, "questionario/dashboard/concluido.html")
        return redirect("recordatorio_publico", token=token, pagina=proxima)

    ctx = _build_recordatorio_context(avaliacao, pagina, readonly=False, publico=True, token=token)
    return render(request, "questionario/avaliacoes/recordatorio_form.html", ctx)


# ── Recordatório: context builders ────────────────────────────────────────────

def _build_recordatorio_context(avaliacao, pagina, *, readonly, publico, token=None):
    paciente = avaliacao.paciente
    progresso = int((pagina - 1) / TOTAL_PAGINAS_RECORDATORIO * 100)

    titulos = [
        "Dia 1 — Dia de semana",
        "Dia 2 — Dia de semana",
        "Dia 3 — Fim de semana",
        "Alimentos que a criança DEIXOU DE COMER",
        "Alimentos do CARDÁPIO FAMILIAR",
        "Alimentos que a criança COME ATUALMENTE",
    ]

    ctx = {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "pagina": pagina,
        "total": TOTAL_PAGINAS_RECORDATORIO,
        "progresso": progresso,
        "titulo_pagina": titulos[pagina - 1],
        "readonly": readonly,
        "publico": publico,
        "token": token,
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    }

    if pagina <= 3:
        entradas_dict = _get_entradas_dia(avaliacao, pagina)
        # Build list of (code, label, entrada_or_None) for easy template iteration
        refeicoes_com_entrada = [
            (code, label, entradas_dict.get(code))
            for code, label in REFEICAO_CHOICES
        ]
        ctx["refeicoes_com_entrada"] = refeicoes_com_entrada
        ctx["tipo_pagina"] = "recordatorio"
    else:
        tipo = TIPO_MAP[str(pagina)]
        ctx["inventario"] = _get_inventario_tipo(avaliacao, tipo)
        ctx["tipo_inventario"] = tipo
        ctx["tipo_pagina"] = "inventario"

    return ctx


def _build_resultado_recordatorio(avaliacao):
    paciente = avaliacao.paciente
    dias = []
    for d, label in [("1", "Dia 1 — Semana"), ("2", "Dia 2 — Semana"), ("3", "Dia 3 — Fim de semana")]:
        entradas_dict = _get_entradas_dia(avaliacao, d)
        # Build list of (label, entrada_or_None) for template iteration
        refeicoes_linhas = [
            (rf_label, entradas_dict.get(code))
            for code, rf_label in REFEICAO_CHOICES
        ]
        dias.append({"label": label, "refeicoes_linhas": refeicoes_linhas})

    return {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "dias": dias,
        "recusados": _get_inventario_tipo(avaliacao, "recusado"),
        "familiares": _get_inventario_tipo(avaliacao, "familiar"),
        "aceitos": _get_inventario_tipo(avaliacao, "aceito"),
    }


# ── Anamnese: views ────────────────────────────────────────────────────────────

@login_required
def nova_avaliacao_anamnese(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('anamnese_alimentar'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo Anamnese Alimentar.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoAnamnese.objects.create(paciente=paciente)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("anamnese_form", avaliacao_id=av.uuid, pagina=1)


@login_required
def anamnese_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoAnamnese, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("anamnese_resultado", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS_ANAMNESE:
        return redirect("anamnese_form", avaliacao_id=avaliacao_id, pagina=1)

    if request.method == "POST":
        _salvar_anamnese_pagina(request, avaliacao, pagina)
        proxima = pagina + 1
        avaliacao.pagina_atual = min(proxima, TOTAL_PAGINAS_ANAMNESE)
        avaliacao.save(update_fields=["pagina_atual"])
        if proxima > TOTAL_PAGINAS_ANAMNESE:
            avaliacao.status = "concluida"
            avaliacao.save(update_fields=["status"])
            return redirect("anamnese_resultado", avaliacao_id=avaliacao_id)
        return redirect("anamnese_form", avaliacao_id=avaliacao_id, pagina=proxima)

    ctx = _build_anamnese_context(avaliacao, pagina)
    return render(request, "questionario/avaliacoes/anamnese_form.html", ctx)


@login_required
def anamnese_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAnamnese, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("anamnese_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)
    return render(request, "questionario/avaliacoes/anamnese_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "hist_itens": _hist_itens(avaliacao),
        "func_itens": _func_itens(avaliacao),
        "sensorial_grupos": _sensorial_grupos(avaliacao),
    })


@login_required
def anamnese_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAnamnese, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Anamnese excluída com sucesso."})
        messages.success(request, "Anamnese excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_anamnese(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAnamnese, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("anamnese_resultado", avaliacao_id=avaliacao_id)


# ── Anamnese helpers ──────────────────────────────────────────────────────────

def _salvar_anamnese_pagina(request, avaliacao, pagina):
    p = request.POST
    if pagina == 1:
        avaliacao.hist_alergia = "hist_alergia" in p
        avaliacao.hist_refluxo = "hist_refluxo" in p
        avaliacao.hist_prob_gi = "hist_prob_gi" in p
        avaliacao.hist_dif_respiratoria = "hist_dif_respiratoria" in p
        avaliacao.hist_baixo_peso = "hist_baixo_peso" in p
        avaliacao.hist_prematuridade = "hist_prematuridade" in p
        avaliacao.hist_tonus = "hist_tonus" in p
        avaliacao.hist_explane = p.get("hist_explane", "").strip()

        avaliacao.func_amamentacao = "func_amamentacao" in p
        avaliacao.func_mamadeira = "func_mamadeira" in p
        avaliacao.func_papinhas = "func_papinhas" in p
        avaliacao.func_solidos = "func_solidos" in p
        avaliacao.func_maos = "func_maos" in p
        avaliacao.func_utensilios = "func_utensilios" in p
        avaliacao.func_copo = "func_copo" in p
        avaliacao.func_explane = p.get("func_explane", "").strip()
        avaliacao.historico_declinio = p.get("historico_declinio", "").strip()
        avaliacao.save(update_fields=[
            "hist_alergia", "hist_refluxo", "hist_prob_gi", "hist_dif_respiratoria",
            "hist_baixo_peso", "hist_prematuridade", "hist_tonus", "hist_explane",
            "func_amamentacao", "func_mamadeira", "func_papinhas", "func_solidos",
            "func_maos", "func_utensilios", "func_copo", "func_explane", "historico_declinio",
        ])
    elif pagina == 2:
        sensorial_fields = [
            "sens_visual_forma", "sens_visual_cor", "sens_visual_tamanho", "sens_visual_outros",
            "sens_olfato_pouco", "sens_olfato_intenso", "sens_olfato_nao_importa", "sens_olfato_outros",
            "sens_tato_frio", "sens_tato_quente", "sens_tato_morno",
            "sens_tato_mole", "sens_tato_dura", "sens_tato_semi_dura",
            "sens_tato_liso", "sens_tato_rugoso", "sens_tato_aspero",
            "sens_tato_pegajoso", "sens_tato_seco", "sens_tato_umido",
            "sens_propr_complexos", "sens_propr_simples", "sens_propr_forca", "sens_propr_resistencia",
            "sens_gosto_doce", "sens_gosto_salgado", "sens_gosto_amargo",
            "sens_gosto_acido", "sens_gosto_umami",
            "sens_audit_barulho", "sens_audit_crocante", "sens_audit_silencioso",
        ]
        for f in sensorial_fields:
            setattr(avaliacao, f, p.get(f, "").strip())
        avaliacao.save(update_fields=sensorial_fields)


def _build_anamnese_context(avaliacao, pagina):
    ctx = {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "pagina": pagina,
        "total": TOTAL_PAGINAS_ANAMNESE,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS_ANAMNESE * 100),
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    }
    if pagina == 2:
        ctx["grupos"] = _sensorial_grupos_for_form(avaliacao)
    return ctx


def _sensorial_grupos_for_form(avaliacao):
    """Like _sensorial_grupos but includes the field_name for the form."""
    return [
        {
            "nome": "VISUAL",
            "itens": [
                ("Forma", avaliacao.sens_visual_forma, "sens_visual_forma"),
                ("Cor", avaliacao.sens_visual_cor, "sens_visual_cor"),
                ("Tamanho", avaliacao.sens_visual_tamanho, "sens_visual_tamanho"),
                ("Outros", avaliacao.sens_visual_outros, "sens_visual_outros"),
            ],
        },
        {
            "nome": "OLFATO",
            "itens": [
                ("Alimentos de pouco odor", avaliacao.sens_olfato_pouco, "sens_olfato_pouco"),
                ("Alimentos com odores intensos", avaliacao.sens_olfato_intenso, "sens_olfato_intenso"),
                ("Os odores não importam", avaliacao.sens_olfato_nao_importa, "sens_olfato_nao_importa"),
                ("Outros", avaliacao.sens_olfato_outros, "sens_olfato_outros"),
            ],
        },
        {
            "nome": "TATO",
            "itens": [
                ("Temperatura: Frio", avaliacao.sens_tato_frio, "sens_tato_frio"),
                ("Temperatura: Quente", avaliacao.sens_tato_quente, "sens_tato_quente"),
                ("Temperatura: Morno", avaliacao.sens_tato_morno, "sens_tato_morno"),
                ("Consistência: Mole", avaliacao.sens_tato_mole, "sens_tato_mole"),
                ("Consistência: Dura", avaliacao.sens_tato_dura, "sens_tato_dura"),
                ("Consistência: Semi-dura", avaliacao.sens_tato_semi_dura, "sens_tato_semi_dura"),
                ("Textura: Liso/Suave", avaliacao.sens_tato_liso, "sens_tato_liso"),
                ("Textura: Rugoso/Texturizado", avaliacao.sens_tato_rugoso, "sens_tato_rugoso"),
                ("Textura: Áspero", avaliacao.sens_tato_aspero, "sens_tato_aspero"),
                ("Textura: Pegajoso", avaliacao.sens_tato_pegajoso, "sens_tato_pegajoso"),
                ("Umidade: Seco", avaliacao.sens_tato_seco, "sens_tato_seco"),
                ("Umidade: Úmido/Molhado", avaliacao.sens_tato_umido, "sens_tato_umido"),
            ],
        },
        {
            "nome": "PROPRIOCEPÇÃO / VESTIBULAR",
            "itens": [
                ("Movimentos complexos", avaliacao.sens_propr_complexos, "sens_propr_complexos"),
                ("Movimentos simples", avaliacao.sens_propr_simples, "sens_propr_simples"),
                ("Força", avaliacao.sens_propr_forca, "sens_propr_forca"),
                ("Resistência", avaliacao.sens_propr_resistencia, "sens_propr_resistencia"),
            ],
        },
        {
            "nome": "GOSTO",
            "itens": [
                ("Doce", avaliacao.sens_gosto_doce, "sens_gosto_doce"),
                ("Salgado", avaliacao.sens_gosto_salgado, "sens_gosto_salgado"),
                ("Amargo", avaliacao.sens_gosto_amargo, "sens_gosto_amargo"),
                ("Ácido", avaliacao.sens_gosto_acido, "sens_gosto_acido"),
                ("Umami", avaliacao.sens_gosto_umami, "sens_gosto_umami"),
            ],
        },
        {
            "nome": "AUDITIVO",
            "itens": [
                ("Muito barulho", avaliacao.sens_audit_barulho, "sens_audit_barulho"),
                ("Crocante", avaliacao.sens_audit_crocante, "sens_audit_crocante"),
                ("Silencioso", avaliacao.sens_audit_silencioso, "sens_audit_silencioso"),
            ],
        },
    ]


def _hist_itens(avaliacao):
    return [
        ("Alergia alimentar", avaliacao.hist_alergia),
        ("Refluxo", avaliacao.hist_refluxo),
        ("Outro problema gastrointestinal", avaliacao.hist_prob_gi),
        ("Dificuldade respiratória", avaliacao.hist_dif_respiratoria),
        ("Baixo peso ao nascer", avaliacao.hist_baixo_peso),
        ("Prematuridade", avaliacao.hist_prematuridade),
        ("Alterações de tônus muscular", avaliacao.hist_tonus),
    ]


def _func_itens(avaliacao):
    return [
        ("Amamentação", avaliacao.func_amamentacao),
        ("Mamadeira", avaliacao.func_mamadeira),
        ("Transição para papinhas", avaliacao.func_papinhas),
        ("Transição para sólidos", avaliacao.func_solidos),
        ("Comer com as mãos / se suja", avaliacao.func_maos),
        ("Uso de utensílios", avaliacao.func_utensilios),
        ("Uso do copo", avaliacao.func_copo),
    ]


def _sensorial_grupos(avaliacao):
    return [
        {
            "nome": "VISUAL",
            "itens": [
                ("Forma", avaliacao.sens_visual_forma),
                ("Cor", avaliacao.sens_visual_cor),
                ("Tamanho", avaliacao.sens_visual_tamanho),
                ("Outros", avaliacao.sens_visual_outros),
            ],
        },
        {
            "nome": "OLFATO",
            "itens": [
                ("Alimentos de pouco odor", avaliacao.sens_olfato_pouco),
                ("Alimentos com odores intensos", avaliacao.sens_olfato_intenso),
                ("Os odores não importam", avaliacao.sens_olfato_nao_importa),
                ("Outros", avaliacao.sens_olfato_outros),
            ],
        },
        {
            "nome": "TATO",
            "itens": [
                ("Temperatura: Frio", avaliacao.sens_tato_frio),
                ("Temperatura: Quente", avaliacao.sens_tato_quente),
                ("Temperatura: Morno", avaliacao.sens_tato_morno),
                ("Consistência: Mole", avaliacao.sens_tato_mole),
                ("Consistência: Dura", avaliacao.sens_tato_dura),
                ("Consistência: Semi-dura", avaliacao.sens_tato_semi_dura),
                ("Textura: Liso/Suave", avaliacao.sens_tato_liso),
                ("Textura: Rugoso/Texturizado", avaliacao.sens_tato_rugoso),
                ("Textura: Áspero", avaliacao.sens_tato_aspero),
                ("Textura: Pegajoso", avaliacao.sens_tato_pegajoso),
                ("Umidade: Seco", avaliacao.sens_tato_seco),
                ("Umidade: Úmido/Molhado", avaliacao.sens_tato_umido),
            ],
        },
        {
            "nome": "PROPRIOCEPÇÃO / VESTIBULAR",
            "itens": [
                ("Movimentos complexos", avaliacao.sens_propr_complexos),
                ("Movimentos simples", avaliacao.sens_propr_simples),
                ("Força", avaliacao.sens_propr_forca),
                ("Resistência", avaliacao.sens_propr_resistencia),
            ],
        },
        {
            "nome": "GOSTO",
            "itens": [
                ("Doce", avaliacao.sens_gosto_doce),
                ("Salgado", avaliacao.sens_gosto_salgado),
                ("Amargo", avaliacao.sens_gosto_amargo),
                ("Ácido", avaliacao.sens_gosto_acido),
                ("Umami", avaliacao.sens_gosto_umami),
            ],
        },
        {
            "nome": "AUDITIVO",
            "itens": [
                ("Muito barulho", avaliacao.sens_audit_barulho),
                ("Crocante", avaliacao.sens_audit_crocante),
                ("Silencioso", avaliacao.sens_audit_silencioso),
            ],
        },
    ]
