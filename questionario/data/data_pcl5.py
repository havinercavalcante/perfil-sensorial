# PCL-5 — PTSD Checklist for DSM-5
# Baseado em experiência traumática. 4 subescalas do DSM-5.

PCL5_OPCOES = [
    {"valor": 0, "label": "Nada"},
    {"valor": 1, "label": "Um pouco"},
    {"valor": 2, "label": "Moderadamente"},
    {"valor": 3, "label": "Bastante"},
    {"valor": 4, "label": "Extremamente"},
]

PCL5_DOMINIOS = [
    {
        "key":    "reexperiencia",
        "nome":   "Reexperiência (Critério B)",
        "cor":    "#DC2626",
        "campo":  "pont_reexperiencia",
        "itens": [
            (1,  "Memórias angustiantes repetidas, involuntárias e intrusivas do evento traumático"),
            (2,  "Sonhos perturbadores ou pesadelos repetidos relacionados ao evento"),
            (3,  "Agir ou sentir como se o evento traumático estivesse acontecendo de novo (flashbacks)"),
            (4,  "Sentir-se muito perturbado(a) quando alguma coisa lembra o evento traumático"),
            (5,  "Ter fortes reações físicas quando algo lembra o evento (coração acelerado, dificuldade de respirar, suor)"),
        ],
    },
    {
        "key":    "evitacao",
        "nome":   "Evitação (Critério C)",
        "cor":    "#D97706",
        "campo":  "pont_evitacao",
        "itens": [
            (6,  "Evitar memórias, pensamentos ou sentimentos relacionados ao evento traumático"),
            (7,  "Evitar lembretes externos do evento (pessoas, lugares, conversas, atividades, objetos, situações)"),
        ],
    },
    {
        "key":    "cognicoes",
        "nome":   "Cognições e Humor Negativos (Critério D)",
        "cor":    "#7C3AED",
        "campo":  "pont_cognicoes",
        "itens": [
            (8,  "Dificuldade para lembrar partes importantes do evento traumático"),
            (9,  "Crenças ou expectativas negativas fortes sobre si mesmo(a), outras pessoas ou o mundo"),
            (10, "Culpar-se ou culpar outras pessoas pelo evento traumático ou pelo que aconteceu depois"),
            (11, "Sentir emoções negativas intensas como medo, horror, raiva, culpa ou vergonha"),
            (12, "Perda de interesse em atividades que antes eram significativas"),
            (13, "Sentir-se distante ou afastado(a) das outras pessoas"),
            (14, "Dificuldade para sentir emoções positivas (felicidade, amor, alegria)"),
        ],
    },
    {
        "key":    "hiperativacao",
        "nome":   "Hiperativação e Reatividade (Critério E)",
        "cor":    "#059669",
        "campo":  "pont_hiperativacao",
        "itens": [
            (15, "Comportamento irritável, explosões de raiva ou agressividade"),
            (16, "Assumir riscos ou comportamentos autodestrutivos"),
            (17, "Estar em estado de alerta — sentir que algo ruim pode acontecer a qualquer momento"),
            (18, "Ficar facilmente assustado(a) ou sobressaltado(a)"),
            (19, "Dificuldade para se concentrar"),
            (20, "Dificuldade para adormecer ou permanecer dormindo"),
        ],
    },
]

PCL5_CORTE = [
    ("Sem indicativo de TEPT",  0,  30),
    ("Indicativo provável",    31,  80),
]
