import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Paciente, AvaliacaoSono, RespostaSono
from ..data.data_sono import SONO_DOMINIOS, SONO_OPCOES
from ..services import notificar_terapeuta

# RespostaSono NÃO tem campo dominio — itens são salvos com numero_item global.
# Numeração global: (index_dominio * 100) + numero_local
# Ex.: domínio 0, item 1 → 1; domínio 1, item 1 → 101; domínio 2, item 3 → 203


def _numero_global_sono(idx_dom, numero_local):
    return (idx_dom * 100) + numero_local


def _calcular_sono(avaliacao):
    for idx, dom in enumerate(SONO_DOMINIOS):
        numeros_globais = [_numero_global_sono(idx, n) for n, _ in dom["itens"]]
        respostas = avaliacao.respostas.filter(numero_item__in=numeros_globais)
        total = sum(r.valor for r in respostas)
        setattr(avaliacao, dom["campo"], total)
    return avaliacao


@login_required
def nova_avaliacao_sono(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('sono_infantil'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo Avaliação de Sono Infantil.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    av = AvaliacaoSono.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "id": av.id})
    return redirect("sono_form", avaliacao_id=av.id)


@login_required
def sono_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSono, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("sono_resultado", avaliacao_id=avaliacao_id)

    # respostas_salvas: {numero_global: valor}
    respostas_salvas = {
        r.numero_item: r.valor
        for r in avaliacao.respostas.all()
    }

    if request.method == "POST":
        import json as _json
        valores_validos = {o["valor"] for o in SONO_OPCOES}
        erros, novas = [], {}
        for idx, dom in enumerate(SONO_DOMINIOS):
            for numero, _ in dom["itens"]:
                chave = f"{dom['key']}_{numero}"
                val = request.POST.get(f"item_{chave}")
                if val is None:
                    erros.append(chave)
                else:
                    try:
                        v = int(val)
                        if v in valores_validos:
                            novas[chave] = (v, _numero_global_sono(idx, numero))
                        else:
                            erros.append(chave)
                    except (ValueError, TypeError):
                        erros.append(chave)
        if erros:
            respostas_form = {}
            for idx, dom in enumerate(SONO_DOMINIOS):
                for numero, _ in dom["itens"]:
                    ng = _numero_global_sono(idx, numero)
                    if ng in respostas_salvas:
                        respostas_form[f"{dom['key']}_{numero}"] = respostas_salvas[ng]
            for chave, (v, _ng) in novas.items():
                respostas_form[chave] = v
            return render(request, "questionario/sono_form.html", {
                "avaliacao": avaliacao, "paciente": avaliacao.paciente,
                "dominios": SONO_DOMINIOS, "opcoes": SONO_OPCOES,
                "respostas_salvas": respostas_salvas,
                "numero_global": _numero_global_sono,
                "respostas_json": _json.dumps(respostas_form),
                "erros_json": _json.dumps(erros),
            })
        for chave, (v, num_global) in novas.items():
            RespostaSono.objects.update_or_create(
                avaliacao=avaliacao, numero_item=num_global,
                defaults={"valor": v}
            )
        avaliacao = _calcular_sono(avaliacao)
        avaliacao.status = "concluida"
        avaliacao.save()
        return redirect("sono_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/sono_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominios": SONO_DOMINIOS,
        "opcoes": SONO_OPCOES,
        "respostas_salvas": respostas_salvas,
        "numero_global": _numero_global_sono,
    })


@login_required
def sono_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSono, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status != "concluida":
        return redirect("sono_form", avaliacao_id=avaliacao_id)
    resultado = []
    max_por_item = max(o["valor"] for o in SONO_OPCOES)
    for dom in SONO_DOMINIOS:
        score = getattr(avaliacao, dom["campo"]) or 0
        max_score = len(dom["itens"]) * max_por_item
        resultado.append({
            "key": dom["key"],
            "nome": dom["nome"],
            "cor": dom["cor"],
            "score": score,
            "max": max_score,
            "pct": int(score / max_score * 100) if max_score else 0,
        })
    return render(request, "questionario/sono_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "resultado": resultado,
    })


@login_required
def sono_visualizar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSono, id=avaliacao_id, paciente__medico=request.user)
    respostas_salvas = {(r.dominio, r.numero_item): r.valor for r in avaliacao.respostas.all()}
    return render(request, "questionario/sono_form.html", {
        "avaliacao": avaliacao, "paciente": avaliacao.paciente,
        "dominios": SONO_DOMINIOS, "opcoes": SONO_OPCOES,
        "respostas_salvas": respostas_salvas, "readonly": True,
    })


@login_required
def sono_deletar(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSono, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação de Sono excluída com sucesso."})
        messages.success(request, "Avaliação de Sono excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_sono(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSono, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas.")
    return redirect("sono_resultado", avaliacao_id=avaliacao_id)


def sono_publico(request, token):
    avaliacao = get_object_or_404(AvaliacaoSono, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/concluido.html")

    # respostas_salvas: {numero_global: valor}
    respostas_salvas = {
        r.numero_item: r.valor
        for r in avaliacao.respostas.all()
    }

    if request.method == "POST":
        import json as _json
        valores_validos = {o["valor"] for o in SONO_OPCOES}
        erros, novas = [], {}
        for idx, dom in enumerate(SONO_DOMINIOS):
            for numero, _ in dom["itens"]:
                chave = f"{dom['key']}_{numero}"
                val = request.POST.get(f"item_{chave}")
                if val is None:
                    erros.append(chave)
                else:
                    try:
                        v = int(val)
                        if v in valores_validos:
                            novas[chave] = (v, _numero_global_sono(idx, numero))
                        else:
                            erros.append(chave)
                    except (ValueError, TypeError):
                        erros.append(chave)
        if erros:
            respostas_form = {}
            for idx, dom in enumerate(SONO_DOMINIOS):
                for numero, _ in dom["itens"]:
                    ng = _numero_global_sono(idx, numero)
                    if ng in respostas_salvas:
                        respostas_form[f"{dom['key']}_{numero}"] = respostas_salvas[ng]
            for chave, (v, _ng) in novas.items():
                respostas_form[chave] = v
            return render(request, "questionario/sono_form.html", {
                "avaliacao": avaliacao, "paciente": avaliacao.paciente,
                "dominios": SONO_DOMINIOS, "opcoes": SONO_OPCOES,
                "respostas_salvas": respostas_salvas,
                "numero_global": _numero_global_sono,
                "respostas_json": _json.dumps(respostas_form),
                "erros_json": _json.dumps(erros),
                "publico": True, "token": token,
            })
        for chave, (v, num_global) in novas.items():
            RespostaSono.objects.update_or_create(
                avaliacao=avaliacao, numero_item=num_global,
                defaults={"valor": v}
            )
        avaliacao = _calcular_sono(avaliacao)
        avaliacao.status = "concluida"
        avaliacao.save()
        try:
            notificar_terapeuta(avaliacao.paciente, "sono", request)
        except Exception:
            pass
        return render(request, "questionario/concluido.html")

    return render(request, "questionario/sono_form.html", {
        "avaliacao": avaliacao,
        "paciente": avaliacao.paciente,
        "dominios": SONO_DOMINIOS,
        "opcoes": SONO_OPCOES,
        "respostas_salvas": respostas_salvas,
        "numero_global": _numero_global_sono,
        "publico": True,
        "token": token,
    })
