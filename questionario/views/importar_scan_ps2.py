"""
Import por OCR de formulários PS2 (Criança 3-14, Criança Pequena, Bebê)
e Perfil Sensorial do Adulto.
"""
import io
import uuid as uuid_mod

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..models import (
    Avaliacao, Resposta,
    AvaliacaoPS2Bebe, RespostaPS2Bebe,
    AvaliacaoAdultoSensorial, RespostaAdultoSensorial,
    Paciente,
)
from ..data.data import (
    SECOES, PERGUNTAS, OPCOES, calcular_pontuacao,
)
from ..data.data_ps2_bebe_wd import (
    SECOES_PS2_BEBE, PERGUNTAS_PS2_BEBE, OPCOES_PS2,
    TOTAL_ITENS_PS2_BEBE, calcular_pontuacao_ps2_bebe,
)
from ..data.data_ps2_cp_wd import (
    SECOES_PS2_CP, PERGUNTAS_PS2_CP, ITENS_EXTRAS_PS2_CP,
    TOTAL_ITENS_PS2_CP, calcular_pontuacao_ps2_cp,
)
from ..data.data_adulto_sensorial import (
    SECOES_ADULTO, PERGUNTAS_ADULTO, OPCOES_ADULTO,
    TOTAL_ITENS_ADULTO, calcular_pontuacao_adulto,
)
from ..ocr.ps2_reader import processar_paginas_ps2

EXTENSOES_ACEITAS = {'.jpg', '.jpeg', '.png', '.webp', '.pdf'}


def _classificar_ps2(pct):
    if pct <= 20:   return 'Muito menos que outros'
    if pct <= 40:   return 'Menos que outros'
    if pct <= 70:   return 'Típico'
    if pct <= 85:   return 'Mais que outros'
    return 'Muito mais que outros'


def _classe_css(pct):
    if pct <= 20:   return 'muito-menos'
    if pct <= 40:   return 'menos'
    if pct <= 70:   return 'tipico'
    if pct <= 85:   return 'mais'
    return 'muito-mais'


def _arquivos_para_bytes(arquivos):
    paginas = []
    for arq in arquivos:
        nome = arq.name.lower()
        dados = arq.read()
        if nome.endswith('.pdf'):
            import pypdfium2 as pdfium
            doc = pdfium.PdfDocument(dados)
            for i in range(len(doc)):
                bitmap = doc[i].render(scale=2.5)
                buf = io.BytesIO()
                bitmap.to_pil().save(buf, format='JPEG', quality=90)
                paginas.append(buf.getvalue())
        else:
            from PIL import Image
            img = Image.open(io.BytesIO(dados)).convert('RGB')
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=90)
            paginas.append(buf.getvalue())
    return paginas


def _validar_upload(request, template, contexto):
    arquivos = request.FILES.getlist('imagens')
    if not arquivos:
        messages.error(request, 'Envie ao menos uma imagem ou PDF do formulário.')
        return None, render(request, template, contexto)
    if len(arquivos) > 10:
        messages.error(request, 'Máximo de 10 arquivos por vez.')
        return None, render(request, template, contexto)
    invalidos = [a.name for a in arquivos
                 if not any(a.name.lower().endswith(e) for e in EXTENSOES_ACEITAS)]
    if invalidos:
        messages.error(request, f'Formato não suportado: {", ".join(invalidos)}.')
        return None, render(request, template, contexto)
    return arquivos, None


# ──────────────────────────────────────────────────────────────
# PS2 Criança (3–14 anos) → Avaliacao / Resposta
# ──────────────────────────────────────────────────────────────

