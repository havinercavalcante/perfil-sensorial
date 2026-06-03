import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..models import Paciente, AvaliacaoInventarioDislexia

CAMPOS = [
    "historico_escolar",
    "desempenho_leitura",
    "desempenho_escrita",
    "processamento_fonologico",
    "memoria_trabalho",
    "velocidade_processamento",
    "historico_familiar",
    "avaliacoes_anteriores",
    "observacoes",
]

LABELS = {
    "historico_escolar":         "Histórico Escolar",
    "desempenho_leitura":        "Desempenho em Leitura",
    "desempenho_escrita":        "Desempenho em Escrita",
    "processamento_fonologico":  "Processamento Fonológico",
    "memoria_trabalho":          "Memória de Trabalho",
    "velocidade_processamento":  "Velocidade de Processamento",
    "historico_familiar":        "Histórico Familiar (Dislexia/Dificuldades Escolares)",
    "avaliacoes_anteriores":     "Avaliações Anteriores",
    "observacoes":               "Observações Clínicas",
}


@login_required
def nova_avaliacao_inventario_dislexia(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('inventario_dislexia'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível."}, status=403)
        messages.error(request, "Você não tem acesso a este módulo.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoInventarioDislexia.objects.create(paciente=paciente)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        from django.urls import reverse
        return JsonResponse({"ok": True, "redirect": reverse("inventario_dislexia_form", args=[av.uuid])})
    return redirect("inventario_dislexia_form", avaliacao_id=av.uuid)


@login_required
def inventario_dislexia_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoInventarioDislexia, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("inventario_dislexia_resultado", avaliacao_id=avaliacao_id)
    if request.method == "POST":
        for campo in CAMPOS:
            setattr(avaliacao, campo, request.POST.get(campo, "").strip())
        avaliacao.status = "concluida"
        avaliacao.save()
        return redirect("inventario_dislexia_resultado", avaliacao_id=avaliacao_id)
    return render(request, "questionario/avaliacoes/inventario_dislexia_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "campos": [(c, LABELS[c]) for c in CAMPOS],
    })


@login_required
def inventario_dislexia_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoInventarioDislexia, uuid=avaliacao_id, paciente__medico=request.user)
    return render(request, "questionario/avaliacoes/inventario_dislexia_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "campos": [(c, LABELS[c], getattr(avaliacao, c, "")) for c in CAMPOS],
    })


@login_required
def inventario_dislexia_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoInventarioDislexia, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Inventário excluído."})
        messages.success(request, "Inventário excluído.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)
