import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Paciente, AvaliacaoPEDI

_PEDI_FS_MAX = {"autocuidado": 73, "mobilidade": 59, "funcao_social": 65}
_PEDI_CA_MAX = {"autocuidado": 40, "mobilidade": 40, "funcao_social": 40}


@login_required
def nova_avaliacao_pedi(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    av = AvaliacaoPEDI.objects.create(paciente=paciente)
    return redirect("pedi_form", avaliacao_id=av.id)


@login_required
def pedi_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoPEDI, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if request.method == "POST":
        def _get_int(name):
            try:
                return int(request.POST.get(name, "").strip())
            except (ValueError, AttributeError):
                return None

        avaliacao.fs_autocuidado = _get_int("fs_autocuidado")
        avaliacao.fs_mobilidade = _get_int("fs_mobilidade")
        avaliacao.fs_funcao_social = _get_int("fs_funcao_social")
        avaliacao.ca_autocuidado = _get_int("ca_autocuidado")
        avaliacao.ca_mobilidade = _get_int("ca_mobilidade")
        avaliacao.ca_funcao_social = _get_int("ca_funcao_social")

        # Escala 0-100 por aproximação (raw/max * 100)
        def _escala(raw, maximo):
            if raw is None or maximo == 0:
                return None
            return round(min(raw, maximo) / maximo * 100, 1)

        avaliacao.fs_autocuidado_escala = _escala(avaliacao.fs_autocuidado, _PEDI_FS_MAX["autocuidado"])
        avaliacao.fs_mobilidade_escala = _escala(avaliacao.fs_mobilidade, _PEDI_FS_MAX["mobilidade"])
        avaliacao.fs_funcao_social_escala = _escala(avaliacao.fs_funcao_social, _PEDI_FS_MAX["funcao_social"])
        avaliacao.ca_autocuidado_escala = _escala(avaliacao.ca_autocuidado, _PEDI_CA_MAX["autocuidado"])
        avaliacao.ca_mobilidade_escala = _escala(avaliacao.ca_mobilidade, _PEDI_CA_MAX["mobilidade"])
        avaliacao.ca_funcao_social_escala = _escala(avaliacao.ca_funcao_social, _PEDI_CA_MAX["funcao_social"])

        avaliacao.save()
        messages.success(request, "PEDI salvo com sucesso.")
        return redirect("pedi_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/pedi_form.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "fs_max": _PEDI_FS_MAX,
        "ca_max": _PEDI_CA_MAX,
    })


@login_required
def pedi_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoPEDI, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    dominios_fs = [
        {"nome": "Autocuidado",    "raw": avaliacao.fs_autocuidado,    "max": _PEDI_FS_MAX["autocuidado"],   "escala": avaliacao.fs_autocuidado_escala},
        {"nome": "Mobilidade",     "raw": avaliacao.fs_mobilidade,     "max": _PEDI_FS_MAX["mobilidade"],    "escala": avaliacao.fs_mobilidade_escala},
        {"nome": "Função Social",  "raw": avaliacao.fs_funcao_social,  "max": _PEDI_FS_MAX["funcao_social"], "escala": avaliacao.fs_funcao_social_escala},
    ]
    dominios_ca = [
        {"nome": "Autocuidado",    "raw": avaliacao.ca_autocuidado,    "max": _PEDI_CA_MAX["autocuidado"],   "escala": avaliacao.ca_autocuidado_escala},
        {"nome": "Mobilidade",     "raw": avaliacao.ca_mobilidade,     "max": _PEDI_CA_MAX["mobilidade"],    "escala": avaliacao.ca_mobilidade_escala},
        {"nome": "Função Social",  "raw": avaliacao.ca_funcao_social,  "max": _PEDI_CA_MAX["funcao_social"], "escala": avaliacao.ca_funcao_social_escala},
    ]

    return render(request, "questionario/pedi_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "dominios_fs": dominios_fs,
        "dominios_ca": dominios_ca,
        "chart_json": json.dumps({
            "labels": ["Autocuidado", "Mobilidade", "Função Social"],
            "fs": [d["escala"] or 0 for d in dominios_fs],
            "ca": [d["escala"] or 0 for d in dominios_ca],
        }),
    })


@login_required
def pedi_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoPEDI, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação PEDI excluída com sucesso."})
        messages.success(request, "Avaliação PEDI excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_pedi(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoPEDI, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("pedi_resultado", avaliacao_id=avaliacao_id)