@login_required
def importar_scan_ps2_crianca_upload(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or not (perfil.tem_acesso('sensorial') or perfil.tem_acesso('adulto_sensorial')):
        messages.error(request, 'Você não tem acesso ao módulo Sensorial.')
        return redirect('detalhe_paciente', paciente_id=paciente_id)

    template = 'questionario/avaliacoes/importar_scan_ps2_upload.html'
    ctx = {'paciente': paciente, 'tipo': 'ps2_crianca',
           'titulo': 'PS2 Criança (3–14 anos)'}

    if request.method == 'GET':
        return render(request, template, ctx)

    arquivos, resp_erro = _validar_upload(request, template, ctx)
    if resp_erro:
        return resp_erro

    try:
        paginas = _arquivos_para_bytes(arquivos)
        # PS2: colunas esq→dir = 5,4,3,2,1
        items_extraidos = processar_paginas_ps2(paginas, total_items=86,
                                                col_values=[5, 4, 3, 2, 1])
    except Exception as exc:
        messages.error(request, f'Erro ao processar imagem: {exc}')
        return render(request, template, ctx)

    av = Avaliacao.objects.create(
        paciente=paciente,
        token=str(uuid_mod.uuid4()),
        status='em_andamento',
    )

    confianca = {}
    for num, info in items_extraidos.items():
        val = info.get('value')
        conf = info.get('confidence', 'missing')
        confianca[str(num)] = conf
        if val and 1 <= val <= 5:
            Resposta.objects.create(avaliacao=av, numero_item=num, valor=val)

    request.session[f'scan_conf_{av.uuid}'] = confianca
    return redirect('importar_scan_ps2_crianca_revisao', avaliacao_id=av.uuid)


@login_required
def importar_scan_ps2_crianca_revisao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, uuid=avaliacao_id, paciente__medico=request.user)

    if avaliacao.status == 'concluida':
        return redirect('dashboard', avaliacao_id=avaliacao_id)

    respostas_atuais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    confianca_raw = request.session.get(f'scan_conf_{avaliacao.uuid}', {})
    confianca = {int(k): v for k, v in confianca_raw.items()}

    if request.method == 'POST':
        novas = {}
        erros = []
        for secao in SECOES:
            for item in secao['itens']:
                val = request.POST.get(f'item_{item}')
                if not val:
                    erros.append(item)
                else:
                    try:
                        v = int(val)
                        if 0 <= v <= 5:
                            novas[item] = v
                        else:
                            erros.append(item)
                    except (ValueError, TypeError):
                        erros.append(item)

        if erros:
            messages.error(request, f'Preencha os {len(erros)} item(ns) em destaque antes de confirmar.')
        else:
            for item, valor in novas.items():
                Resposta.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={'valor': valor}
                )
            respostas_finais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
            p = calcular_pontuacao(respostas_finais)
            avaliacao.pont_auditiva     = p.get("auditiva", 0)
            avaliacao.pont_visual       = p.get("visual", 0)
            avaliacao.pont_tato         = p.get("tato", 0)
            avaliacao.pont_movimento    = p.get("movimento", 0)
            avaliacao.pont_posicao      = p.get("posicao", 0)
            avaliacao.pont_oral         = p.get("oral", 0)
            avaliacao.pont_conduta      = p.get("conduta", 0)
            avaliacao.pont_socioemocional = p.get("socioemocional", 0)
            avaliacao.pont_atencao      = p.get("atencao", 0)
            avaliacao.pont_ex = p.get("EX", 0)
            avaliacao.pont_ev = p.get("EV", 0)
            avaliacao.pont_sn = p.get("SN", 0)
            avaliacao.pont_ob = p.get("OB", 0)
            avaliacao.status = 'concluida'
            avaliacao.save()
            request.session.pop(f'scan_conf_{avaliacao.uuid}', None)
            return redirect('dashboard', avaliacao_id=avaliacao_id)

    secoes_revisao, n_baixa, n_ausente = _montar_secoes_revisao(
        SECOES, PERGUNTAS, respostas_atuais, confianca
    )

    return render(request, 'questionario/avaliacoes/importar_scan_ps2_revisao.html', {
        'avaliacao': avaliacao,
        'paciente': avaliacao.paciente,
        'secoes': secoes_revisao,
        'opcoes': OPCOES,
        'n_baixa': n_baixa,
        'n_ausente': n_ausente,
        'titulo': 'PS2 Criança (3–14 anos)',
    })


# ──────────────────────────────────────────────────────────────
# PS2 Bebê / Criança Pequena (Winnie Dunn) → AvaliacaoPS2Bebe
# ──────────────────────────────────────────────────────────────

@login_required
def importar_scan_ps2_bebe_upload(request, paciente_id, faixa):
    if faixa not in ('bebe', 'cp'):
        return redirect('detalhe_paciente', paciente_id=paciente_id)

    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    perfil = getattr(request.user, 'perfil', None)
    modulo = 'ps2_bebe_wd' if faixa == 'bebe' else 'ps2_cp_wd'
    if not perfil or not (perfil.tem_acesso(modulo) or perfil.tem_acesso('bebe')):
        messages.error(request, 'Você não tem acesso a este módulo.')
        return redirect('detalhe_paciente', paciente_id=paciente_id)

    titulo = 'PS2 Bebê (0–6 meses)' if faixa == 'bebe' else 'PS2 Criança Pequena (7–35 meses)'
    template = 'questionario/avaliacoes/importar_scan_ps2_upload.html'
    ctx = {'paciente': paciente, 'tipo': f'ps2_{faixa}', 'titulo': titulo, 'faixa': faixa}

    if request.method == 'GET':
        return render(request, template, ctx)

    arquivos, resp_erro = _validar_upload(request, template, ctx)
    if resp_erro:
        return resp_erro

    total = TOTAL_ITENS_PS2_BEBE if faixa == 'bebe' else TOTAL_ITENS_PS2_CP
    try:
        paginas = _arquivos_para_bytes(arquivos)
        items_extraidos = processar_paginas_ps2(paginas, total_items=total,
                                                col_values=[5, 4, 3, 2, 1])
    except Exception as exc:
        messages.error(request, f'Erro ao processar imagem: {exc}')
        return render(request, template, ctx)

    av = AvaliacaoPS2Bebe.objects.create(
        paciente=paciente,
        faixa=faixa,
        status='em_andamento',
    )

    extras = ITENS_EXTRAS_PS2_CP if faixa == 'cp' else []
    confianca = {}
    for num, info in items_extraidos.items():
        val = info.get('value')
        conf = info.get('confidence', 'missing')
        confianca[str(num)] = conf
        if val and 1 <= val <= 5:
            RespostaPS2Bebe.objects.create(avaliacao=av, numero_item=num, valor=val)

    request.session[f'scan_conf_{av.uuid}'] = confianca
    return redirect('importar_scan_ps2_bebe_revisao', avaliacao_id=av.uuid)


