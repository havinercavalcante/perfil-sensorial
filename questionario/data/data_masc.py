# MASC — Multidimensional Anxiety Scale for Children (March et al., 1997)
# 39 itens, escala 0–3 (nunca/raramente/às vezes/frequentemente)
# 4 subescalas principais
# Respondido por pais/cuidadores (versão parental)

MASC_ITENS = [
    # Subescala: Sintomas Físicos
    {"numero":  1, "texto": "Meu(minha) filho(a) sente dores de barriga",                                             "subescala": "sint_fisicos"},
    {"numero":  2, "texto": "Meu(minha) filho(a) se assusta ou entra em pânico com pequenas coisas",                  "subescala": "sint_fisicos"},
    {"numero":  3, "texto": "Meu(minha) filho(a) sente sua cabeça girar ou tombar",                                   "subescala": "sint_fisicos"},
    {"numero":  4, "texto": "Meu(minha) filho(a) sente que o coração bate forte sem motivo",                          "subescala": "sint_fisicos"},
    {"numero":  5, "texto": "Meu(minha) filho(a) fica sem ar de repente",                                            "subescala": "sint_fisicos"},
    {"numero":  6, "texto": "Meu(minha) filho(a) sente seus membros trêmulos ou fracos",                             "subescala": "sint_fisicos"},
    # Subescala: Ansiedade Social
    {"numero":  7, "texto": "Meu(minha) filho(a) tem medo de ser criticado(a) perante os outros",                    "subescala": "anx_social"},
    {"numero":  8, "texto": "Meu(minha) filho(a) evita falar com pessoas que não conhece bem",                       "subescala": "anx_social"},
    {"numero":  9, "texto": "Meu(minha) filho(a) fica envergonhado(a) quando está com pessoas novas",                "subescala": "anx_social"},
    {"numero": 10, "texto": "Meu(minha) filho(a) preocupa-se com o que os outros pensam dele(dela)",                  "subescala": "anx_social"},
    {"numero": 11, "texto": "Meu(minha) filho(a) fica muito nervoso(a) ao falar em público",                         "subescala": "anx_social"},
    {"numero": 12, "texto": "Meu(minha) filho(a) fica com medo de parecer idiota quando está com outros",             "subescala": "anx_social"},
    {"numero": 13, "texto": "Meu(minha) filho(a) evita participar de atividades em grupo",                           "subescala": "anx_social"},
    {"numero": 14, "texto": "Meu(minha) filho(a) é muito tímido(a) com crianças desconhecidas",                      "subescala": "anx_social"},
    # Subescala: Evitação de Danos
    {"numero": 15, "texto": "Meu(minha) filho(a) verifica repetidamente se fez tudo certo",                          "subescala": "evit_danos"},
    {"numero": 16, "texto": "Meu(minha) filho(a) tem que terminar tudo que começa",                                  "subescala": "evit_danos"},
    {"numero": 17, "texto": "Meu(minha) filho(a) é perfeccionista",                                                  "subescala": "evit_danos"},
    {"numero": 18, "texto": "Meu(minha) filho(a) acha que tem que fazer tudo perfeito",                              "subescala": "evit_danos"},
    {"numero": 19, "texto": "Meu(minha) filho(a) trabalha nas tarefas até ficarem perfeitas",                        "subescala": "evit_danos"},
    {"numero": 20, "texto": "Meu(minha) filho(a) tem dificuldade em finalizar as tarefas por insatisfação",          "subescala": "evit_danos"},
    {"numero": 21, "texto": "Meu(minha) filho(a) pensa muito antes de começar algo novo",                            "subescala": "evit_danos"},
    # Subescala: Ansiedade de Separação / Pânico
    {"numero": 22, "texto": "Meu(minha) filho(a) fica muito perturbado(a) quando se separa dos pais",               "subescala": "sep_panico"},
    {"numero": 23, "texto": "Meu(minha) filho(a) pensa em coisas assustadoras",                                      "subescala": "sep_panico"},
    {"numero": 24, "texto": "Meu(minha) filho(a) tem medo de ficar doente",                                          "subescala": "sep_panico"},
    {"numero": 25, "texto": "Meu(minha) filho(a) fica preocupado(a) quando alguém perto está doente ou triste",     "subescala": "sep_panico"},
    {"numero": 26, "texto": "Meu(minha) filho(a) tem pesadelos",                                                     "subescala": "sep_panico"},
    {"numero": 27, "texto": "Meu(minha) filho(a) acha difícil dormir longe de casa",                                 "subescala": "sep_panico"},
    {"numero": 28, "texto": "Meu(minha) filho(a) não gosta de ficar sozinho(a) em casa",                            "subescala": "sep_panico"},
    {"numero": 29, "texto": "Meu(minha) filho(a) sente medo de ir para a escola",                                    "subescala": "sep_panico"},
    {"numero": 30, "texto": "Meu(minha) filho(a) chora facilmente quando se preocupa",                               "subescala": "sep_panico"},
    {"numero": 31, "texto": "Meu(minha) filho(a) tem medo de coisas específicas (altura, escuro, insetos)",         "subescala": "sep_panico"},
    {"numero": 32, "texto": "Meu(minha) filho(a) é muito sensível às críticas dos adultos",                          "subescala": "sep_panico"},
    {"numero": 33, "texto": "Meu(minha) filho(a) preocupa-se com o que vai acontecer no futuro",                    "subescala": "sep_panico"},
    {"numero": 34, "texto": "Meu(minha) filho(a) se preocupa demais com as coisas",                                  "subescala": "sep_panico"},
    {"numero": 35, "texto": "Meu(minha) filho(a) fica preocupado(a) que algo ruim lhe aconteça",                    "subescala": "sep_panico"},
    {"numero": 36, "texto": "Meu(minha) filho(a) fica nervoso(a) quando as coisas não saem como esperado",          "subescala": "sep_panico"},
    {"numero": 37, "texto": "Meu(minha) filho(a) teme que seus pais possam morrer",                                 "subescala": "sep_panico"},
    {"numero": 38, "texto": "Meu(minha) filho(a) fica inseguro(a) quando não sabe o que vai acontecer",             "subescala": "sep_panico"},
    {"numero": 39, "texto": "Meu(minha) filho(a) tem crises de choro sem motivo claro",                             "subescala": "sep_panico"},
]

