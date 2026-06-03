# GHQ-12 — General Health Questionnaire (versão 12 itens)
# Pontuação Likert 0-1-2-3. Itens 1,2,4,7,8,12 positivos (invertidos).
# Pontuação binária alternativa: 0,0,1,1 por item (corte ≥3).

GHQ12_ITENS = [
    {
        "numero": 1,
        "texto": "Tem conseguido se concentrar bem no que está fazendo?",
        "invertido": True,
        "opcoes": [
            {"valor": 0, "label": "Melhor do que de costume"},
            {"valor": 0, "label": "Igual ao de costume"},
            {"valor": 1, "label": "Menos do que de costume"},
            {"valor": 1, "label": "Muito menos do que de costume"},
        ],
    },
    {
        "numero": 2,
        "texto": "Tem perdido muito sono por causa de preocupações?",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Não, absolutamente"},
            {"valor": 0, "label": "Não mais do que de costume"},
            {"valor": 1, "label": "Mais do que de costume"},
            {"valor": 1, "label": "Muito mais do que de costume"},
        ],
    },
    {
        "numero": 3,
        "texto": "Tem sentido que está desempenhando um papel útil nas coisas?",
        "invertido": True,
        "opcoes": [
            {"valor": 0, "label": "Mais do que de costume"},
            {"valor": 0, "label": "Igual ao de costume"},
            {"valor": 1, "label": "Menos útil do que de costume"},
            {"valor": 1, "label": "Muito menos útil do que de costume"},
        ],
    },
    {
        "numero": 4,
        "texto": "Tem se sentido capaz de tomar decisões?",
        "invertido": True,
        "opcoes": [
            {"valor": 0, "label": "Mais do que de costume"},
            {"valor": 0, "label": "Igual ao de costume"},
            {"valor": 1, "label": "Menos do que de costume"},
            {"valor": 1, "label": "Muito menos do que de costume"},
        ],
    },
    {
        "numero": 5,
        "texto": "Tem se sentido constantemente sobrecarregado(a) e sob pressão?",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Não, absolutamente"},
            {"valor": 0, "label": "Não mais do que de costume"},
            {"valor": 1, "label": "Mais do que de costume"},
            {"valor": 1, "label": "Muito mais do que de costume"},
        ],
    },
    {
        "numero": 6,
        "texto": "Tem sentido que não consegue superar suas dificuldades?",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Não, absolutamente"},
            {"valor": 0, "label": "Não mais do que de costume"},
            {"valor": 1, "label": "Mais do que de costume"},
            {"valor": 1, "label": "Muito mais do que de costume"},
        ],
    },
    {
        "numero": 7,
        "texto": "Tem conseguido aproveitar suas atividades normais do dia a dia?",
        "invertido": True,
        "opcoes": [
            {"valor": 0, "label": "Mais do que de costume"},
            {"valor": 0, "label": "Igual ao de costume"},
            {"valor": 1, "label": "Menos do que de costume"},
            {"valor": 1, "label": "Muito menos do que de costume"},
        ],
    },
    {
        "numero": 8,
        "texto": "Tem conseguido enfrentar seus problemas?",
        "invertido": True,
        "opcoes": [
            {"valor": 0, "label": "Melhor do que de costume"},
            {"valor": 0, "label": "Igual ao de costume"},
            {"valor": 1, "label": "Menos do que de costume"},
            {"valor": 1, "label": "Muito menos do que de costume"},
        ],
    },
    {
        "numero": 9,
        "texto": "Tem se sentido muito infeliz e deprimido(a)?",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Não, absolutamente"},
            {"valor": 0, "label": "Não mais do que de costume"},
            {"valor": 1, "label": "Mais do que de costume"},
            {"valor": 1, "label": "Muito mais do que de costume"},
        ],
    },
    {
        "numero": 10,
        "texto": "Tem perdido a confiança em si mesmo(a)?",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Não, absolutamente"},
            {"valor": 0, "label": "Não mais do que de costume"},
            {"valor": 1, "label": "Mais do que de costume"},
            {"valor": 1, "label": "Muito mais do que de costume"},
        ],
    },
    {
        "numero": 11,
        "texto": "Tem pensado em si mesmo(a) como uma pessoa sem valor?",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Não, absolutamente"},
            {"valor": 0, "label": "Não mais do que de costume"},
            {"valor": 1, "label": "Mais do que de costume"},
            {"valor": 1, "label": "Muito mais do que de costume"},
        ],
    },
    {
        "numero": 12,
        "texto": "Tem se sentido razoavelmente feliz, considerando tudo?",
        "invertido": True,
        "opcoes": [
            {"valor": 0, "label": "Mais feliz do que de costume"},
            {"valor": 0, "label": "Igual ao de costume"},
            {"valor": 1, "label": "Menos feliz do que de costume"},
            {"valor": 1, "label": "Muito menos feliz do que de costume"},
        ],
    },
]

GHQ12_CORTE = [
    ("Sem indicativo de distress",  0,  2),
    ("Distress psicológico",        3, 12),
]