@login_required
def importar_scan_ps2_bebe_revisao(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoPS2Bebe, uuid=avaliacao_id,
                                  paciente__medico=request.user)

    if avaliacao.status == 'concluida':
        return redirect('detalhe_paciente', paciente_id=avaliacao.paciente.uuid)

    faixa = avaliacao.faixa
    secoes_data   = SECOES_PS2_BEBE if faixa == 'bebe' else SECOES_PS2_CP
    perguntas_data = PERGUNTAS_PS2_BEBE if faixa == 'bebe' else PERGUNTAS_PS2_CP
    extras        = [] if faixa == 'bebe' else ITENS_EXTRAS_PS2_CP
    total_itens   = TOTAL_ITENS_PS2_BEBE if faixa == 'bebe' else TOTAL_ITENS_PS2_CP

    respostas_atuais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    confianca_raw = request.session.get(f'scan_conf_{avaliacao.uuid}', {})
    confianca = {int(k): v for k, v in confianca_raw.items()}

    if request.method == 'POST':
        novas = {}
        erros = []
        for secao in secoes_data:
            for item in secao['itens']:
                if item in extras:
                    continue
                val = request.POST.get(f'item_{item}')
                if not val:
                    erros.append(item)
                else:
                    try:
                        v = int(val)
                        if 1 <= v <= 5:
                            novas[item] = v
                        else:
                            erros.append(item)
                    except (ValueError, TypeError):
                        erros.append(item)

        if erros:
            messages.error(request, f'Preencha os {len(erros)} item(ns) em destaque antes de confirmar.')
        else:
            for item, valor in novas.items():
                RespostaPS2Bebe.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={'valor': valor}
                )
            respostas_finais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
            if faixa == 'bebe':
                p = calcular_pontuacao_ps2_bebe(respostas_finais)
            else:
                p = calcular_pontuacao_ps2_cp(respostas_finais)
            avaliacao.pont_geral          = p.get("geral", 0)
            avaliacao.pont_auditivo       = p.get("auditivo", 0)
            avaliacao.pont_visual         = p.get("visual", 0)
            avaliacao.pont_tato           = p.get("tato", 0)
            avaliacao.pont_movimentos     = p.get("movimentos", 0)
            avaliacao.pont_oral           = p.get("oral", 0)
            avaliacao.pont_comportamental = p.get("comportamental", 0)
            avaliacao.pont_ex = p.get("EX", 0)
            avaliacao.pont_ev = p.get("EV", 0)
            avaliacao.pont_sn = p.get("SN", 0)
            avaliacao.pont_ob = p.get("OB", 0)
            avaliacao.status = 'concluida'
            avaliacao.save()
            request.session.pop(f'scan_conf_{avaliacao.uuid}', None)
            return redirect('detalhe_paciente', paciente_id=avaliacao.paciente.uuid)

    titulo = 'PS2 Bebê (0–6 meses)' if faixa == 'bebe' else 'PS2 Criança Pequena (7–35 meses)'
    secoes_revisao, n_baixa, n_ausente = _montar_secoes_revisao(
        secoes_data, perguntas_data, respostas_atuais, confianca, extras=extras
    )

    return render(request, 'questionario/avaliacoes/importar_scan_ps2_revisao.html', {
        'avaliacao': avaliacao,
        'paciente': avaliacao.paciente,
        'secoes': secoes_revisao,
        'opcoes': OPCOES_PS2,
        'n_baixa': n_baixa,
        'n_ausente': n_ausente,
        'titulo': titulo,
    })


# ──────────────────────────────────────────────────────────────
# Perfil Sensorial do Adulto → AvaliacaoAdultoSensorial
# ──────────────────────────────────────────────────────────────

