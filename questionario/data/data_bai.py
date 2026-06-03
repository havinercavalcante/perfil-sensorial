# BAI — Inventário de Ansiedade de Beck (21 itens, escala 0–3)
# Pontos de corte: 0–7 mínimo, 8–15 leve, 16–25 moderado, 26–63 grave

BAI_ITENS = [
    {"numero":  1, "texto": "Dormência ou formigamento"},
    {"numero":  2, "texto": "Sensação de calor"},
    {"numero":  3, "texto": "Tremores nas pernas"},
    {"numero":  4, "texto": "Incapaz de relaxar"},
    {"numero":  5, "texto": "Medo que aconteça o pior"},
    {"numero":  6, "texto": "Tonteira ou vertigem"},
    {"numero":  7, "texto": "Palpitações ou aceleração do coração"},
    {"numero":  8, "texto": "Sem equilíbrio"},
    {"numero":  9, "texto": "Aterrorizado(a)"},
    {"numero": 10, "texto": "Nervosismo"},
    {"numero": 11, "texto": "Sensação de sufocamento"},
    {"numero": 12, "texto": "Tremores nas mãos"},
    {"numero": 13, "texto": "Trêmulo(a)"},
    {"numero": 14, "texto": "Medo de perder o controle"},
    {"numero": 15, "texto": "Dificuldade em respirar"},
    {"numero": 16, "texto": "Medo de morrer"},
    {"numero": 17, "texto": "Assustado(a)"},
    {"numero": 18, "texto": "Indigestão ou desconforto abdominal"},
    {"numero": 19, "texto": "Sensação de desmaio"},
    {"numero": 20, "texto": "Rosto avermelhado"},
    {"numero": 21, "texto": "Suores (não devidos ao calor)"},
]

for item in BAI_ITENS:
    item["subescala"] = "total"
    item["reverso"] = False

BAI_SUBESCALAS = {
    "total": {"nome": "Pontuação Total", "itens": list(range(1, 22)), "cor": "#C0392B", "campo": "pont_total"},
}

BAI_OPCOES = [
    {"valor": 0, "label": "Absolutamente não"},
    {"valor": 1, "label": "Levemente — não me incomodou muito"},
    {"valor": 2, "label": "Moderadamente — foi muito desagradável mas pude suportar"},
    {"valor": 3, "label": "Gravemente — quase não pude suportar"},
]

BAI_CORTE = {
    "total": [
        ("Mínimo",    0,  7),
        ("Leve",      8, 15),
        ("Moderado", 16, 25),
        ("Grave",    26, 63),
    ],
}
