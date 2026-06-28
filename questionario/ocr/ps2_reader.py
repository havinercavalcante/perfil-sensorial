"""
Leitura óptica de formulários Perfil Sensorial 2 (PS2) e Perfil Sensorial do Adulto.

Diferença do SPM: as colunas de resposta ficam na DIREITA da página.

PS2 (Criança, Bebê, Criança Pequena):
  colunas esquerda→direita: 5 | 4 | 3 | 2 | 1  (+ NSA na borda, ignorado)
  Escala: 5=Quase sempre … 1=Quase nunca

Perfil Sensorial do Adulto:
  colunas esquerda→direita: 1 | 2 | 3 | 4 | 5
  Escala: 1=Quase nunca … 5=Quase sempre
"""

import io
import numpy as np
from PIL import Image, ImageFilter

# Posição das colunas de resposta na imagem (fração da largura)
# O grid de 5 colunas ocupa aproximadamente os 37% direitos da folha
ANSWER_X1_DEFAULT = 0.60
ANSWER_X2_DEFAULT = 0.97

ROW_MIN_DENSITY = 0.020
HIGH_CONF_RATIO  = 2.0
LOW_CONF_RATIO   = 1.30
MIN_VARIANCE     = 0.0002


def _load_and_normalize(img_bytes: bytes, target_height: int = 2800):
    img = Image.open(io.BytesIO(img_bytes)).convert('L')
    w, h = img.size
    new_w = int(w * target_height / h)
    img = img.resize((new_w, target_height), Image.LANCZOS)
    return img, (new_w, target_height)


def _to_binary(img: Image.Image) -> np.ndarray:
    arr  = np.array(img, dtype=np.float32)
    blur = np.array(img.filter(ImageFilter.GaussianBlur(radius=11)), dtype=np.float32)
    return (arr < blur - 12).astype(np.float32)


def _find_content_rows(binary: np.ndarray, ax1: int, ax2: int,
                       min_height: int = 10, merge_gap: int = 6) -> list:
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
    if y2 <= y1 or x2 <= x1:
        return 0.0
    cell = binary[y1:y2, x1:x2]
    return float(cell.mean()) if cell.size > 0 else 0.0


def _classify_row(densities: list, col_values: list):
    """
    Dado o array de densidades por coluna e os valores de cada coluna,
    retorna (valor_int|None, confiança).
    """
    max_d = max(densities)

    if max_d < ROW_MIN_DENSITY:
        return None, 'missing'

    if np.var(densities) < MIN_VARIANCE:
        return None, 'missing'

    sorted_d = sorted(densities, reverse=True)
    second_d = max(sorted_d[1], 0.001)
    ratio = max_d / second_d

    max_idx = int(np.argmax(densities))
    value = col_values[max_idx]

    if ratio >= HIGH_CONF_RATIO:
        return value, 'high'
    elif ratio >= LOW_CONF_RATIO:
        return value, 'low'
    else:
        return None, 'missing'


def processar_paginas_ps2(paginas_bytes: list,
                           total_items: int,
                           col_values: list = None,
                           answer_x1: float = ANSWER_X1_DEFAULT,
                           answer_x2: float = ANSWER_X2_DEFAULT) -> dict:
    """
    Processa páginas de formulários PS2 e retorna as respostas detectadas.

    Args:
        paginas_bytes : lista de bytes (uma por imagem/página)
        total_items   : total de itens esperados no formulário
        col_values    : valores de cada coluna, esq→dir.
                        PS2 padrão: [5, 4, 3, 2, 1]
                        Adulto:     [1, 2, 3, 4, 5]
        answer_x1     : início da área de colunas (fração da largura)
        answer_x2     : fim da área de colunas

    Returns:
        dict {num_item: {'value': int|None, 'confidence': 'high'|'low'|'missing'}}
    """
    if col_values is None:
        col_values = [5, 4, 3, 2, 1]

    n_cols = len(col_values)
    resultados = {}
    item_counter = 1

    for pg_bytes in paginas_bytes:
        if item_counter > total_items:
            break

        img, (W, H) = _load_and_normalize(pg_bytes)
        binary = _to_binary(img)

        ax1 = int(answer_x1 * W)
        ax2 = int(answer_x2 * W)
        col_w = (ax2 - ax1) // n_cols
        col_bounds = [(ax1 + i * col_w, ax1 + (i + 1) * col_w) for i in range(n_cols)]

        rows = _find_content_rows(binary, ax1, ax2)

        for y1, y2 in rows:
            if item_counter > total_items:
                break

            densities = [_cell_density(binary, y1, y2, cx1, cx2)
                         for cx1, cx2 in col_bounds]

            value, confidence = _classify_row(densities, col_values)

            # Linhas com densidade mínima são cabeçalhos → pula sem incrementar
            if confidence == 'missing' and max(densities) < ROW_MIN_DENSITY * 1.5:
                continue

            resultados[item_counter] = {'value': value, 'confidence': confidence}
            item_counter += 1

    for i in range(1, total_items + 1):
        if i not in resultados:
            resultados[i] = {'value': None, 'confidence': 'missing'}

    return resultados