@login_required
def importar_scan_adulto_upload(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or not (perfil.tem_acesso('adulto_sensorial') or perfil.tem_acesso('sensorial')):
        messages.error(request, 'Você não tem acesso a este módulo.')
        return redirect('detalhe_paciente', paciente_id=paciente_id)

    template = 'questionario/avaliacoes/importar_scan_ps2_upload.html'
    ctx = {'paciente': paciente, 'tipo': 'adulto',
           'titulo': 'Perfil Sensorial do Adulto/Adolescente'}

    if request.method == 'GET':
        return render(request, template, ctx)

    arquivos, resp_erro = _validar_upload(request, template, ctx)
    if resp_erro:
        return resp_erro

    try:
        paginas = _arquivos_para_bytes(arquivos)
        # Adulto: colunas esq→dir = 1,2,3,4,5 (QN, R, O, F, QS)
        items_extraidos = processar_paginas_ps2(paginas, total_items=TOTAL_ITENS_ADULTO,
                                                col_values=[1, 2, 3, 4, 5])
    except Exception as exc:
        messages.error(request, f'Erro ao processar imagem: {exc}')
        return render(request, template, ctx)

    av = AvaliacaoAdultoSensorial.objects.create(
        paciente=paciente,
        status='em_andamento',
    )

    confianca = {}
    for num, info in items_extraidos.items():
        val = info.get('value')
        conf = info.get('confidence', 'missing')
        confianca[str(num)] = conf
        if val and 1 <= val <= 5:
            RespostaAdultoSensorial.objects.create(avaliacao=av, numero_item=num, valor=val)

    request.session[f'scan_conf_{av.uuid}'] = confianca
    return redirect('importar_scan_adulto_revisao', avaliacao_id=av.uuid)


@login_required
def importar_scan_adulto_revisao(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAdultoSensorial, uuid=avaliacao_id,
                                  paciente__medico=request.user)

    if avaliacao.status == 'concluida':
        return redirect('detalhe_paciente', paciente_id=avaliacao.paciente.uuid)

    respostas_atuais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    confianca_raw = request.session.get(f'scan_conf_{avaliacao.uuid}', {})
    confianca = {int(k): v for k, v in confianca_raw.items()}

    if request.method == 'POST':
        novas = {}
        erros = []
        for secao in SECOES_ADULTO:
            for item in secao['itens']:
                val = request.POST.get(f'item_{item}')
                if not val:
                    erros.append(item)
                else:
                    try:
                        v = int(val)
                        if 1 <= v <= 5:
                            novas[item] = v
                        else:
                            erros.append(item)
                    except (ValueError, TypeError):
                        erros.append(item)

        if erros:
            messages.error(request, f'Preencha os {len(erros)} item(ns) em destaque antes de confirmar.')
        else:
            for item, valor in novas.items():
                RespostaAdultoSensorial.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={'valor': valor}
                )
            respostas_finais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
            p = calcular_pontuacao_adulto(respostas_finais)
            avaliacao.pont_baixo_registro   = p.get("Q1", 0)
            avaliacao.pont_procura_sensacao = p.get("Q2", 0)
            avaliacao.pont_sensitividade    = p.get("Q3", 0)
            avaliacao.pont_evita_sensacao   = p.get("Q4", 0)
            avaliacao.status = 'concluida'
            avaliacao.save()
            request.session.pop(f'scan_conf_{avaliacao.uuid}', None)
            return redirect('detalhe_paciente', paciente_id=avaliacao.paciente.uuid)

    secoes_revisao, n_baixa, n_ausente = _montar_secoes_revisao(
        SECOES_ADULTO, PERGUNTAS_ADULTO, respostas_atuais, confianca
    )

    return render(request, 'questionario/avaliacoes/importar_scan_ps2_revisao.html', {
        'avaliacao': avaliacao,
        'paciente': avaliacao.paciente,
        'secoes': secoes_revisao,
        'opcoes': OPCOES_ADULTO,
        'n_baixa': n_baixa,
        'n_ausente': n_ausente,
        'titulo': 'Perfil Sensorial do Adulto/Adolescente',
    })


# ──────────────────────────────────────────────────────────────
# Utilitário compartilhado
# ──────────────────────────────────────────────────────────────

@login_required
def importar_scan_auto(request, paciente_id):
    """
    Import com detecção automática — paciente já conhecido (vindo do detalhe do paciente).
    POST step=detectar → JSON com tipo detectado
    POST step=importar  → roda OCR e redireciona para revisão
    """
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)

    if request.method == 'GET':
        return render(request, 'questionario/avaliacoes/importar_scan_auto.html',
                      {'paciente': paciente, 'modo': 'paciente'})

    arquivos = request.FILES.getlist('imagens')
    erro = _validar_arquivos(arquivos)
    if erro:
        return JsonResponse({'ok': False, 'erro': erro})

    try:
        paginas = _arquivos_para_bytes(arquivos)
    except Exception as e:
        return JsonResponse({'ok': False, 'erro': f'Erro ao processar arquivo: {e}'})

    step = request.POST.get('step', 'detectar')
    if step == 'detectar':
        return _detectar_json(paginas)

    tipo = request.POST.get('tipo', '')
    return _executar_import(request, paciente, tipo, paginas)


@login_required
def importar_scan_auto_novo_paciente(request):
    """
    Import com detecção automática — sem paciente (vindo do gerar-link).
    Passo extra: formulário de cadastro do paciente após detecção.
    """
    if request.method == 'GET':
        return render(request, 'questionario/avaliacoes/importar_scan_auto.html',
                      {'paciente': None, 'modo': 'novo_paciente'})

    arquivos = request.FILES.getlist('imagens')
    erro = _validar_arquivos(arquivos)
    if erro:
        return JsonResponse({'ok': False, 'erro': erro})

    try:
        paginas = _arquivos_para_bytes(arquivos)
    except Exception as e:
        return JsonResponse({'ok': False, 'erro': f'Erro ao processar arquivo: {e}'})

    step = request.POST.get('step', 'detectar')

    if step == 'detectar':
        return _detectar_json(paginas)

    if step == 'importar':
        # Cria o paciente com os dados do formulário
        nome         = request.POST.get('nome', '').strip()
        responsavel  = request.POST.get('responsavel', '').strip()
        data_nasc    = request.POST.get('data_nascimento', '').strip()
        tipo         = request.POST.get('tipo', '')

        if not nome or not data_nasc:
            return JsonResponse({'ok': False, 'erro': 'Nome e data de nascimento são obrigatórios.'})

        paciente = Paciente.objects.create(
            medico=request.user,
            nome=nome,
            responsavel=responsavel or nome,
            data_nascimento=data_nasc,
        )
        return _executar_import(request, paciente, tipo, paginas)

    return JsonResponse({'ok': False, 'erro': 'Passo inválido.'})


