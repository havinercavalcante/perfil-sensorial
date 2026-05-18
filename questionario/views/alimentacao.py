import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Paciente, AvaliacaoAlimentacao, RespostaAlimentacao
from ..data.data_alimentacao import ALIMENTACAO_DOMINIOS, ALIMENTACAO_OPCOES
from ..services import notificar_terapeuta


def _calcular_alimentacao(avaliacao):
    for dom in ALIMENTACAO_DOMINIOS:
        itens = [n for n, _, _reverso in dom["itens"]]
        respostas = avaliacao.respostas.filter(dominio=dom["key"], numero_item__in=itens)
        total = sum(r.valor for r in respostas)
        setattr(avaliacao, dom["campo"], total)
    return avaliacao


@login_required
def nova_avaliacao_alimentacao(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('alimentacao_seletiva'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo Triagem de Alimentação Seletiva.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoAlimentacao.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "id": av.id})
    return redirect("alimentacao_form", avaliacao_id=av.id)


@login_required
def alimentacao_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAlimentacao, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("alimentacao_resultado", avaliacao_id=avaliacao_id)

    respostas_salvas = {
        (r.dominio, r.numero_item): r.valor
        for r in avaliacao.respostas.all()
    }

    if request.method == "POST":
        import json as _json
        erros, novas = [], {}
        for dom in ALIMENTACAO_DOMINIOS:
            for numero, _, _reverso in dom["itens"]:
                chave = f"{dom['key']}_{numero}"
                val = request.POST.get(f"item_{chave}")
                if val is None:
                    erros.append(chave)
                else:
                    try:
                        v = int(val)
                        if v in {o["valor"] for o in ALIMENTACAO_OPCOES}:
                            novas[chave] = v
                        else:
                            erros.append(chave)
                    except (ValueError, TypeError):
                        erros.append(chave)
        if erros:
            respostas_form = {f"{d}_{n}": v for (d, n), v in respostas_salvas.items()}
            respostas_form.update(novas)
            return render(request, "questionario/alimentacao_form.html", {
                "avaliacao": avaliacao, "paciente": avaliacao.paciente,
                "dominios": ALIMENTACAO_DOMINIOS, "opcoes": ALIMENTACAO_OPCOES,
                "respostas_salvas": respostas_salvas,
                "respostas_json": _json.dumps(respostas_form),
                "erros_json": _json.dumps(erros),
            })
        for chave, v in novas.items():
            dom_key, _, num_str = chave.rpartition("_")
            RespostaAlimentacao.objects.update_or_create(
                avaliacao=avaliacao, dominio=dom_key, numero_item=int(num_str),
                defaults={"valor": v}
            )
        avaliacao = _calcular_alimentacao(avaliacao)
        avaliacao.status = "concluida"
        avaliacao.save()
        return redirect("alimentacao_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/alimentacao_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominios": ALIMENTACAO_DOMINIOS,
        "opcoes": ALIMENTACAO_OPCOES,
        "respostas_salvas": respostas_salvas,
    })


@login_required
def alimentacao_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAlimentacao, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("alimentacao_form", avaliacao_id=avaliacao_id)
    resultado = []
    for dom in ALIMENTACAO_DOMINIOS:
        score = getattr(avaliacao, dom["campo"]) or 0
        max_score = len(dom["itens"]) * 2
        resultado.append({
            "key": dom["key"],
            "nome": dom["nome"],
            "cor": dom["cor"],
            "score": score,
            "max": max_score,
            "pct": int(score / max_score * 100) if max_score else 0,
        })
    return render(request, "questionario/alimentacao_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "resultado": resultado,
    })


@login_required
def alimentacao_visualizar(request, avaliacao_id):
    import json
    avaliacao = get_object_or_404(AvaliacaoAlimentacao, id=avaliacao_id, paciente__medico=request.user)
    respostas_salvas = {(r.dominio, r.numero_item): r.valor for r in avaliacao.respostas.all()}
    respostas_json = json.dumps({f"{d}_{n}": v for (d, n), v in respostas_salvas.items()})
    return render(request, "questionario/alimentacao_form.html", {
        "avaliacao": avaliacao, "paciente": avaliacao.paciente,
        "dominios": ALIMENTACAO_DOMINIOS, "opcoes": ALIMENTACAO_OPCOES,
        "respostas_salvas": respostas_salvas, "respostas_json": respostas_json, "readonly": True,
    })


@login_required
def alimentacao_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAlimentacao, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação de Alimentação excluída com sucesso."})
        messages.success(request, "Avaliação de Alimentação excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_alimentacao(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAlimentacao, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("alimentacao_resultado", avaliacao_id=avaliacao_id)


def alimentacao_publico(request, token):
    avaliacao = get_object_or_404(AvaliacaoAlimentacao, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/concluido.html")

    respostas_salvas = {
        (r.dominio, r.numero_item): r.valor
        for r in avaliacao.respostas.all()
    }

    if request.method == "POST":
        import json as _json
        erros, novas = [], {}
        for dom in ALIMENTACAO_DOMINIOS:
            for numero, _, _reverso in dom["itens"]:
                chave = f"{dom['key']}_{numero}"
                val = request.POST.get(f"item_{chave}")
                if val is None:
                    erros.append(chave)
                else:
                    try:
                        v = int(val)
                        if v in {o["valor"] for o in ALIMENTACAO_OPCOES}:
                            novas[chave] = v
                        else:
                            erros.append(chave)
                    except (ValueError, TypeError):
                        erros.append(chave)
        if erros:
            respostas_form = {f"{d}_{n}": v for (d, n), v in respostas_salvas.items()}
            respostas_form.update(novas)
            return render(request, "questionario/alimentacao_form.html", {
                "avaliacao": avaliacao, "paciente": avaliacao.paciente,
                "dominios": ALIMENTACAO_DOMINIOS, "opcoes": ALIMENTACAO_OPCOES,
                "respostas_salvas": respostas_salvas,
                "respostas_json": _json.dumps(respostas_form),
                "erros_json": _json.dumps(erros),
                "publico": True, "token": token,
            })
        for chave, v in novas.items():
            dom_key, _, num_str = chave.rpartition("_")
            RespostaAlimentacao.objects.update_or_create(
                avaliacao=avaliacao, dominio=dom_key, numero_item=int(num_str),
                defaults={"valor": v}
            )
        avaliacao = _calcular_alimentacao(avaliacao)
        avaliacao.status = "concluida"
        avaliacao.save()
        try:
            notificar_terapeuta(avaliacao.paciente, "alimentacao", request)
        except Exception:
            pass
        return render(request, "questionario/concluido.html")

    return render(request, "questionario/alimentacao_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominios": ALIMENTACAO_DOMINIOS,
        "opcoes": ALIMENTACAO_OPCOES,
        "respostas_salvas": respostas_salvas,
        "publico": True,
        "token": token,
    })
