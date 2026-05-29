import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..models import Paciente, AvaliacaoAnamneseTDAHAdulto

CAMPOS = [
    "queixa_principal", "sintomas_desatencao", "sintomas_hiperativos",
    "historico_infancia", "desempenho_escolar", "desempenho_profissional",
    "relacionamentos", "comorbidades", "medicamentos",
    "sono", "impacto_funcional", "observacoes",
]
LABELS = {
    "queixa_principal":        "Queixa Principal",
    "sintomas_desatencao":     "Sintomas de Desatenção",
    "sintomas_hiperativos":    "Sintomas Hiperativos/Impulsivos",
    "historico_infancia":      "Histórico na Infância",
    "desempenho_escolar":      "Desempenho Escolar",
    "desempenho_profissional": "Desempenho Profissional",
    "relacionamentos":         "Relacionamentos",
    "comorbidades":            "Comorbidades",
    "medicamentos":            "Medicamentos em Uso",
    "sono":                    "Sono",
    "impacto_funcional":       "Impacto Funcional",
    "observacoes":             "Observações Clínicas",
}


@login_required
def nova_avaliacao_anamnese_tdah_adulto(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('anamnese_tdah_adulto'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível."}, status=403)
        messages.error(request, "Você não tem acesso a este módulo.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoAnamneseTDAHAdulto.objects.create(paciente=paciente)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "redirect": f"/questionario/anamnese-tdah-adulto/{av.uuid}/form/"})
    return redirect("anamnese_tdah_adulto_form", avaliacao_id=av.uuid)


@login_required
def anamnese_tdah_adulto_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAnamneseTDAHAdulto, uuid=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("anamnese_tdah_adulto_resultado", avaliacao_id=avaliacao_id)
    if request.method == "POST":
        for campo in CAMPOS:
            setattr(avaliacao, campo, request.POST.get(campo, "").strip())
        avaliacao.status = "concluida"
        avaliacao.save()
        return redirect("anamnese_tdah_adulto_resultado", avaliacao_id=avaliacao_id)
    return render(request, "questionario/avaliacoes/anamnese_tdah_adulto_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "campos": [(c, LABELS[c]) for c in CAMPOS],
    })


@login_required
def anamnese_tdah_adulto_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAnamneseTDAHAdulto, uuid=avaliacao_id, paciente__medico=request.user)
    return render(request, "questionario/avaliacoes/anamnese_tdah_adulto_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "campos": [(c, LABELS[c], getattr(avaliacao, c, "")) for c in CAMPOS],
    })


@login_required
def anamnese_tdah_adulto_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAnamneseTDAHAdulto, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Anamnese excluída."})
        messages.success(request, "Anamnese excluída.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)
