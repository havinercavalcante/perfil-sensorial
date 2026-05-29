# AUQEI — Autoquestionnaire Qualité de Vie Enfant Imagé
# 26 itens, escala 1–4 (muito infeliz / infeliz / feliz / muito feliz)
# 6 subescalas + itens independentes
# Respondido pela criança (6–12 anos) — versão digital com texto

AUQEI_ITENS = [
    {"numero":  1, "texto": "Como você se sente quando está com sua família?",                                "subescala": "familia"},
    {"numero":  2, "texto": "Como você se sente quando come?",                                                "subescala": "funcoes"},
    {"numero":  3, "texto": "Como você se sente quando está dormindo?",                                       "subescala": "funcoes"},
    {"numero":  4, "texto": "Como você se sente quando está com seus amigos?",                                "subescala": "amigos"},
    {"numero":  5, "texto": "Como você se sente quando está na escola?",                                      "subescala": "escola"},
    {"numero":  6, "texto": "Como você se sente quando você é elogiado(a)?",                                  "subescala": "independente"},
    {"numero":  7, "texto": "Como você se sente quando você está com sua mãe?",                               "subescala": "familia"},
    {"numero":  8, "texto": "Como você se sente quando você está com seu pai?",                               "subescala": "familia"},
    {"numero":  9, "texto": "Como você se sente quando você aprende coisas novas?",                           "subescala": "escola"},
    {"numero": 10, "texto": "Como você se sente quando você se machuca?",                                     "subescala": "funcoes"},
    {"numero": 11, "texto": "Como você se sente quando você brinca sozinho(a)?",                              "subescala": "lazer"},
    {"numero": 12, "texto": "Como você se sente quando você brinca com outros(as)?",                          "subescala": "amigos"},
    {"numero": 13, "texto": "Como você se sente quando você está doente?",                                    "subescala": "funcoes"},
    {"numero": 14, "texto": "Como você se sente quando você vai ao médico ou ao hospital?",                   "subescala": "independente"},
    {"numero": 15, "texto": "Como você se sente quando você precisa ir ao banheiro?",                         "subescala": "funcoes"},
    {"numero": 16, "texto": "Como você se sente quando você fica com seus irmãos(ãs)?",                      "subescala": "familia"},
    {"numero": 17, "texto": "Como você se sente quando você faz uma atividade esportiva?",                    "subescala": "lazer"},
    {"numero": 18, "texto": "Como você se sente quando você usa roupas novas?",                               "subescala": "independente"},
    {"numero": 19, "texto": "Como você se sente quando você tem brinquedos novos?",                           "subescala": "lazer"},
    {"numero": 20, "texto": "Como você se sente quando você está na aula?",                                   "subescala": "escola"},
    {"numero": 21, "texto": "Como você se sente quando você fica longe dos seus pais?",                       "subescala": "autonomia"},
    {"numero": 22, "texto": "Como você se sente quando você assiste televisão?",                              "subescala": "lazer"},
    {"numero": 23, "texto": "Como você se sente quando você não consegue fazer algo sozinho(a)?",             "subescala": "autonomia"},
    {"numero": 24, "texto": "Como você se sente quando você cuida do seu próprio corpo (higiene)?",           "subescala": "autonomia"},
    {"numero": 25, "texto": "Como você se sente quando você está com seus professores?",                      "subescala": "escola"},
    {"numero": 26, "texto": "Como você se sente quando você está de férias?",                                 "subescala": "lazer"},
]

for item in AUQEI_ITENS:
    item["reverso"] = False

AUQEI_SUBESCALAS = {
    "familia":      {"nome": "Família",              "itens": [1, 7, 8, 16],       "cor": "#E74C3C", "campo": "pont_familia"},
    "lazer":        {"nome": "Lazer",                "itens": [11, 17, 19, 22, 26],"cor": "#27AE60", "campo": "pont_lazer"},
    "escola":       {"nome": "Escola",               "itens": [5, 9, 20, 25],      "cor": "#3498DB", "campo": "pont_escola"},
    "autonomia":    {"nome": "Autonomia",             "itens": [21, 23, 24],        "cor": "#9B59B6", "campo": "pont_autonomia"},
    "funcoes":      {"nome": "Funções Corporais",    "itens": [2, 3, 10, 13, 15],  "cor": "#E67E22", "campo": "pont_funcoes"},
    "amigos":       {"nome": "Amigos",               "itens": [4, 12],             "cor": "#F1C40F", "campo": "pont_amigos"},
    "independente": {"nome": "Itens Independentes",  "itens": [6, 14, 18],         "cor": "#1ABC9C", "campo": "pont_independente"},
}

AUQEI_OPCOES = [
    {"valor": 1, "label": "Muito infeliz"},
    {"valor": 2, "label": "Infeliz"},
    {"valor": 3, "label": "Feliz"},
    {"valor": 4, "label": "Muito feliz"},
]

# Corte total: < 48 = comprometimento de qualidade de vida
AUQEI_CORTE = {
    "total": [
        ("Comprometido",    26,  47),
        ("Satisfatório",    48, 104),
    ],
}
