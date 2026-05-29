# DASS-21 — Depression Anxiety Stress Scales (21 itens, escala 0–3)
# 3 subescalas: depressão (7 itens), ansiedade (7 itens), estresse (7 itens)
# Score final = soma × 2 (para equiparar com DASS-42 original)

# Distribuição dos itens (numeração na versão 21 itens):
# Depressão: 3, 5, 10, 13, 16, 17, 21
# Ansiedade:  2, 4,  7,  9, 15, 19, 20
# Estresse:   1, 6,  8, 11, 12, 14, 18

DASS21_ITENS = [
    {"numero":  1, "texto": "Tive dificuldade em me acalmar",                                                    "subescala": "estresse"},
    {"numero":  2, "texto": "Percebi que tinha a boca seca",                                                     "subescala": "ansiedade"},
    {"numero":  3, "texto": "Não consegui experimentar nenhum sentimento positivo",                              "subescala": "depressao"},
    {"numero":  4, "texto": "Tive dificuldade em respirar (ex.: respiração ofegante, sem conseguir respirar)",   "subescala": "ansiedade"},
    {"numero":  5, "texto": "Tive dificuldade em tomar iniciativa para fazer coisas",                            "subescala": "depressao"},
    {"numero":  6, "texto": "Tive tendência a reagir de forma exagerada às situações",                           "subescala": "estresse"},
    {"numero":  7, "texto": "Senti tremores (ex.: nas mãos)",                                                    "subescala": "ansiedade"},
    {"numero":  8, "texto": "Senti que estava utilizando muita energia nervosa",                                  "subescala": "estresse"},
    {"numero":  9, "texto": "Preocupei-me com situações em que pudesse entrar em pânico e fazer papel ridículo", "subescala": "ansiedade"},
    {"numero": 10, "texto": "Senti que não tinha nada a esperar do futuro",                                      "subescala": "depressao"},
    {"numero": 11, "texto": "Senti que estava agitado(a)",                                                       "subescala": "estresse"},
    {"numero": 12, "texto": "Tive dificuldade em me relaxar",                                                    "subescala": "estresse"},
    {"numero": 13, "texto": "Senti-me desanimado(a) e melancólico(a)",                                          "subescala": "depressao"},
    {"numero": 14, "texto": "Fui intolerante com as coisas que me impediam de continuar o que estava fazendo",   "subescala": "estresse"},
    {"numero": 15, "texto": "Senti que estava quase em pânico",                                                  "subescala": "ansiedade"},
    {"numero": 16, "texto": "Não fui capaz de me entusiasmar com nada",                                          "subescala": "depressao"},
    {"numero": 17, "texto": "Senti que não tinha muito valor como pessoa",                                       "subescala": "depressao"},
    {"numero": 18, "texto": "Senti que por vezes estava sensível",                                               "subescala": "estresse"},
    {"numero": 19, "texto": "Percebi alterações no meu coração sem fazer exercício físico",                      "subescala": "ansiedade"},
    {"numero": 20, "texto": "Senti-me assustado(a) sem ter tido uma boa razão para isso",                        "subescala": "ansiedade"},
    {"numero": 21, "texto": "Senti que a vida não tinha sentido",                                                "subescala": "depressao"},
]

for item in DASS21_ITENS:
    item["reverso"] = False

DASS21_SUBESCALAS = {
    "depressao": {"nome": "Depressão",  "itens": [3, 5, 10, 13, 16, 17, 21], "cor": "#2C3E50", "campo": "pont_depressao"},
    "ansiedade": {"nome": "Ansiedade",  "itens": [2, 4,  7,  9, 15, 19, 20], "cor": "#C0392B", "campo": "pont_ansiedade"},
    "estresse":  {"nome": "Estresse",   "itens": [1, 6,  8, 11, 12, 14, 18], "cor": "#E67E22", "campo": "pont_estresse"},
}

DASS21_OPCOES = [
    {"valor": 0, "label": "Não se aplicou de nenhuma forma"},
    {"valor": 1, "label": "Aplicou-se um pouco, ou durante parte do tempo"},
    {"valor": 2, "label": "Aplicou-se consideravelmente, ou durante boa parte do tempo"},
    {"valor": 3, "label": "Aplicou-se muito, ou na maior parte do tempo"},
]

# Cortes usando score × 2
DASS21_CORTE = {
    "depressao": [
        ("Normal",   0,  9),
        ("Leve",    10, 13),
        ("Moderado",14, 20),
        ("Grave",   21, 27),
        ("Extremo", 28, 42),
    ],
    "ansiedade": [
        ("Normal",   0,  7),
        ("Leve",     8,  9),
        ("Moderado", 10, 14),
        ("Grave",    15, 19),
        ("Extremo",  20, 42),
    ],
    "estresse": [
        ("Normal",   0, 14),
        ("Leve",    15, 18),
        ("Moderado",19, 25),
        ("Grave",   26, 33),
        ("Extremo", 34, 42),
    ],
}
