import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..models import Paciente, AvaliacaoAnamneseTEAInf

CAMPOS = [
    "queixa_principal", "historico_gestacional", "marcos_desenvolvimento",
    "linguagem", "interacao_social", "comportamentos_repetitivos",
    "historico_medico", "medicamentos", "historico_familiar",
    "alimentacao", "sono", "escola", "terapias_anteriores", "observacoes",
]
LABELS = {
    "queixa_principal":           "Queixa Principal",
    "historico_gestacional":      "Histórico Gestacional",
    "marcos_desenvolvimento":     "Marcos de Desenvolvimento",
    "linguagem":                  "Linguagem",
    "interacao_social":           "Interação Social",
    "comportamentos_repetitivos": "Comportamentos Repetitivos / Interesses Restritos",
    "historico_medico":           "Histórico Médico",
    "medicamentos":               "Medicamentos em Uso",
    "historico_familiar":         "Histórico Familiar",
    "alimentacao":                "Alimentação",
    "sono":                       "Sono",
    "escola":                     "Escola / Aprendizagem",
    "terapias_anteriores":        "Terapias Anteriores",
    "observacoes":                "Observações Clínicas",
}


@login_required
def nova_avaliacao_anamnese_tea_inf(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('anamnese_tea_inf'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível."}, status=403)
        messages.error(request, "Você não tem acesso a este módulo.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoAnamneseTEAInf.objects.create(paciente=paciente)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "redirect": f"/questionario/anamnese-tea-inf/{av.uuid}/form/"})
    return redirect("anamnese_tea_inf_form", avaliacao_id=av.uuid)


@login_required
def anamnese_tea_inf_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAnamneseTEAInf, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("anamnese_tea_inf_resultado", avaliacao_id=avaliacao_id)
    if request.method == "POST":
        for campo in CAMPOS:
            setattr(avaliacao, campo, request.POST.get(campo, "").strip())
        avaliacao.status = "concluida"
        avaliacao.save()
        return redirect("anamnese_tea_inf_resultado", avaliacao_id=avaliacao_id)
    return render(request, "questionario/avaliacoes/anamnese_tea_inf_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "campos": [(c, LABELS[c]) for c in CAMPOS],
    })


@login_required
def anamnese_tea_inf_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAnamneseTEAInf, uuid=avaliacao_id, paciente__medico=request.user)
    return render(request, "questionario/avaliacoes/anamnese_tea_inf_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "campos": [(c, LABELS[c], getattr(avaliacao, c, "")) for c in CAMPOS],
    })


@login_required
def anamnese_tea_inf_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAnamneseTEAInf, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Anamnese excluída."})
        messages.success(request, "Anamnese excluída.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)
