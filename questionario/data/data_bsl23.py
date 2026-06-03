# BSL-23 — Borderline Symptom List (23 itens, escala 0–4)
# Ponto de corte: média ≥ 2,0 = sintomático

BSL23_ITENS = [
    {"numero":  1, "texto": "Senti-me sozinho(a) e abandonado(a)"},
    {"numero":  2, "texto": "Senti-me sem valor"},
    {"numero":  3, "texto": "Senti-me com vergonha de mim mesmo(a)"},
    {"numero":  4, "texto": "Senti raiva de mim mesmo(a)"},
    {"numero":  5, "texto": "Senti-me perdido(a) ou sem rumo"},
    {"numero":  6, "texto": "Não consegui sentir nada — fiquei vazio(a) e entorpecido(a) por dentro"},
    {"numero":  7, "texto": "Senti-me sem esperança"},
    {"numero":  8, "texto": "Senti-me tão tenso(a) que mal podia ficar parado(a)"},
    {"numero":  9, "texto": "Senti-me manipulado(a) por pessoas das quais dependia"},
    {"numero": 10, "texto": "Tive medo de ser abandonado(a)"},
    {"numero": 11, "texto": "Tive pensamentos de me machucar"},
    {"numero": 12, "texto": "Não consegui parar de chorar"},
    {"numero": 13, "texto": "Tive medo de perder o controle"},
    {"numero": 14, "texto": "Tive sentimentos que me encheram de vergonha"},
    {"numero": 15, "texto": "Tive sentimentos que me encheram de culpa"},
    {"numero": 16, "texto": "Tive pensamentos ruins que não conseguia afastar"},
    {"numero": 17, "texto": "Senti que ficaria louco(a)"},
    {"numero": 18, "texto": "Senti que estava com raiva demais"},
    {"numero": 19, "texto": "Me prejudiquei de propósito (ex.: me machuquei, me cortei)"},
    {"numero": 20, "texto": "Senti que precisava se machucar para sentir alguma coisa"},
    {"numero": 21, "texto": "Senti que meu corpo não era meu / me senti desconectado(a) dele"},
    {"numero": 22, "texto": "Desejei estar morto(a)"},
    {"numero": 23, "texto": "Senti que as pessoas ao meu redor me fariam mal"},
]

for item in BSL23_ITENS:
    item["subescala"] = "total"
    item["reverso"] = False

BSL23_SUBESCALAS = {
    "total": {"nome": "Média Total", "itens": list(range(1, 24)), "cor": "#8E44AD", "campo": "media_total"},
}

BSL23_OPCOES = [
    {"valor": 0, "label": "Nunca"},
    {"valor": 1, "label": "Raramente"},
    {"valor": 2, "label": "Às vezes"},
    {"valor": 3, "label": "Frequentemente"},
    {"valor": 4, "label": "Sempre"},
]

BSL23_CORTE = {
    "total": [
        ("Assintomático", 0.0, 1.99),
        ("Sintomático",   2.0, 4.0),
    ],
}