for item in MASC_ITENS:
    item["reverso"] = False

MASC_SUBESCALAS = {
    "sint_fisicos": {"nome": "Sintomas Físicos",              "itens": [1, 2, 3, 4, 5, 6],                       "cor": "#C0392B", "campo": "pont_sint_fisicos"},
    "anx_social":   {"nome": "Ansiedade Social",              "itens": [7, 8, 9, 10, 11, 12, 13, 14],            "cor": "#9B59B6", "campo": "pont_anx_social"},
    "evit_danos":   {"nome": "Evitação de Danos",             "itens": [15, 16, 17, 18, 19, 20, 21],             "cor": "#27AE60", "campo": "pont_evit_danos"},
    "sep_panico":   {"nome": "Ansiedade de Separação / Pânico","itens": list(range(22, 40)),                      "cor": "#3498DB", "campo": "pont_sep_panico"},
}

MASC_OPCOES = [
    {"valor": 0, "label": "Nunca / Raramente"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Frequentemente"},
    {"valor": 3, "label": "Quase sempre"},
]

MASC_CORTE = {
    "sint_fisicos": [("Normal", 0,  6), ("Elevado",  7, 18)],
    "anx_social":   [("Normal", 0, 10), ("Elevado", 11, 24)],
    "evit_danos":   [("Normal", 0,  8), ("Elevado",  9, 21)],
    "sep_panico":   [("Normal", 0, 12), ("Elevado", 13, 54)],
    "total":        [("Normal", 0, 25), ("Elevado", 26, 117)],
}
