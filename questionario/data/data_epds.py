# EPDS — Edinburgh Postnatal Depression Scale
# Itens 1 e 2: pontuação INVERTIDA (melhor resposta = 0)
# Itens 3–10: pontuação DIRETA

EPDS_ITENS = [
    {
        "numero": 1,
        "texto": "Tenho sido capaz de rir e ver o lado positivo das coisas",
        "invertido": True,
        "opcoes": [
            {"valor": 0, "label": "Tanto quanto antes"},
            {"valor": 1, "label": "Não tanto quanto antes"},
            {"valor": 2, "label": "Muito menos do que antes"},
            {"valor": 3, "label": "Não, de jeito nenhum"},
        ],
    },
    {
        "numero": 2,
        "texto": "Tenho sentido prazer quando penso no que está por vir",
        "invertido": True,
        "opcoes": [
            {"valor": 0, "label": "Tanto quanto antes"},
            {"valor": 1, "label": "Menos do que antes"},
            {"valor": 2, "label": "Muito menos do que antes"},
            {"valor": 3, "label": "Quase nada"},
        ],
    },
    {
        "numero": 3,
        "texto": "Tenho me culpado sem necessidade quando as coisas correm mal",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Não, nunca"},
            {"valor": 1, "label": "Não muito frequentemente"},
            {"valor": 2, "label": "Sim, às vezes"},
            {"valor": 3, "label": "Sim, na maioria das vezes"},
        ],
    },
    {
        "numero": 4,
        "texto": "Tenho ficado ansiosa ou preocupada sem um motivo especial",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Não, nunca"},
            {"valor": 1, "label": "Quase nunca"},
            {"valor": 2, "label": "Sim, às vezes"},
            {"valor": 3, "label": "Sim, com muita frequência"},
        ],
    },
    {
        "numero": 5,
        "texto": "Tenho sentido medo ou ficado apavorada sem um bom motivo",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Não, nunca"},
            {"valor": 1, "label": "Não muito"},
            {"valor": 2, "label": "Sim, às vezes"},
            {"valor": 3, "label": "Sim, bastante"},
        ],
    },
    {
        "numero": 6,
        "texto": "As coisas têm me sobrecarregado",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Não, tenho me saído tão bem quanto antes"},
            {"valor": 1, "label": "Não, na maioria das vezes tenho me saído bem"},
            {"valor": 2, "label": "Sim, às vezes não tenho conseguido me sair bem"},
            {"valor": 3, "label": "Sim, na maior parte do tempo não tenho conseguido"},
        ],
    },
    {
        "numero": 7,
        "texto": "Tenho me sentido tão infeliz que tenho tido dificuldade para dormir",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Não, nunca"},
            {"valor": 1, "label": "Não muito frequentemente"},
            {"valor": 2, "label": "Sim, às vezes"},
            {"valor": 3, "label": "Sim, na maioria das vezes"},
        ],
    },
    {
        "numero": 8,
        "texto": "Tenho me sentido triste ou muito mal",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Não, nunca"},
            {"valor": 1, "label": "Não muito frequentemente"},
            {"valor": 2, "label": "Sim, às vezes"},
            {"valor": 3, "label": "Sim, na maioria das vezes"},
        ],
    },
    {
        "numero": 9,
        "texto": "Tenho ficado tão infeliz que choro",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Não, nunca"},
            {"valor": 1, "label": "Só às vezes"},
            {"valor": 2, "label": "Sim, bastante frequentemente"},
            {"valor": 3, "label": "Sim, na maioria das vezes"},
        ],
    },
    {
        "numero": 10,
        "texto": "Tenho tido pensamentos de me machucar",
        "invertido": False,
        "opcoes": [
            {"valor": 0, "label": "Nunca"},
            {"valor": 1, "label": "Raramente"},
            {"valor": 2, "label": "Às vezes"},
            {"valor": 3, "label": "Sim, com bastante frequência"},
        ],
    },
]

EPDS_CORTE = [
    ("Sem indicativo",           0,  9),
    ("Leve / Atenção",          10, 12),
    ("Indicativo de DPP",       13, 30),
]