def _validar_arquivos(arquivos):
    if not arquivos:
        return 'Envie ao menos uma imagem ou PDF.'
    if len(arquivos) > 10:
        return 'Máximo de 10 arquivos.'
    invalidos = [a.name for a in arquivos
                 if not any(a.name.lower().endswith(e) for e in EXTENSOES_ACEITAS)]
    if invalidos:
        return f'Formato não suportado: {", ".join(invalidos)}'
    return None


def _detectar_json(paginas):
    from ..ocr.detector import detectar_instrumento
    try:
        resultado = detectar_instrumento(paginas)
        return JsonResponse({'ok': True, **resultado})
    except Exception as e:
        return JsonResponse({'ok': False, 'erro': f'Erro na detecção: {e}'})


def _executar_import(request, paciente, tipo, paginas):
    """Roda OCR e cria a avaliação para o tipo detectado/confirmado."""
    from ..ocr.spm_reader import processar_paginas_spm
    from ..ocr.ps2_reader import processar_paginas_ps2
    from ..models import AvaliacaoSPM, RespostaSPM
    from ..data.data_spm import PERGUNTAS_SPM_P, PERGUNTAS_SPM_CASA

    try:
        if tipo in ('spm_p', 'spm_casa', 'spm'):
            faixa = tipo if tipo != 'spm' else 'spm_p'
            items = processar_paginas_spm(paginas, total_items=75)
            av = AvaliacaoSPM.objects.create(
                paciente=paciente, faixa=faixa, token=str(uuid_mod.uuid4()), status='em_andamento'
            )
            confianca = {}
            for num, info in items.items():
                val = info.get('value')
                conf = info.get('confidence', 'missing')
                confianca[str(num)] = conf
                if val and val in {'N': 1, 'O': 2, 'F': 3, 'S': 4}:
                    RespostaSPM.objects.create(avaliacao=av, numero_item=num,
                                               valor={'N':1,'O':2,'F':3,'S':4}[val])
            request.session[f'scan_conf_{av.uuid}'] = confianca
            return redirect('importar_scan_spm_revisao', avaliacao_id=av.uuid)

        elif tipo == 'sensorial':
            items = processar_paginas_ps2(paginas, total_items=86, col_values=[5,4,3,2,1])
            av = Avaliacao.objects.create(
                paciente=paciente, token=str(uuid_mod.uuid4()), status='em_andamento'
            )
            confianca = {}
            for num, info in items.items():
                val = info.get('value')
                conf = info.get('confidence', 'missing')
                confianca[str(num)] = conf
                if val and 1 <= val <= 5:
                    Resposta.objects.create(avaliacao=av, numero_item=num, valor=val)
            request.session[f'scan_conf_{av.uuid}'] = confianca
            return redirect('importar_scan_ps2_crianca_revisao', avaliacao_id=av.uuid)

        elif tipo in ('ps2_bebe_wd', 'ps2_cp_wd'):
            faixa = 'bebe' if tipo == 'ps2_bebe_wd' else 'cp'
            total = 25 if faixa == 'bebe' else 54
            extras = [] if faixa == 'bebe' else ITENS_EXTRAS_PS2_CP
            items = processar_paginas_ps2(paginas, total_items=total, col_values=[5,4,3,2,1])
            av = AvaliacaoPS2Bebe.objects.create(
                paciente=paciente, faixa=faixa, token=str(uuid_mod.uuid4()), status='em_andamento'
            )
            confianca = {}
            for num, info in items.items():
                val = info.get('value')
                conf = info.get('confidence', 'missing')
                confianca[str(num)] = conf
                if val and 1 <= val <= 5:
                    RespostaPS2Bebe.objects.create(avaliacao=av, numero_item=num, valor=val)
            request.session[f'scan_conf_{av.uuid}'] = confianca
            return redirect('importar_scan_ps2_bebe_revisao', avaliacao_id=av.uuid)

        elif tipo == 'adulto_sensorial':
            items = processar_paginas_ps2(paginas, total_items=60,
                                          col_values=[1,2,3,4,5])
            av = AvaliacaoAdultoSensorial.objects.create(
                paciente=paciente, token=str(uuid_mod.uuid4()), status='em_andamento'
            )
            confianca = {}
            for num, info in items.items():
                val = info.get('value')
                conf = info.get('confidence', 'missing')
                confianca[str(num)] = conf
                if val and 1 <= val <= 5:
                    RespostaAdultoSensorial.objects.create(avaliacao=av, numero_item=num, valor=val)
            request.session[f'scan_conf_{av.uuid}'] = confianca
            return redirect('importar_scan_adulto_revisao', avaliacao_id=av.uuid)

    except Exception as e:
        messages.error(request, f'Erro ao processar: {e}')

    return redirect('detalhe_paciente', paciente_id=paciente.uuid)


