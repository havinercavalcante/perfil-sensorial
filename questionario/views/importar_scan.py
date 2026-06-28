import io
import uuid as uuid_mod

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..models import AvaliacaoSPM, Paciente, RespostaSPM
from ..data.data_spm import (
    OPCOES_SPM,
    PERGUNTAS_SPM_P,
    PERGUNTAS_SPM_CASA,
    SECOES_SPM_P,
    SECOES_SPM_CASA,
)
from ..ocr.spm_reader import processar_paginas_spm
from .spm import _spm_salvar_pontuacao

LABEL_TO_VALUE = {'N': 1, 'O': 2, 'F': 3, 'S': 4}

EXTENSOES_ACEITAS = {'.jpg', '.jpeg', '.png', '.webp', '.pdf'}


def _arquivos_para_bytes(arquivos):
    """
    Converte UploadedFiles para lista de bytes prontos para o leitor OCR.
    PDFs são convertidos em imagens JPEG (uma por página).
    """
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


@login_required
def importar_scan_spm_upload(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)

    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('spm'):
        messages.error(request, 'Você não tem acesso ao módulo SPM.')
        return redirect('detalhe_paciente', paciente_id=paciente_id)

    if request.method == 'GET':
        return render(request, 'questionario/avaliacoes/importar_scan_upload.html', {
            'paciente': paciente,
        })

    faixa = request.POST.get('faixa', 'spm_p')
    if faixa not in ('spm_p', 'spm_casa'):
        faixa = 'spm_p'

    arquivos = request.FILES.getlist('imagens')
    if not arquivos:
        messages.error(request, 'Envie ao menos uma imagem ou PDF do formulário.')
        return render(request, 'questionario/avaliacoes/importar_scan_upload.html', {'paciente': paciente})

    if len(arquivos) > 10:
        messages.error(request, 'Máximo de 10 arquivos por vez.')
        return render(request, 'questionario/avaliacoes/importar_scan_upload.html', {'paciente': paciente})

    # Valida extensões
    invalidos = [a.name for a in arquivos
                 if not any(a.name.lower().endswith(e) for e in EXTENSOES_ACEITAS)]
    if invalidos:
        messages.error(request, f'Formato não suportado: {", ".join(invalidos)}. Use JPG, PNG ou PDF.')
        return render(request, 'questionario/avaliacoes/importar_scan_upload.html', {'paciente': paciente})

    try:
        paginas = _arquivos_para_bytes(arquivos)
        items_extraidos = processar_paginas_spm(paginas, total_items=75)
    except Exception as exc:
        messages.error(request, f'Erro ao processar imagem: {exc}')
        return render(request, 'questionario/avaliacoes/importar_scan_upload.html', {'paciente': paciente})

    av = AvaliacaoSPM.objects.create(
        paciente=paciente,
        faixa=faixa,
        token=str(uuid_mod.uuid4()),
        status='em_andamento',
    )

    confianca_por_item = {}
    for num, info in items_extraidos.items():
        label = info.get('value')
        conf = info.get('confidence', 'missing')
        confianca_por_item[str(num)] = conf
        if label and label in LABEL_TO_VALUE:
            RespostaSPM.objects.create(
                avaliacao=av,
                numero_item=num,
                valor=LABEL_TO_VALUE[label],
            )

    request.session[f'scan_conf_{av.uuid}'] = confianca_por_item
    return redirect('importar_scan_spm_revisao', avaliacao_id=av.uuid)


@login_required
def importar_scan_spm_revisao(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoSPM, uuid=avaliacao_id, paciente__medico=request.user)

    if avaliacao.status == 'concluida':
        return redirect('spm_resultado', avaliacao_id=avaliacao_id)

    secoes = SECOES_SPM_P if avaliacao.faixa == 'spm_p' else SECOES_SPM_CASA
    perguntas_data = PERGUNTAS_SPM_P if avaliacao.faixa == 'spm_p' else PERGUNTAS_SPM_CASA

    respostas_atuais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    confianca_raw = request.session.get(f'scan_conf_{avaliacao.uuid}', {})
    confianca = {int(k): v for k, v in confianca_raw.items()}

    if request.method == 'POST':
        novas = {}
        erros = []
        for secao in secoes:
            for item in secao['itens']:
                val = request.POST.get(f'item_{item}')
                if not val:
                    erros.append(item)
                else:
                    try:
                        v = int(val)
                        if 1 <= v <= 4:
                            novas[item] = v
                        else:
                            erros.append(item)
                    except (ValueError, TypeError):
                        erros.append(item)

        if erros:
            messages.error(request, f'Preencha os {len(erros)} item(ns) em destaque antes de confirmar.')
        else:
            for item, valor in novas.items():
                RespostaSPM.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={'valor': valor}
                )
            avaliacao = _spm_salvar_pontuacao(avaliacao)
            avaliacao.status = 'concluida'
            avaliacao.save()
            request.session.pop(f'scan_conf_{avaliacao.uuid}', None)
            return redirect('spm_resultado', avaliacao_id=avaliacao_id)

    # Monta seções para o template
    secoes_revisao = []
    n_baixa = 0
    n_ausente = 0

    for secao in secoes:
        itens = []
        for num in secao['itens']:
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

    return render(request, 'questionario/avaliacoes/importar_scan_revisao_spm.html', {
        'avaliacao': avaliacao,
        'paciente': avaliacao.paciente,
        'secoes': secoes_revisao,
        'opcoes': OPCOES_SPM,
        'n_baixa': n_baixa,
        'n_ausente': n_ausente,
    })
