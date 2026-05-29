# SCARED — Screen for Child Anxiety Related Emotional Disorders (Birmaher, 1997)
# 41 itens, escala 0–2 (nunca/às vezes/sempre)
# 5 subescalas; respondido por pais
# Corte total ≥ 25; subescalas têm cortes próprios

SCARED_ITENS = [
    {"numero":  1, "texto": "Quando meu(minha) filho(a) se sente assustado(a), fica difícil respirar",                "subescala": "panico"},
    {"numero":  2, "texto": "Meu(minha) filho(a) tem dores de cabeça quando está na escola",                          "subescala": "escola"},
    {"numero":  3, "texto": "Meu(minha) filho(a) não gosta de estar com pessoas que não conhece bem",                 "subescala": "separacao"},
    {"numero":  4, "texto": "Meu(minha) filho(a) tem medo de dormir fora de casa",                                    "subescala": "separacao"},
    {"numero":  5, "texto": "Meu(minha) filho(a) se preocupa com outras pessoas",                                     "subescala": "generalizada"},
    {"numero":  6, "texto": "Quando meu(minha) filho(a) se sente assustado(a), começa a tremer",                      "subescala": "panico"},
    {"numero":  7, "texto": "Meu(minha) filho(a) é nervoso(a), inquieto(a) ou tenso(a)",                             "subescala": "generalizada"},
    {"numero":  8, "texto": "Meu(minha) filho(a) segue minha sombra em casa",                                        "subescala": "separacao"},
    {"numero":  9, "texto": "Meu(minha) filho(a) tem medo de ter ataques de pânico",                                  "subescala": "panico"},
    {"numero": 10, "texto": "Meu(minha) filho(a) fica assustado(a) com pessoas que não conhece bem",                  "subescala": "fobia_social"},
    {"numero": 11, "texto": "Meu(minha) filho(a) tem dores de barriga quando vai à escola",                           "subescala": "escola"},
    {"numero": 12, "texto": "Quando meu(minha) filho(a) se sente assustado(a), sente que vai enlouquecer",            "subescala": "panico"},
    {"numero": 13, "texto": "Meu(minha) filho(a) se preocupa em dormir sozinho(a)",                                   "subescala": "separacao"},
    {"numero": 14, "texto": "Meu(minha) filho(a) se preocupa em ser tão bom(boa) quanto outras crianças",             "subescala": "generalizada"},
    {"numero": 15, "texto": "Quando meu(minha) filho(a) se sente assustado(a), sente que as coisas não são reais",    "subescala": "panico"},
    {"numero": 16, "texto": "Meu(minha) filho(a) tem pesadelos sobre algo ruim acontecer com seus pais",              "subescala": "separacao"},
    {"numero": 17, "texto": "Meu(minha) filho(a) se preocupa em ir à escola",                                        "subescala": "fobia_social"},
    {"numero": 18, "texto": "Quando meu(minha) filho(a) se sente assustado(a), seu coração bate muito forte",        "subescala": "panico"},
    {"numero": 19, "texto": "Meu(minha) filho(a) fica muito tremulo(a)",                                             "subescala": "panico"},
    {"numero": 20, "texto": "Meu(minha) filho(a) tem pesadelos sobre algo ruim acontecer com ele(ela)",              "subescala": "fobia_social"},
    {"numero": 21, "texto": "Meu(minha) filho(a) se preocupa que as coisas deem errado",                             "subescala": "generalizada"},
    {"numero": 22, "texto": "Quando meu(minha) filho(a) se sente assustado(a), sente calor",                         "subescala": "panico"},
    {"numero": 23, "texto": "Meu(minha) filho(a) se preocupa se fez algo errado",                                    "subescala": "generalizada"},
    {"numero": 24, "texto": "Meu(minha) filho(a) tem medo de ir ao dentista ou ao médico",                           "subescala": "panico"},
    {"numero": 25, "texto": "Meu(minha) filho(a) evita sair de casa sem mim",                                        "subescala": "separacao"},
    {"numero": 26, "texto": "Meu(minha) filho(a) fica nervoso(a) na escola",                                         "subescala": "escola"},
    {"numero": 27, "texto": "Quando meu(minha) filho(a) se sente assustado(a), pode sentir que vai sufocar",         "subescala": "panico"},
    {"numero": 28, "texto": "Meu(minha) filho(a) se preocupa muito com o futuro",                                    "subescala": "generalizada"},
    {"numero": 29, "texto": "Meu(minha) filho(a) se sente assustado(a) quando está longe de casa",                   "subescala": "separacao"},
    {"numero": 30, "texto": "Meu(minha) filho(a) tem medo de ter ansiedade ou de passar mal em público",             "subescala": "panico"},
    {"numero": 31, "texto": "Meu(minha) filho(a) se preocupa que algo ruim vai lhe acontecer",                       "subescala": "generalizada"},
    {"numero": 32, "texto": "Meu(minha) filho(a) fica envergonhado(a) quando é observado(a)",                        "subescala": "fobia_social"},
    {"numero": 33, "texto": "Meu(minha) filho(a) se preocupa com o que vai acontecer no futuro",                     "subescala": "generalizada"},
    {"numero": 34, "texto": "Quando meu(minha) filho(a) se sente assustado(a), sente vontade de vomitar",            "subescala": "panico"},
    {"numero": 35, "texto": "Meu(minha) filho(a) se preocupa muito com o desempenho escolar",                        "subescala": "generalizada"},
    {"numero": 36, "texto": "Meu(minha) filho(a) tem medo de sair de casa sozinho(a)",                               "subescala": "separacao"},
    {"numero": 37, "texto": "Meu(minha) filho(a) se preocupa muito em fazer as coisas bem feitas",                   "subescala": "generalizada"},
    {"numero": 38, "texto": "Quando meu(minha) filho(a) se sente assustado(a), sente tontura",                       "subescala": "panico"},
    {"numero": 39, "texto": "Meu(minha) filho(a) sente ansiedade quando está com crianças/pessoas diferentes",       "subescala": "fobia_social"},
    {"numero": 40, "texto": "Meu(minha) filho(a) fica nervoso(a) quando vai a festas ou saídas sociais",             "subescala": "fobia_social"},
    {"numero": 41, "texto": "Meu(minha) filho(a) tem medo de ir à escola",                                          "subescala": "escola"},
]

