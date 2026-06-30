"""
Leitura de formulários escaneados usando o Gemini (Google) como OCR semântico.

Substitui a abordagem antiga (densidade de pixels por coluna) por uma chamada
de visão computacional: enviamos as páginas do formulário como imagens e
pedimos para o modelo identificar o instrumento e extrair, item a item, qual
opção foi circulada/marcada — devolvendo um JSON estruturado.

Vantagem sobre o approach de pixels: não depende de calibrar manualmente a
posição exata de cada coluna de resposta por formulário/edição.
"""

import json
import logging

from django.conf import settings

from .formularios_meta import INSTRUMENTOS, RESPONSE_SCHEMA, montar_prompt

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"


def _client():
    from google import genai

    api_key = getattr(settings, "GOOGLE_API_KEY", "") or ""
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY não configurada. Adicione GOOGLE_API_KEY=... no .env."
        )
    return genai.Client(api_key=api_key)


def ler_formulario(paginas_bytes: list, forcar_tipo: str = None) -> dict:
    """
    Envia as páginas (lista de bytes JPEG/PNG) ao Gemini e retorna o resultado
    estruturado da leitura.

    Returns:
        {
          'tipo': str,            # código do instrumento (ou 'desconhecido')
          'label': str,
          'confianca': 'alta'|'baixa',
          'nome_detectado': str,
          'nasc_detectado': str,
          'resp_detectado': str,
          'respostas': {int: {'value': str, 'confidence': 'alta'|'baixa'}},
        }
    """
    from google.genai import types

    client = _client()
    prompt = montar_prompt(forcar_tipo)

    parts = [types.Part.from_text(text=prompt)]
    for pg in paginas_bytes:
        parts.append(types.Part.from_bytes(data=pg, mime_type="image/jpeg"))

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[types.Content(role="user", parts=parts)],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
            temperature=0.0,
        ),
    )

    data = json.loads(response.text)

    tipo = data.get("instrumento") or forcar_tipo or "desconhecido"
    info = INSTRUMENTOS.get(tipo)
    label = info["label"] if info else "Desconhecido"

    # Per-item confidence usa 'high'/'low'/'missing' — mesma convenção dos
    # leitores antigos (spm_reader/ps2_reader), consumida pelos templates de revisão.
    conf_map = {"alta": "high", "baixa": "low"}

    respostas = {}
    n_baixa = 0
    n_total = 0
    for entrada in data.get("respostas", []):
        try:
            num = int(entrada.get("item"))
        except (TypeError, ValueError):
            continue
        valor = (entrada.get("valor") or "").strip().upper()
        conf_raw = entrada.get("confianca") or "baixa"
        conf = conf_map.get(conf_raw, "low")
        if not valor:
            conf = "missing"
        respostas[num] = {"value": valor or None, "confidence": conf}
        n_total += 1
        if conf != "high":
            n_baixa += 1

    confianca_geral = "alta" if n_total > 0 and (n_baixa / n_total) < 0.15 else "baixa"

    return {
        "tipo": tipo,
        "label": label,
        "confianca": confianca_geral,
        "nome_detectado": (data.get("nome_crianca") or "").strip(),
        "nasc_detectado": (data.get("data_nascimento") or "").strip(),
        "resp_detectado": (data.get("nome_responsavel") or "").strip(),
        "respostas": respostas,
    }