@login_required
def ps2_bebe_wd_resultado(request, avaliacao_id):
    import json
    avaliacao = get_object_or_404(AvaliacaoPS2Bebe, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if avaliacao.status != 'concluida':
        return redirect('detalhe_paciente', paciente_id=paciente.uuid)

    faixa = avaliacao.faixa
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}

    if faixa == 'bebe':
        from ..data.data_ps2_bebe_wd import calcular_pontuacao_ps2_bebe, SECOES_PS2_BEBE
        p = calcular_pontuacao_ps2_bebe(respostas)
        secoes_data = SECOES_PS2_BEBE
        extras = []
    else:
        from ..data.data_ps2_cp_wd import calcular_pontuacao_ps2_cp, SECOES_PS2_CP, ITENS_EXTRAS_PS2_CP
        p = calcular_pontuacao_ps2_cp(respostas)
        secoes_data = SECOES_PS2_CP
        extras = ITENS_EXTRAS_PS2_CP

    if avaliacao.pont_ex is None:
        avaliacao.pont_ex = p.get('EX', 0)
        avaliacao.pont_ev = p.get('EV', 0)
        avaliacao.pont_sn = p.get('SN', 0)
        avaliacao.pont_ob = p.get('OB', 0)
        avaliacao.save(update_fields=['pont_ex', 'pont_ev', 'pont_sn', 'pont_ob'])

    QUAD_CONFIG = [
        {'id': 'EX', 'nome': 'Exploração',    'subtitulo': 'Busca sensorial',        'cor': '#E8793A', 'valor': avaliacao.pont_ex or 0},
        {'id': 'EV', 'nome': 'Esquiva',        'subtitulo': 'Evitamento sensorial',   'cor': '#6B8DD6', 'valor': avaliacao.pont_ev or 0},
        {'id': 'SN', 'nome': 'Sensibilidade',  'subtitulo': 'Sensitividade sensorial','cor': '#E8B84B', 'valor': avaliacao.pont_sn or 0},
        {'id': 'OB', 'nome': 'Observação',     'subtitulo': 'Baixo registro',         'cor': '#7DB87D', 'valor': avaliacao.pont_ob or 0},
    ]
    # Estimativa do máximo por quadrante com base nos itens
    quad_itens_count = {'EX': 0, 'EV': 0, 'SN': 0, 'OB': 0}
    from ..data.data_ps2_bebe_wd import QUADRANTE_PS2_BEBE
    from ..data.data_ps2_cp_wd import QUADRANTE_PS2_CP
    quad_map = QUADRANTE_PS2_BEBE if faixa == 'bebe' else QUADRANTE_PS2_CP
    for item, quad in quad_map.items():
        if quad and item not in extras:
            quad_itens_count[quad] = quad_itens_count.get(quad, 0) + 1
    for q in QUAD_CONFIG:
        cnt = quad_itens_count.get(q['id'], 1)
        q['maximo'] = cnt * 5
        q['pct'] = min(100, int(q['valor'] / q['maximo'] * 100)) if q['maximo'] else 0
        q['classificacao'] = _classificar_ps2(q['pct'])

    # Seções com pontuação e %
    SECOES = []
    for s in secoes_data:
        itens = [i for i in s['itens'] if i not in extras]
        maximo = len(itens) * 5
        valor = p.get(s['id'], 0)
        pct = min(100, int(valor / maximo * 100)) if maximo else 0
        SECOES.append({
            'nome': s['nome'], 'valor': valor, 'maximo': maximo, 'pct': pct,
            'classificacao': _classificar_ps2(pct),
            'classe_css': _classe_css(pct),
        })

    todas = list(paciente.avaliacoes_ps2_bebe.filter(status='concluida').order_by('data'))
    outras = [a for a in todas if a.id != avaliacao.id]
    comp_labels = json.dumps([a.data.strftime('%d/%m/%Y') for a in todas])
    comp_datasets = json.dumps([
        {'label': q['nome'],
         'data': [min(100, int((getattr(a, f"pont_{q['id'].lower()}") or 0) / q['maximo'] * 100)) if q['maximo'] else 0 for a in todas],
         'borderColor': q['cor'], 'backgroundColor': q['cor'] + '33', 'tension': 0.3}
        for q in QUAD_CONFIG
    ])

    return render(request, 'questionario/avaliacoes/ps2_bebe_resultado.html', {
        'avaliacao': avaliacao, 'paciente': paciente,
        'quadrantes': QUAD_CONFIG,
        'secoes': SECOES,
        'radar_labels': json.dumps([s['nome'].replace('Processamento ', '').replace(' este bebê...', '').replace(' (Winnie Dunn)', '') for s in SECOES]),
        'radar_valores': json.dumps([s['pct'] for s in SECOES]),
        'quad_labels': json.dumps([q['nome'] for q in QUAD_CONFIG]),
        'quad_valores': json.dumps([q['pct'] for q in QUAD_CONFIG]),
        'quad_cores': json.dumps([q['cor'] for q in QUAD_CONFIG]),
        'comp_labels': comp_labels, 'comp_datasets': comp_datasets,
        'tem_comparativo': len(todas) > 1, 'outras_avaliacoes': outras,
    })