for item in SCARED_ITENS:
    item["reverso"] = False

SCARED_SUBESCALAS = {
    "panico":       {"nome": "Pânico / Somático",        "itens": [1, 6, 9, 12, 15, 18, 19, 22, 24, 27, 30, 34, 38], "cor": "#C0392B", "campo": "pont_panico"},
    "generalizada": {"nome": "Ansiedade Generalizada",   "itens": [5, 7, 14, 21, 23, 28, 31, 33, 35, 37],            "cor": "#E67E22", "campo": "pont_generalizada"},
    "fobia_social": {"nome": "Fobia Social",             "itens": [10, 17, 20, 25, 32, 39, 40],                      "cor": "#9B59B6", "campo": "pont_fobia_social"},
    "separacao":    {"nome": "Ansiedade de Separação",   "itens": [3, 4, 8, 13, 16, 29, 36],                        "cor": "#3498DB", "campo": "pont_separacao"},
    "escola":       {"nome": "Ansiedade Escolar",        "itens": [2, 11, 26, 41],                                   "cor": "#27AE60", "campo": "pont_escola"},
}

SCARED_OPCOES = [
    {"valor": 0, "label": "Nunca / Quase nunca"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Frequentemente / Sempre"},
]

SCARED_CORTE = {
    "panico":       [("Sem indicação", 0, 6),  ("Positivo", 7, 26)],
    "generalizada": [("Sem indicação", 0, 8),  ("Positivo", 9, 20)],
    "fobia_social": [("Sem indicação", 0, 8),  ("Positivo", 9, 14)],
    "separacao":    [("Sem indicação", 0, 4),  ("Positivo", 5, 14)],
    "escola":       [("Sem indicação", 0, 2),  ("Positivo", 3, 8)],
    "total":        [("Sem indicação", 0, 24), ("Positivo", 25, 82)],
}
