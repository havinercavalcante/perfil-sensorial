# HAD — Escala Hospitalar de Ansiedade e Depressão (14 itens)
# Itens ímpares (1,3,5,7,9,11,13): Ansiedade
# Itens pares  (2,4,6,8,10,12,14): Depressão
# Cada item tem 4 alternativas; alguns scores são invertidos (ver opcoes)
# Cortes: 0–7 normal, 8–10 duvidoso, 11–21 confirmado (por subescala)

HAD_ITENS = [
    {
        "numero": 1, "texto": "Eu me sinto tenso(a) ou contraído(a):", "subescala": "ansiedade",
        "opcoes": [
            {"valor": 3, "label": "A maior parte do tempo"},
            {"valor": 2, "label": "Boa parte do tempo"},
            {"valor": 1, "label": "De vez em quando"},
            {"valor": 0, "label": "Nunca"},
        ],
    },
    {
        "numero": 2, "texto": "Eu ainda sinto gosto pelas mesmas coisas de antes:", "subescala": "depressao",
        "opcoes": [
            {"valor": 0, "label": "Sim, do mesmo jeito que antes"},
            {"valor": 1, "label": "Não tanto quanto antes"},
            {"valor": 2, "label": "Só um pouco"},
            {"valor": 3, "label": "Já não sinto mais prazer em nada"},
        ],
    },
    {
        "numero": 3, "texto": "Eu sinto uma espécie de medo, como se alguma coisa ruim fosse acontecer:", "subescala": "ansiedade",
        "opcoes": [
            {"valor": 3, "label": "Sim, e de um jeito muito forte"},
            {"valor": 2, "label": "Sim, mas não tão forte"},
            {"valor": 1, "label": "Um pouco, mas isso não me preocupa"},
            {"valor": 0, "label": "Não sinto nada disso"},
        ],
    },
    {
        "numero": 4, "texto": "Dou risada e me divirto quando vejo coisas engraçadas:", "subescala": "depressao",
        "opcoes": [
            {"valor": 0, "label": "Do mesmo jeito que antes"},
            {"valor": 1, "label": "Atualmente um pouco menos"},
            {"valor": 2, "label": "Atualmente bem menos"},
            {"valor": 3, "label": "Não consigo mais"},
        ],
    },
    {
        "numero": 5, "texto": "Estou com a cabeça cheia de preocupações:", "subescala": "ansiedade",
        "opcoes": [
            {"valor": 3, "label": "A maior parte do tempo"},
            {"valor": 2, "label": "Boa parte do tempo"},
            {"valor": 1, "label": "De vez em quando"},
            {"valor": 0, "label": "Raramente"},
        ],
    },
    {
        "numero": 6, "texto": "Eu me sinto alegre:", "subescala": "depressao",
        "opcoes": [
            {"valor": 3, "label": "Nunca"},
            {"valor": 2, "label": "Poucas vezes"},
            {"valor": 1, "label": "Muitas vezes"},
            {"valor": 0, "label": "A maior parte do tempo"},
        ],
    },
    {
        "numero": 7, "texto": "Consigo ficar sentado(a) à vontade e me sentir relaxado(a):", "subescala": "ansiedade",
        "opcoes": [
            {"valor": 0, "label": "Sim, quase sempre"},
            {"valor": 1, "label": "Muitas vezes"},
            {"valor": 2, "label": "Poucas vezes"},
            {"valor": 3, "label": "Nunca"},
        ],
    },
    {
        "numero": 8, "texto": "Eu estou lento(a) para pensar e fazer as coisas:", "subescala": "depressao",
        "opcoes": [
            {"valor": 3, "label": "Quase sempre"},
            {"valor": 2, "label": "Muitas vezes"},
            {"valor": 1, "label": "De vez em quando"},
            {"valor": 0, "label": "Nunca"},
        ],
    },
    {
        "numero": 9, "texto": "Eu tenho uma sensação ruim de medo, como um frio na barriga ou um aperto no estômago:", "subescala": "ansiedade",
        "opcoes": [
            {"valor": 0, "label": "Nunca"},
            {"valor": 1, "label": "De vez em quando"},
            {"valor": 2, "label": "Muitas vezes"},
            {"valor": 3, "label": "Quase sempre"},
        ],
    },
    {
        "numero": 10, "texto": "Eu perdi o interesse em cuidar da minha aparência:", "subescala": "depressao",
        "opcoes": [
            {"valor": 3, "label": "Completamente"},
            {"valor": 2, "label": "Não estou mais me cuidando como deveria"},
            {"valor": 1, "label": "Talvez não tanto quanto antes"},
            {"valor": 0, "label": "Me cuido do mesmo jeito que antes"},
        ],
    },
    {
        "numero": 11, "texto": "Eu me sinto inquieto(a), como se eu não pudesse ficar parado(a) em lugar nenhum:", "subescala": "ansiedade",
        "opcoes": [
            {"valor": 3, "label": "Sim, demais"},
            {"valor": 2, "label": "Bastante"},
            {"valor": 1, "label": "Um pouco"},
            {"valor": 0, "label": "Não me sinto assim"},
        ],
    },
    {
        "numero": 12, "texto": "Fico esperando animado(a) as coisas boas que estão por vir:", "subescala": "depressao",
        "opcoes": [
            {"valor": 0, "label": "Do mesmo jeito que antes"},
            {"valor": 1, "label": "Um pouco menos do que antes"},
            {"valor": 2, "label": "Bem menos do que antes"},
            {"valor": 3, "label": "Quase nunca"},
        ],
    },
    {
        "numero": 13, "texto": "De repente tenho a sensação de entrar em pânico:", "subescala": "ansiedade",
        "opcoes": [
            {"valor": 3, "label": "A quase todo momento"},
            {"valor": 2, "label": "Várias vezes"},
            {"valor": 1, "label": "De vez em quando"},
            {"valor": 0, "label": "Não sinto isso"},
        ],
    },
    {
        "numero": 14, "texto": "Consigo sentir prazer quando assisto a um bom programa de televisão, de rádio, ou quando leio alguma coisa:", "subescala": "depressao",
        "opcoes": [
            {"valor": 0, "label": "Muitas vezes"},
            {"valor": 1, "label": "Algumas vezes"},
            {"valor": 2, "label": "Poucas vezes"},
            {"valor": 3, "label": "Quase nunca"},
        ],
    },
]

HAD_SUBESCALAS = {
    "ansiedade": {"nome": "Ansiedade",  "itens": [1, 3, 5, 7, 9, 11, 13], "cor": "#C0392B", "campo": "pont_ansiedade"},
    "depressao": {"nome": "Depressão",  "itens": [2, 4, 6, 8, 10, 12, 14], "cor": "#2C3E50", "campo": "pont_depressao"},
}

# HAD usa opcoes por item (variáveis) — opcoes globais não se aplicam
HAD_OPCOES = None

HAD_CORTE = {
    "ansiedade": [
        ("Normal",    0,  7),
        ("Duvidoso",  8, 10),
        ("Confirmado",11, 21),
    ],
    "depressao": [
        ("Normal",    0,  7),
        ("Duvidoso",  8, 10),
        ("Confirmado",11, 21),
    ],
}
