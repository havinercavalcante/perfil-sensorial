import json
import datetime
import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST

from questionario.models import (
    Paciente,
    AvaliacaoEBAI, AvaliacaoSEPS, AvaliacaoECA, AvaliacaoTOD,
)
from .models import ProcedimentoDocumento

TIPO_LABELS = dict(ProcedimentoDocumento.TIPO_CHOICES)

TEMPLATE_MAP = {
    "anamnese":          "procedimentos/anamnese.html",
    "anamnese_adulto":   "procedimentos/anamnese_adulto.html",
    "anamnese_infantil": "procedimentos/anamnese_infantil.html",
    "anamnese_tea":      "procedimentos/anamnese_tea.html",
    "anamnese_tdah":     "procedimentos/anamnese_tdah.html",
    "anamnese_casal":    "procedimentos/anamnese_casal.html",
    "anamnese_seletividade_alimentar": "procedimentos/anamnese_seletividade_alimentar.html",
    "evolucao_semanal":     "procedimentos/evolucao_semanal.html",
    "ficha_visita_escolar": "procedimentos/ficha_visita_escolar.html",
    "ficha_triagem":        "procedimentos/ficha_triagem.html",
    "carta_encaminhamento": "procedimentos/carta_encaminhamento.html",
    "atestado":             "procedimentos/atestado.html",
    "relatorio":            "procedimentos/relatorio.html",
}


def _idade_str(data_nasc):
    if not data_nasc:
        return "—"
    hoje = datetime.date.today()
    anos = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
    meses = (hoje.month - data_nasc.month - (hoje.day < data_nasc.day)) % 12
    if anos >= 2:
        return f"{anos} anos"
    if anos == 1:
        return f"1 ano e {meses} mês{'es' if meses != 1 else ''}"
    return f"{meses} meses"


def _doc_ctx(request, paciente, doc, tipo=None, is_public=False):
    t = doc.tipo if doc else tipo
    return {
        "paciente":       paciente,
        "doc":            doc,
        "idade_str":      _idade_str(paciente.data_nascimento),
        "data_hoje":      datetime.date.today().strftime("%d/%m/%Y"),
        "data_registro":  (doc.data if doc else datetime.date.today()).isoformat(),
        "conteudo_salvo": json.dumps(doc.conteudo if doc else {}),
        "atualizado_em":  doc.atualizado_em if doc else None,
        "tipo":           t,
        "tipo_label":     TIPO_LABELS.get(t, t),
        "criar_url":      None,
        "is_public":      is_public,
    }


# ── Nova anamnese preenchida diretamente pelo profissional ───────────────────
# (sem precisar cadastrar o paciente antes — mesma lógica de find-or-create
# usada no link público enviado ao responsável, só que iniciada pelo profissional).

@login_required
def nova_anamnese(request):
    tipos = [(t, TIPO_LABELS[t]) for t in ProcedimentoDocumento.TIPOS_ANAMNESE]

    if request.method == "POST":
        tipo = request.POST.get("tipo", "")
        nome = request.POST.get("nome", "").strip()
        data_nascimento = request.POST.get("data_nascimento", "")
        is_adulto = tipo == "anamnese_adulto"
        responsavel = request.POST.get("responsavel", "").strip() if not is_adulto else nome
        email = request.POST.get("email_responsavel", "").strip()
        telefone = request.POST.get("telefone", "").strip()

        erro = None
        if tipo not in ProcedimentoDocumento.TIPOS_ANAMNESE:
            erro = "Selecione o tipo de anamnese."
        elif not nome or not data_nascimento or (not is_adulto and not responsavel):
            erro = "Preencha os campos obrigatórios."

        if erro:
            return render(request, "procedimentos/nova_anamnese.html", {
                "tipos": tipos, "post": request.POST, "erro": erro,
            })

        paciente = Paciente.objects.find_or_create_anamnese(
            medico=request.user, nome=nome, data_nascimento=data_nascimento,
            responsavel=responsavel, email_responsavel=email, telefone=telefone,
        )
        doc = ProcedimentoDocumento.objects.create(paciente=paciente, tipo=tipo)
        return redirect("abrir_procedimento", paciente_id=paciente.uuid, tipo=tipo, doc_id=doc.uuid)

    return render(request, "procedimentos/nova_anamnese.html", {"tipos": tipos})


# ── Lista de documentos por tipo ─────────────────────────────────────────────

