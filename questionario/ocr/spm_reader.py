"""
Leitura óptica de formulários SPM preenchidos à mão.

Lógica:
  - O formulário SPM tem 4 colunas de resposta (N, O, F, S) sempre na lateral esquerda
  - Cada linha de item tem UMA marcação (X, círculo, traço) em uma das colunas
  - A célula marcada tem densidade de pixels escuros notavelmente maior que as outras
  - Linhas de cabeçalho de seção têm distribuição uniforme → são descartadas

Limitações:
  - Fotos muito inclinadas (> 5°) reduzem a precisão
  - Marcações muito leves podem ser classificadas como "não detectado"
  - Resultado sempre exibe tela de revisão para o profissional confirmar
"""

import io
import numpy as np
from PIL import Image, ImageFilter

# Posição das colunas de resposta como fração da largura da imagem
# Calibrado para o formulário SPM-P e SPM Casa (layout padrão)
ANSWER_X1 = 0.02   # início da área de resposta
ANSWER_X2 = 0.24   # fim da área de resposta (4 colunas de N, O, F, S)

COL_LABELS = ['N', 'O', 'F', 'S']

# Limiar mínimo de densidade para considerar que existe alguma marca na linha
ROW_MIN_DENSITY = 0.025

# Razão entre a célula mais marcada e a segunda para classificar confiança
HIGH_CONF_RATIO = 2.2
LOW_CONF_RATIO  = 1.35

# Variância mínima entre as 4 colunas — abaixo disso é cabeçalho (distribuição uniforme)
MIN_VARIANCE = 0.0003


def _load_and_normalize(img_bytes: bytes, target_height: int = 2800):
    """Carrega imagem, redimensiona para altura padrão e retorna array grayscale normalizado."""
    img = Image.open(io.BytesIO(img_bytes)).convert('L')
    w, h = img.size
    new_w = int(w * target_height / h)
    img = img.resize((new_w, target_height), Image.LANCZOS)
    return img, (new_w, target_height)


def _to_binary(img: Image.Image) -> np.ndarray:
    """
    Converte para array binário usando threshold adaptativo local.
    Pixels mais escuros que a média local → 1 (marca), resto → 0.
    """
    arr = np.array(img, dtype=np.float32)
    blur = np.array(img.filter(ImageFilter.GaussianBlur(radius=11)), dtype=np.float32)
    # Marca detectada onde pixel é significativamente mais escuro que o fundo local
    binary = (arr < blur - 14).astype(np.float32)
    return binary


def _find_content_rows(binary: np.ndarray, ax1: int, ax2: int,
                       min_height: int = 12, merge_gap: int = 5) -> list:
    """
    Encontra intervalos verticais (y1, y2) com conteúdo na área de resposta.
    Usa projeção horizontal — soma de pixels escuros por linha.
    """
    proj = binary[:, ax1:ax2].mean(axis=1)
    has_content = proj > ROW_MIN_DENSITY

    rows = []
    in_row = False
    y_start = 0
    gap = 0

    for i, active in enumerate(has_content):
        if active:
            if not in_row:
                y_start = i
                in_row = True
            gap = 0
        else:
            if in_row:
                gap += 1
                if gap > merge_gap:
                    height = i - gap - y_start
                    if height >= min_height:
                        rows.append((y_start, i - gap))
                    in_row = False
                    gap = 0

    if in_row:
        h = binary.shape[0]
        if h - y_start >= min_height:
            rows.append((y_start, h))

    return rows


def _cell_density(binary: np.ndarray, y1: int, y2: int, x1: int, x2: int) -> float:
    """Densidade de pixels marcados em uma célula (0–1)."""
    if y2 <= y1 or x2 <= x1:
        return 0.0
    cell = binary[y1:y2, x1:x2]
    return float(cell.mean()) if cell.size > 0 else 0.0


def _classify_row(densities: list):
    """
    Dado o array de densidades das 4 colunas [N, O, F, S], retorna:
      (label, confidence) onde label ∈ {'N','O','F','S', None}
      e confidence ∈ {'high', 'low', 'missing'}
    """
    densities = list(densities)
    max_d = max(densities)

    # Linha sem nenhuma marca relevante
    if max_d < ROW_MIN_DENSITY:
        return None, 'missing'

    # Variância muito baixa → distribuição uniforme → cabeçalho ou linha vazia
    if np.var(densities) < MIN_VARIANCE:
        return None, 'missing'

    sorted_d = sorted(densities, reverse=True)
    second_d = max(sorted_d[1], 0.001)
    ratio = max_d / second_d

    max_idx = int(np.argmax(densities))
    label = COL_LABELS[max_idx]

    if ratio >= HIGH_CONF_RATIO:
        return label, 'high'
    elif ratio >= LOW_CONF_RATIO:
        return label, 'low'
    else:
        # Ambíguo — duas colunas com densidade similar
        return None, 'missing'


def processar_paginas_spm(paginas_bytes: list, total_items: int = 75) -> dict:
    """
    Processa uma lista de imagens (páginas do formulário SPM) e retorna as respostas detectadas.

    Args:
        paginas_bytes: lista de bytes, uma entrada por página/imagem enviada
        total_items:   75 para SPM-P e SPM Casa

    Returns:
        dict com chave = número do item (int), valor = dict:
            {'value': 'N'|'O'|'F'|'S'|None, 'confidence': 'high'|'low'|'missing'}
    """
    resultados = {}
    item_counter = 1

    for pg_bytes in paginas_bytes:
        if item_counter > total_items:
            break

        img, (W, H) = _load_and_normalize(pg_bytes)
        binary = _to_binary(img)

        ax1 = int(ANSWER_X1 * W)
        ax2 = int(ANSWER_X2 * W)
        col_w = (ax2 - ax1) // 4
        col_bounds = [(ax1 + i * col_w, ax1 + (i + 1) * col_w) for i in range(4)]

        rows = _find_content_rows(binary, ax1, ax2)

        for y1, y2 in rows:
            if item_counter > total_items:
                break

            densities = [_cell_density(binary, y1, y2, cx1, cx2)
                         for cx1, cx2 in col_bounds]

            label, confidence = _classify_row(densities)

            # Linhas classificadas como 'missing' com densidade muito baixa são cabeçalhos
            # — pula sem incrementar o contador de itens
            if confidence == 'missing' and max(densities) < ROW_MIN_DENSITY * 1.5:
                continue

            resultados[item_counter] = {'value': label, 'confidence': confidence}
            item_counter += 1

    # Garante que todos os itens estão no resultado, mesmo que não detectados
    for i in range(1, total_items + 1):
        if i not in resultados:
            resultados[i] = {'value': None, 'confidence': 'missing'}

    return resultados
