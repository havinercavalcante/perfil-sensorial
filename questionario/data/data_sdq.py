SDQ_ITENS = [
    {"numero":  1, "texto": "Considerado(a) com sentimentos alheios",                                                          "subescala": "prossocial",     "reverso": False},
    {"numero":  2, "texto": "Agitado(a), hiperativo(a), não fica sossegado(a)",                                                "subescala": "hiperatividade", "reverso": False},
    {"numero":  3, "texto": "Com frequência se queixa de dores de cabeça, de barriga ou vômitos",                              "subescala": "emocional",      "reverso": False},
    {"numero":  4, "texto": "Tem vontade de compartilhar com outras crianças (guloseimas, brinquedos, etc.)",                  "subescala": "prossocial",     "reverso": False},
    {"numero":  5, "texto": "Tem crises de raiva ou temperamento difícil",                                                     "subescala": "conduta",        "reverso": False},
    {"numero":  6, "texto": "Tende a brincar só(a); prefere ficar sozinho(a)",                                                 "subescala": "pares",          "reverso": False},
    {"numero":  7, "texto": "Geralmente obedece; faz o que os adultos pedem",                                                  "subescala": "conduta",        "reverso": True},
    {"numero":  8, "texto": "Tem muitas preocupações; frequentemente parece preocupado(a)",                                    "subescala": "emocional",      "reverso": False},
    {"numero":  9, "texto": "É prestativo(a) se alguém se machuca, está mal-humorado(a) ou doente",                           "subescala": "prossocial",     "reverso": False},
    {"numero": 10, "texto": "Está constantemente inquieto(a) ou agitado(a)",                                                   "subescala": "hiperatividade", "reverso": False},
    {"numero": 11, "texto": "Tem pelo menos um(a) bom(boa) amigo(a)",                                                         "subescala": "pares",          "reverso": True},
    {"numero": 12, "texto": "Frequentemente briga com outras crianças ou as intimida",                                         "subescala": "conduta",        "reverso": False},
    {"numero": 13, "texto": "Frequentemente infeliz, abatido(a) ou choroso(a)",                                               "subescala": "emocional",      "reverso": False},
    {"numero": 14, "texto": "Geralmente é querido(a) pelas outras crianças",                                                   "subescala": "pares",          "reverso": True},
    {"numero": 15, "texto": "Facilmente se distrai; tem dificuldade de concentração",                                          "subescala": "hiperatividade", "reverso": False},
    {"numero": 16, "texto": "Fica nervoso(a) em situações novas; perde confiança facilmente",                                  "subescala": "emocional",      "reverso": False},
    {"numero": 17, "texto": "É gentil com crianças mais novas",                                                                "subescala": "prossocial",     "reverso": False},
    {"numero": 18, "texto": "Frequentemente mente ou engana",                                                                  "subescala": "conduta",        "reverso": False},
    {"numero": 19, "texto": "Outras crianças implicam com ela, excluem-na ou perseguem-na",                                    "subescala": "pares",          "reverso": False},
    {"numero": 20, "texto": "Frequentemente oferece ajuda voluntariamente (pais, professores, outras crianças)",               "subescala": "prossocial",     "reverso": False},
    {"numero": 21, "texto": "Pensa antes de agir",                                                                             "subescala": "hiperatividade", "reverso": True},
    {"numero": 22, "texto": "Pega coisas que não lhe pertencem em casa, na escola ou em outros locais",                       "subescala": "conduta",        "reverso": False},
    {"numero": 23, "texto": "Se dá melhor com adultos do que com outras crianças",                                             "subescala": "pares",          "reverso": False},
    {"numero": 24, "texto": "Tem muitos medos; assusta-se facilmente",                                                         "subescala": "emocional",      "reverso": False},
    {"numero": 25, "texto": "Completa as tarefas que começa; tem boa concentração",                                            "subescala": "hiperatividade", "reverso": True},
]

SDQ_SUBESCALAS = {
    "emocional":      {"nome": "Sintomas Emocionais",       "itens": [3, 8, 13, 16, 24], "cor": "#E74C3C", "campo": "pont_emocional"},
    "conduta":        {"nome": "Problemas de Conduta",      "itens": [5, 7, 12, 18, 22], "cor": "#E67E22", "campo": "pont_conduta"},
    "hiperatividade": {"nome": "Hiperatividade/Desatenção", "itens": [2, 10, 15, 21, 25], "cor": "#3498DB", "campo": "pont_hiperatividade"},
    "pares":          {"nome": "Problemas com Colegas",     "itens": [6, 11, 14, 19, 23], "cor": "#9B59B6", "campo": "pont_pares"},
    "prossocial":     {"nome": "Comportamento Prossocial",  "itens": [1, 4, 9, 17, 20],  "cor": "#27AE60", "campo": "pont_prossocial"},
}

SDQ_OPCOES = [
    {"valor": 0, "label": "Não é verdade"},
    {"valor": 1, "label": "Um pouco verdade"},
    {"valor": 2, "label": "Muito verdade"},
]

# Pontos de corte para Total de Dificuldades (soma de emocional+conduta+hiper+pares, 0–40)
# e para cada subescala (0–10)
SDQ_CORTE = {
    "emocional":      [("Normal", 0, 3),  ("Limítrofe", 4, 4),   ("Elevado", 5, 10)],
    "conduta":        [("Normal", 0, 2),  ("Limítrofe", 3, 3),   ("Elevado", 4, 10)],
    "hiperatividade": [("Normal", 0, 5),  ("Limítrofe", 6, 6),   ("Elevado", 7, 10)],
    "pares":          [("Normal", 0, 2),  ("Limítrofe", 3, 3),   ("Elevado", 4, 10)],
    "prossocial":     [("Baixo", 0, 4),   ("Médio", 5, 6),       ("Elevado", 7, 10)],
    "total":          [("Normal", 0, 13), ("Limítrofe", 14, 16), ("Elevado", 17, 40)],
}