@login_required
def lista_procedimentos(request, paciente_id, tipo):
    if tipo not in TEMPLATE_MAP:
        from django.http import Http404
        raise Http404
    paciente  = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    documentos = ProcedimentoDocumento.objects.filter(paciente=paciente, tipo=tipo)
    return render(request, "procedimentos/lista.html", {
        "paciente":   paciente,
        "documentos": documentos,
        "tipo":       tipo,
        "tipo_label": TIPO_LABELS.get(tipo, tipo),
    })


# ── Novo documento — só renderiza, não salva ainda ───────────────────────────

def _escalas_ctx_seletividade(paciente):
    ebai = paciente.avaliacoes_ebai.filter(status="concluida").first()
    seps = paciente.avaliacoes_seps.filter(status="concluida").first()
    eca  = paciente.avaliacoes_eca.filter(status="concluida").first()
    tod  = paciente.avaliacoes_tod.filter(status="concluida").first()

    def class_ebai(t):
        if t is None: return "não disponível"
        if t >= 71: return "Dificuldades severas"
        if t >= 66: return "Dificuldades moderadas"
        if t >= 61: return "Dificuldades leves"
        return "Sem dificuldades significativas"

    def top_seps(av):
        if not av: return "não disponível"
        subs = {
            "Aversão ao toque": av.pont_aversao_toque or 0,
            "Foco numa única comida": av.pont_foco_unica or 0,
            "Vômito": av.pont_vomito or 0,
            "Sensibilidade à temperatura": av.pont_sensib_temp or 0,
            "Expulsão": av.pont_expulsao or 0,
            "Encher demasiado": av.pont_encher or 0,
        }
        top = sorted(subs, key=subs.get, reverse=True)[:2]
        return ", ".join(top)

    def top_eca(av):
        if not av: return "não disponível"
        subs = {
            "Motricidade na Mastigação": av.pont_mastigacao or 0,
            "Seletividade Alimentar": av.pont_seletividade or 0,
            "Aspectos Comportamentais": av.pont_comportamental or 0,
            "Sintomas Gastrointestinais": av.pont_gi or 0,
            "Sensibilidade Sensorial": av.pont_sensorial or 0,
            "Habilidades nas Refeições": av.pont_habilidades or 0,
        }
        top = sorted(subs, key=subs.get, reverse=True)[:2]
        return ", ".join(top)

    return {
        "ebai_resumo": (
            f"Escore T = {ebai.escore_t} ({class_ebai(ebai.escore_t)}), "
            f"Pontuação Bruta = {ebai.pont_bruto}/98"
        ) if ebai else "Aguardando resposta do responsável.",
        "seps_resumo": (
            f"Subescalas com maior pontuação: {top_seps(seps)}"
        ) if seps else "Aguardando resposta do responsável.",
        "eca_resumo": (
            f"Subescalas com maior pontuação: {top_eca(eca)}"
        ) if eca else "Aguardando resposta do responsável.",
        "tod_resumo": (
            f"{tod.itens_corte_positivos or 0} itens ★ com valor ≥ 2 — "
            f"{'Positivo para TOD' if (tod.itens_corte_positivos or 0) >= 4 else 'Negativo para TOD'}"
        ) if tod else "Aguardando resposta do responsável.",
    }


@login_required
def novo_procedimento(request, paciente_id, tipo):
    if tipo not in TEMPLATE_MAP:
        from django.http import Http404
        raise Http404
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    ctx = _doc_ctx(request, paciente, None)
    ctx["tipo"]      = tipo
    ctx["criar_url"] = f"/pacientes/{paciente_id}/procedimentos/{tipo}/criar/"
    if tipo == "anamnese_seletividade_alimentar":
        ctx.update(_escalas_ctx_seletividade(paciente))
    return render(request, TEMPLATE_MAP[tipo], ctx)


# ── Criar documento no primeiro Save ─────────────────────────────────────────

def _extrair_data_registro(conteudo):
    """Retira a chave '_data' (se houver) do conteúdo e devolve (conteudo, data ou None)."""
    valor = conteudo.pop("_data", None)
    if not valor:
        return conteudo, None
    try:
        return conteudo, datetime.date.fromisoformat(valor)
    except ValueError:
        return conteudo, None