@login_required
def adulto_sensorial_resultado(request, avaliacao_id):
    import json
    avaliacao = get_object_or_404(AvaliacaoAdultoSensorial, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if avaliacao.status != 'concluida':
        return redirect('detalhe_paciente', paciente_id=paciente.uuid)

    from ..data.data_adulto_sensorial import (
        calcular_pontuacao_adulto, QUADRANTES_CONFIG_ADULTO, SECOES_ADULTO
    )
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    p = calcular_pontuacao_adulto(respostas)

    if avaliacao.pont_baixo_registro is None:
        avaliacao.pont_baixo_registro   = p.get('Q1', 0)
        avaliacao.pont_procura_sensacao = p.get('Q2', 0)
        avaliacao.pont_sensitividade    = p.get('Q3', 0)
        avaliacao.pont_evita_sensacao   = p.get('Q4', 0)
        avaliacao.save(update_fields=['pont_baixo_registro','pont_procura_sensacao','pont_sensitividade','pont_evita_sensacao'])

    cores = ['#6B48C8', '#E8793A', '#E8B84B', '#6B8DD6']
    campo_map = {
        'Q1': avaliacao.pont_baixo_registro   or 0,
        'Q2': avaliacao.pont_procura_sensacao or 0,
        'Q3': avaliacao.pont_sensitividade    or 0,
        'Q4': avaliacao.pont_evita_sensacao   or 0,
    }
    QUAD_CONFIG = []
    subtitulos = {'Q1': 'Não percebe estímulos', 'Q2': 'Busca estímulos', 'Q3': 'Detecta com facilidade', 'Q4': 'Evita estímulos'}
    for i, (qid, cfg) in enumerate(QUADRANTES_CONFIG_ADULTO.items()):
        valor = campo_map[qid]
        pct = min(100, int(valor / cfg['max'] * 100)) if cfg['max'] else 0
        classificacao = '—'
        for min_v, max_v, label in cfg['faixas']:
            if min_v <= valor <= max_v:
                classificacao = label
                break
        QUAD_CONFIG.append({'id': qid, 'nome': cfg['nome'], 'subtitulo': subtitulos.get(qid, ''),
                            'cor': cores[i], 'valor': valor, 'maximo': cfg['max'],
                            'pct': pct, 'classificacao': classificacao})

    # Seções
    SECOES = []
    for s in SECOES_ADULTO:
        maximo = len(s['itens']) * 5
        valor = p.get(s['id'], 0)
        pct = min(100, int(valor / maximo * 100)) if maximo else 0
        SECOES.append({
            'nome': s['nome'], 'valor': valor, 'maximo': maximo, 'pct': pct,
            'classificacao': _classificar_ps2(pct),
            'classe_css': _classe_css(pct),
        })

    todas = list(paciente.avaliacoes_adulto_sensorial.filter(status='concluida').order_by('data'))
    outras = [a for a in todas if a.id != avaliacao.id]
    comp_labels = json.dumps([a.data.strftime('%d/%m/%Y') for a in todas])
    campos_quad = ['pont_baixo_registro','pont_procura_sensacao','pont_sensitividade','pont_evita_sensacao']
    comp_datasets = json.dumps([
        {'label': q['nome'],
         'data': [min(100, int((getattr(a, campos_quad[i]) or 0) / q['maximo'] * 100)) if q['maximo'] else 0 for a in todas],
         'borderColor': q['cor'], 'backgroundColor': q['cor'] + '33', 'tension': 0.3}
        for i, q in enumerate(QUAD_CONFIG)
    ])

    return render(request, 'questionario/avaliacoes/adulto_sensorial_resultado.html', {
        'avaliacao': avaliacao, 'paciente': paciente,
        'quadrantes': QUAD_CONFIG,
        'secoes': SECOES,
        'radar_labels': json.dumps([s['nome'].split('.')[1].strip() if '.' in s['nome'] else s['nome'] for s in SECOES]),
        'radar_valores': json.dumps([s['pct'] for s in SECOES]),
        'quad_labels': json.dumps([q['nome'] for q in QUAD_CONFIG]),
        'quad_valores': json.dumps([q['pct'] for q in QUAD_CONFIG]),
        'quad_cores': json.dumps([q['cor'] for q in QUAD_CONFIG]),
        'comp_labels': comp_labels, 'comp_datasets': comp_datasets,
        'tem_comparativo': len(todas) > 1, 'outras_avaliacoes': outras,
    })


@login_required
def ps2_bebe_wd_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoPS2Bebe, uuid=avaliacao_id, paciente__medico=request.user)
    faixa = avaliacao.faixa
    secoes       = SECOES_PS2_BEBE if faixa == 'bebe' else SECOES_PS2_CP
    perguntas_d  = PERGUNTAS_PS2_BEBE if faixa == 'bebe' else PERGUNTAS_PS2_CP
    extras       = [] if faixa == 'bebe' else ITENS_EXTRAS_PS2_CP
    opcoes       = OPCOES_PS2
    total = len(secoes)
    if pagina < 1 or pagina > total:
        return redirect('ps2_bebe_wd_visualizar', avaliacao_id=avaliacao_id, pagina=1)
    secao_atual = secoes[pagina - 1]
    itens = [i for i in secao_atual['itens'] if i not in extras]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens)}
    perguntas = [{'numero': i, 'texto': perguntas_d.get(i, ''), 'resposta_salva': respostas_salvas.get(i)} for i in itens]
    return render(request, 'questionario/avaliacoes/bebe_form.html', {
        'avaliacao': avaliacao, 'secao': secao_atual, 'perguntas': perguntas,
        'opcoes': opcoes, 'pagina': pagina, 'total': total,
        'progresso': int((pagina - 1) / total * 100),
        'paginas_secoes': [(i + 1, secoes[i]['nome']) for i in range(total)],
        'pagina_anterior': pagina - 1 if pagina > 1 else None,
        'readonly': True,
        'resultado_url': 'ps2_bebe_wd_resultado',
        'resultado_uuid': avaliacao.uuid,
    })


