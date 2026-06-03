import json
import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from questionario.models import Paciente
from .models import ProcedimentoDocumento

TIPO_LABELS = dict(ProcedimentoDocumento.TIPO_CHOICES)

TEMPLATE_MAP = {
    "anamnese":          "procedimentos/anamnese.html",
    "anamnese_adulto":   "procedimentos/anamnese_adulto.html",
    "anamnese_infantil": "procedimentos/anamnese_infantil.html",
    "anamnese_tea":      "procedimentos/anamnese_tea.html",
    "anamnese_tdah":     "procedimentos/anamnese_tdah.html",
    "anamnese_casal":    "procedimentos/anamnese_casal.html",
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


def _doc_ctx(request, paciente, doc, tipo=None):
    t = doc.tipo if doc else tipo
    return {
        "paciente":       paciente,
        "doc":            doc,
        "idade_str":      _idade_str(paciente.data_nascimento),
        "data_hoje":      datetime.date.today().strftime("%d/%m/%Y"),
        "conteudo_salvo": json.dumps(doc.conteudo if doc else {}),
        "atualizado_em":  doc.atualizado_em if doc else None,
        "tipo":           t,
        "tipo_label":     TIPO_LABELS.get(t, t),
        "criar_url":      None,
    }


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

@login_required
def novo_procedimento(request, paciente_id, tipo):
    if tipo not in TEMPLATE_MAP:
        from django.http import Http404
        raise Http404
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    # doc=None sinaliza para o template que ainda não foi salvo
    ctx = _doc_ctx(request, paciente, None)
    ctx["tipo"]  = tipo
    ctx["criar_url"] = f"/pacientes/{paciente_id}/procedimentos/{tipo}/criar/"
    return render(request, TEMPLATE_MAP[tipo], ctx)


# ── Criar documento no primeiro Save ─────────────────────────────────────────

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

    doc = ProcedimentoDocumento.objects.create(
        paciente=paciente,
        tipo=tipo,
        conteudo=data,
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

    doc.conteudo = data.get("conteudo", data)
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