@login_required
@require_POST
def criar_procedimento(request, paciente_id, tipo):
    if tipo not in TEMPLATE_MAP:
        return JsonResponse({"ok": False}, status=404)
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"ok": False, "error": "Dados inválidos."}, status=400)

    data, data_registro = _extrair_data_registro(data)
    doc = ProcedimentoDocumento.objects.create(
        paciente=paciente,
        tipo=tipo,
        conteudo=data,
        **({"data": data_registro} if data_registro else {}),
    )
    from django.urls import reverse
    return JsonResponse({
        "ok": True,
        "atualizado_em": doc.atualizado_em.strftime("%d/%m/%Y às %H:%M"),
        "titulo": doc.titulo_display,
        "save_url": reverse("salvar_procedimento",
                            kwargs={"paciente_id": paciente_id, "tipo": tipo, "doc_id": doc.uuid}),
        "edit_url": reverse("abrir_procedimento",
                            kwargs={"paciente_id": paciente_id, "tipo": tipo, "doc_id": doc.uuid}),
    })


# ── Abrir documento existente ─────────────────────────────────────────────────

@login_required
def abrir_procedimento(request, paciente_id, tipo, doc_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    doc      = get_object_or_404(ProcedimentoDocumento, uuid=doc_id, paciente=paciente, tipo=tipo)
    template = TEMPLATE_MAP[tipo]
    return render(request, template, _doc_ctx(request, paciente, doc))


# ── Salvar documento ──────────────────────────────────────────────────────────

@login_required
@require_POST
def salvar_procedimento(request, paciente_id, tipo, doc_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    doc      = get_object_or_404(ProcedimentoDocumento, uuid=doc_id, paciente=paciente, tipo=tipo)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"ok": False, "error": "Dados inválidos."}, status=400)

    conteudo = data.get("conteudo", data)
    conteudo, data_registro = _extrair_data_registro(conteudo)
    doc.conteudo = conteudo
    if data_registro:
        doc.data = data_registro
    titulo = data.get("titulo", "").strip()
    if titulo:
        doc.titulo = titulo
    doc.save()
    return JsonResponse({
        "ok": True,
        "atualizado_em": doc.atualizado_em.strftime("%d/%m/%Y às %H:%M"),
        "titulo":        doc.titulo_display,
    })


# ── Excluir documento ────────────────────────────────────────────────────────

@login_required
@require_POST
def excluir_procedimento(request, paciente_id, tipo, doc_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    doc      = get_object_or_404(ProcedimentoDocumento, uuid=doc_id, paciente=paciente, tipo=tipo)
    doc.delete()
    return JsonResponse({"ok": True, "message": "Documento excluído com sucesso."})


# ── Anamnese pública (sem login) — preenchida pelo responsável via link ───────

def anamnese_publica_form(request, token):
    doc = get_object_or_404(ProcedimentoDocumento, token_publico=token, tipo__in=ProcedimentoDocumento.TIPOS_ANAMNESE)
    if doc.tipo not in TEMPLATE_MAP:
        raise Http404
    ctx = _doc_ctx(request, doc.paciente, doc, is_public=True)
    return render(request, TEMPLATE_MAP[doc.tipo], ctx)


@require_POST
def anamnese_publica_salvar(request, token):
    doc = get_object_or_404(ProcedimentoDocumento, token_publico=token, tipo__in=ProcedimentoDocumento.TIPOS_ANAMNESE)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"ok": False, "error": "Dados inválidos."}, status=400)

    finalizar = bool(data.pop("finalizar", False))
    conteudo, data_registro = _extrair_data_registro(data)
    doc.conteudo = conteudo
    if data_registro:
        doc.data = data_registro
    doc.save()

    if finalizar:
        doc.token_publico = None
        doc.save(update_fields=["token_publico"])
        return JsonResponse({"ok": True, "finalizado": True})

    return JsonResponse({
        "ok": True,
        "atualizado_em": doc.atualizado_em.strftime("%d/%m/%Y às %H:%M"),
    })


# ── Atalhos legados (redireciona para lista) ──────────────────────────────────

@login_required
def anamnese(request, paciente_id):
    return redirect("lista_procedimentos", paciente_id=paciente_id, tipo="anamnese")

@login_required
def ficha_triagem(request, paciente_id):
    return redirect("lista_procedimentos", paciente_id=paciente_id, tipo="ficha_triagem")

@login_required
def carta_encaminhamento(request, paciente_id):
    return redirect("lista_procedimentos", paciente_id=paciente_id, tipo="carta_encaminhamento")

@login_required
def atestado(request, paciente_id):
    return redirect("lista_procedimentos", paciente_id=paciente_id, tipo="atestado")

@login_required
def relatorio(request, paciente_id):
    return redirect("lista_procedimentos", paciente_id=paciente_id, tipo="relatorio")
