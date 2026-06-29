"""
Detecção automática do tipo de instrumento a partir das imagens do formulário.

Lógica:
  1. Verifica se as colunas de resposta estão na ESQUERDA (SPM) ou DIREITA (PS2/Adulto)
  2. Conta o total de linhas com conteúdo em todas as páginas
  3. Mapeia a contagem para o instrumento mais provável
"""

import numpy as np
from .spm_reader import (
    _load_and_normalize, _to_binary, _find_content_rows, ROW_MIN_DENSITY
)

# Limites para classificação pelo total de linhas detectadas
FAIXAS = [
    (0,  35,  'ps2_bebe_wd',    'PS2 Bebê (0–6 meses)'),
    (35, 60,  'ps2_cp_wd',      'PS2 Criança Pequena (7–35 meses)'),
    (60, 72,  'adulto_sensorial','Perfil Sensorial Adulto/Adolescente'),
    (72, 82,  'spm',            'SPM — Sensory Processing Measure'),
    (82, 999, 'sensorial',      'Perfil Sensorial 2 — Criança (3–14 anos)'),
]


def detectar_instrumento(paginas_bytes: list) -> dict:
    """
    Analisa as páginas e retorna o instrumento detectado.

    Returns:
        {
          'tipo':         str  — chave do instrumento
          'label':        str  — nome legível
          'confianca':    'alta' | 'baixa'
          'total_linhas': int
          'coluna_lado':  'esquerda' | 'direita'
        }
    """
    if not paginas_bytes:
        return {'tipo': None, 'label': 'Não detectado', 'confianca': 'baixa',
                'total_linhas': 0, 'coluna_lado': None}

    # ── Passo 1: determinar lado das colunas usando a 1ª página ──────────────
    img0, (W0, H0) = _load_and_normalize(paginas_bytes[0])
    binary0 = _to_binary(img0)

    left_area  = binary0[:, int(0.02 * W0): int(0.25 * W0)]
    right_area = binary0[:, int(0.60 * W0): int(0.97 * W0)]

    left_d  = float(left_area.mean())
    right_d = float(right_area.mean())

    is_spm = left_d > right_d * 1.2   # colunas na esquerda → SPM
    coluna_lado = 'esquerda' if is_spm else 'direita'

    # ── Passo 2: contar linhas com conteúdo em todas as páginas ─────────────
    total_linhas = 0
    for pg_bytes in paginas_bytes:
        img, (W, H) = _load_and_normalize(pg_bytes)
        binary = _to_binary(img)

        if is_spm:
            ax1, ax2 = int(0.02 * W), int(0.25 * W)
            n_cols = 4
        else:
            ax1, ax2 = int(0.60 * W), int(0.97 * W)
            n_cols = 5

        rows = _find_content_rows(binary, ax1, ax2)
        col_w = (ax2 - ax1) // n_cols

        for y1, y2 in rows:
            densidades = [
                float(binary[y1:y2, ax1 + i * col_w: ax1 + (i+1) * col_w].mean())
                for i in range(n_cols)
            ]
            # Só conta linhas que têm pelo menos uma marca real
            if max(densidades) >= ROW_MIN_DENSITY * 1.5:
                total_linhas += 1

    # ── Passo 3: mapear para instrumento ─────────────────────────────────────
    if is_spm:
        tipo  = 'spm'
        label = 'SPM — Sensory Processing Measure'
    else:
        tipo  = 'sensorial'        # fallback
        label = 'Desconhecido'
        for min_l, max_l, t, l in FAIXAS:
            if min_l <= total_linhas < max_l:
                tipo  = t
                label = l
                break

    confianca = 'alta' if total_linhas >= 8 else 'baixa'

    # ── Passo 4: tentar extrair dados do cabeçalho (requer tesseract) ─────────
    dados_cabecalho = _extrair_cabecalho(paginas_bytes[0])

    return {
        'tipo':         tipo,
        'label':        label,
        'confianca':    confianca,
        'total_linhas': total_linhas,
        'coluna_lado':  coluna_lado,
        **dados_cabecalho,
    }


def _extrair_cabecalho(pg_bytes: bytes) -> dict:
    """
    Tenta extrair nome e data de nascimento do cabeçalho do formulário.
    Retorna campos vazios se tesseract não estiver instalado.
    """
    resultado = {'nome_detectado': '', 'nasc_detectado': '', 'resp_detectado': ''}
    try:
        import pytesseract
        import re
        from PIL import Image
        import io as _io

        img = Image.open(_io.BytesIO(pg_bytes)).convert('RGB')
        w, h = img.size
        # Região do cabeçalho: topo 35% da página
        cabecalho = img.crop((0, 0, w, int(h * 0.35)))
        cabecalho = cabecalho.resize((cabecalho.width * 2, cabecalho.height * 2), Image.LANCZOS)

        texto = pytesseract.image_to_string(cabecalho, lang='por', config='--psm 6')

        # Nome da criança — procura padrões como "Primeiro nome: Xxx" ou "Nome: Xxx"
        for padrao in [
            r'(?:rimeiro\s+nome|Nome\s+da\s+crian)[^\n:]*[:\s]+([A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕ][a-záéíóúâêîôûàèìòùãõ]+(?:\s+[A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕ][a-záéíóúâêîôûàèìòùãõ]+)*)',
            r'Nome[^\n:]*:\s*([A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕ][a-záéíóúâêîôûàèìòùãõ]+(?:\s+[A-Z][a-záéíóúâ]+)*)',
        ]:
            m = re.search(padrao, texto, re.IGNORECASE)
            if m:
                resultado['nome_detectado'] = m.group(1).strip()
                break

        # Sobrenome (PS2 tem campo separado)
        m_sobre = re.search(r'Sobrenome[^\n:]*:\s*([A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕ][a-záéíóúâêîôûàèìòùãõ ]+)', texto, re.IGNORECASE)
        if m_sobre and resultado['nome_detectado']:
            resultado['nome_detectado'] = resultado['nome_detectado'] + ' ' + m_sobre.group(1).strip()

        # Data de nascimento — padrão dd/mm/aaaa ou dd/mm/aa
        m_nasc = re.search(r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})', texto)
        if m_nasc:
            d, mes, a = m_nasc.group(1), m_nasc.group(2), m_nasc.group(3)
            if len(a) == 2:
                a = '20' + a if int(a) <= 30 else '19' + a
            resultado['nasc_detectado'] = f'{a}-{mes.zfill(2)}-{d.zfill(2)}'

        # Responsável/cuidador
        for padrao in [
            r'(?:cuidador|respons[aá]vel|preenchi)[^\n:]*:\s*([A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕ][a-záéíóúâêîôûàèìòùãõ]+(?:\s+[A-Z][a-záéíóú]+)*)',
        ]:
            m = re.search(padrao, texto, re.IGNORECASE)
            if m:
                resultado['resp_detectado'] = m.group(1).strip()
                break

    except Exception:
        pass  # tesseract não disponível ou erro — campos ficam vazios

    return resultado