@login_required
def adulto_sensorial_visualizar(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoAdultoSensorial, uuid=avaliacao_id, paciente__medico=request.user)
    total = len(SECOES_ADULTO)
    if pagina < 1 or pagina > total:
        return redirect('adulto_sensorial_visualizar', avaliacao_id=avaliacao_id, pagina=1)
    secao_atual = SECOES_ADULTO[pagina - 1]
    itens = secao_atual['itens']
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens)}
    perguntas = [{'numero': i, 'texto': PERGUNTAS_ADULTO.get(i, ''), 'resposta_salva': respostas_salvas.get(i)} for i in itens]
    return render(request, 'questionario/avaliacoes/bebe_form.html', {
        'avaliacao': avaliacao, 'secao': secao_atual, 'perguntas': perguntas,
        'opcoes': OPCOES_ADULTO, 'pagina': pagina, 'total': total,
        'progresso': int((pagina - 1) / total * 100),
        'paginas_secoes': [(i + 1, SECOES_ADULTO[i]['nome']) for i in range(total)],
        'pagina_anterior': pagina - 1 if pagina > 1 else None,
        'readonly': True,
        'resultado_url': 'adulto_sensorial_resultado',
        'resultado_uuid': avaliacao.uuid,
    })


@login_required
def salvar_observacoes_ps2_bebe(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoPS2Bebe, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == 'POST':
        avaliacao.observacoes = request.POST.get('observacoes', '').strip()
        avaliacao.save(update_fields=['observacoes'])
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
        messages.success(request, 'Observações salvas.')
    return redirect('ps2_bebe_wd_resultado', avaliacao_id=avaliacao_id)


@login_required
def salvar_observacoes_adulto_sensorial(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoAdultoSensorial, uuid=avaliacao_id, paciente__medico=request.user)
    if request.method == 'POST':
        avaliacao.observacoes = request.POST.get('observacoes', '').strip()
        avaliacao.save(update_fields=['observacoes'])
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
        messages.success(request, 'Observações salvas.')
    return redirect('adulto_sensorial_resultado', avaliacao_id=avaliacao_id)


@login_required
def nova_avaliacao_ps2_bebe_wd(request, paciente_id):
    from django.http import JsonResponse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or not (perfil.tem_acesso('ps2_bebe_wd') or perfil.tem_acesso('bebe')):
        return JsonResponse({"ok": False, "error": "Módulo não disponível."}, status=403)
    import uuid as _uuid
    av = AvaliacaoPS2Bebe.objects.create(paciente=paciente, faixa='bebe', token=str(_uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("detalhe_paciente", paciente_id=paciente_id)


@login_required
def nova_avaliacao_ps2_cp_wd(request, paciente_id):
    from django.http import JsonResponse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or not (perfil.tem_acesso('ps2_cp_wd') or perfil.tem_acesso('bebe')):
        return JsonResponse({"ok": False, "error": "Módulo não disponível."}, status=403)
    import uuid as _uuid
    av = AvaliacaoPS2Bebe.objects.create(paciente=paciente, faixa='cp', token=str(_uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("detalhe_paciente", paciente_id=paciente_id)


@login_required
def nova_avaliacao_adulto_sensorial(request, paciente_id):
    from django.http import JsonResponse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or not (perfil.tem_acesso('adulto_sensorial') or perfil.tem_acesso('sensorial')):
        return JsonResponse({"ok": False, "error": "Módulo não disponível."}, status=403)
    import uuid as _uuid
    av = AvaliacaoAdultoSensorial.objects.create(paciente=paciente, token=str(_uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(av.uuid)})
    return redirect("detalhe_paciente", paciente_id=paciente_id)


@login_required
def ps2_bebe_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    av = get_object_or_404(AvaliacaoPS2Bebe, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = av.paciente.uuid
    if request.method == "POST":
        av.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação PS2 excluída com sucesso."})
        messages.success(request, "Avaliação PS2 excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def adulto_sensorial_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    av = get_object_or_404(AvaliacaoAdultoSensorial, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = av.paciente.uuid
    if request.method == "POST":
        av.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação excluída com sucesso."})
        messages.success(request, "Avaliação excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


def _montar_secoes_revisao(secoes_data, perguntas_data, respostas_atuais,
                            confianca, extras=None):
    extras = extras or []
    n_baixa = 0
    n_ausente = 0
    secoes_revisao = []

    for secao in secoes_data:
        itens = []
        for num in secao['itens']:
            if num in extras:
                continue
            conf = confianca.get(num, 'missing')
            valor = respostas_atuais.get(num)
            if valor is None:
                n_ausente += 1
            elif conf == 'low':
                n_baixa += 1
            itens.append({
                'numero': num,
                'texto': perguntas_data.get(num, ''),
                'valor': valor,
                'confianca': conf,
            })
        secoes_revisao.append({'id': secao['id'], 'nome': secao['nome'], 'itens': itens})

    return secoes_revisao, n_baixa, n_ausente
