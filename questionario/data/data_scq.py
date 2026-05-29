# SCQ — Social Communication Questionnaire (Rutter et al., 2003)
# 40 itens Sim/Não (1=Sim, 0=Não), itens de rastreio para TEA
# Corte: ≥ 15 indica rastreio positivo para TEA
# Respondido por pais; refere-se ao comportamento atual (≥4 anos)

SCQ_ITENS = [
    {"numero":  1, "texto": "Sua criança usa frases de pelo menos 4–5 palavras?",                                    "chave": 0},  # Não = 1 ponto
    {"numero":  2, "texto": "Você pode ter uma conversa com sua criança?",                                           "chave": 0},  # Não = 1 ponto
    {"numero":  3, "texto": "Sua criança usa linguagem de maneira estranha ou incomum?",                             "chave": 1},  # Sim = 1 ponto
    {"numero":  4, "texto": "Sua criança usa palavras de maneira inapropriada?",                                     "chave": 1},
    {"numero":  5, "texto": "Sua criança inventa palavras ou frases novas?",                                         "chave": 1},
    {"numero":  6, "texto": "Sua criança repete as mesmas coisas repetidamente?",                                    "chave": 1},
    {"numero":  7, "texto": "Sua criança pode descrever algo de forma simples?",                                     "chave": 0},  # Não = 1 ponto
    {"numero":  8, "texto": "Quando ela fala, você entende o que está dizendo?",                                     "chave": 0},  # Não = 1 ponto
    {"numero":  9, "texto": "Sua criança conversa sobre seus interesses com outros?",                                "chave": 0},  # Não = 1 ponto
    {"numero": 10, "texto": "Sua criança fala sobre seus sentimentos com você?",                                     "chave": 0},  # Não = 1 ponto
    {"numero": 11, "texto": "Sua criança olha para o seu rosto para verificar como você reagiu?",                   "chave": 0},  # Não = 1 ponto
    {"numero": 12, "texto": "Sua criança sorriso ao ver você ou quando você sorri?",                                 "chave": 0},  # Não = 1 ponto
    {"numero": 13, "texto": "Sua criança responde quando você chama seu nome?",                                      "chave": 0},  # Não = 1 ponto
    {"numero": 14, "texto": "Sua criança olha para você quando você fala com ela?",                                  "chave": 0},  # Não = 1 ponto
    {"numero": 15, "texto": "Sua criança imita suas ações ou as de outras pessoas?",                                 "chave": 0},  # Não = 1 ponto
    {"numero": 16, "texto": "Sua criança aponta para coisas que lhe interessam?",                                    "chave": 0},  # Não = 1 ponto
    {"numero": 17, "texto": "Sua criança traz objetos para mostrar a você?",                                        "chave": 0},  # Não = 1 ponto
    {"numero": 18, "texto": "Sua criança tem bom amigo(a) de mesma idade?",                                         "chave": 0},  # Não = 1 ponto
    {"numero": 19, "texto": "Sua criança brinca de faz-de-conta com outras crianças?",                              "chave": 0},  # Não = 1 ponto
    {"numero": 20, "texto": "Sua criança se junta às brincadeiras de outras crianças voluntariamente?",             "chave": 0},  # Não = 1 ponto
    {"numero": 21, "texto": "Sua criança parece perceber os sentimentos dos outros?",                               "chave": 0},  # Não = 1 ponto
    {"numero": 22, "texto": "Sua criança console alguém que está triste ou magoado?",                               "chave": 0},  # Não = 1 ponto
    {"numero": 23, "texto": "Sua criança tem amizades com crianças de mesma idade?",                                "chave": 0},  # Não = 1 ponto
    {"numero": 24, "texto": "Sua criança entende quando as pessoas estão brincando?",                               "chave": 0},  # Não = 1 ponto
    {"numero": 25, "texto": "Sua criança percebe quando as pessoas ficam com ela por educação?",                    "chave": 0},  # Não = 1 ponto
    {"numero": 26, "texto": "Sua criança tem interesses repetitivos e rotinas rígidas?",                            "chave": 1},  # Sim = 1 ponto
    {"numero": 27, "texto": "Sua criança fica perturbada com pequenas mudanças de rotina?",                         "chave": 1},
    {"numero": 28, "texto": "Sua criança tem movimentos repetitivos (balançar, agitar mãos)?",                      "chave": 1},
    {"numero": 29, "texto": "Sua criança tem interesses incomuns e específicos intensos?",                          "chave": 1},
    {"numero": 30, "texto": "Sua criança organiza objetos repetidamente?",                                          "chave": 1},
    {"numero": 31, "texto": "Sua criança parece hipersensível a sons?",                                             "chave": 1},
    {"numero": 32, "texto": "Sua criança tem comportamentos repetitivos com objetos?",                              "chave": 1},
    {"numero": 33, "texto": "Sua criança cheira ou lambe objetos incomuns?",                                        "chave": 1},
    {"numero": 34, "texto": "Sua criança anda na ponta dos pés com frequência?",                                    "chave": 1},
    {"numero": 35, "texto": "Sua criança se machuca sem querer?",                                                   "chave": 1},
    {"numero": 36, "texto": "Sua criança tem comportamentos que podem machucá-la?",                                 "chave": 1},
    {"numero": 37, "texto": "Sua criança tem expressões faciais inapropriadas?",                                    "chave": 1},
    {"numero": 38, "texto": "Sua criança tem postura corporal estranha?",                                           "chave": 1},
    {"numero": 39, "texto": "Sua criança usa gestos incomuns para comunicar?",                                      "chave": 1},
    {"numero": 40, "texto": "Sua criança usa gestos de apontar para comunicar desejos?",                           "chave": 0},  # Não = 1 ponto
]

for item in SCQ_ITENS:
    item["subescala"] = "total"
    item["reverso"] = False

SCQ_SUBESCALAS = {
    "total": {"nome": "Pontuação Total", "itens": list(range(1, 41)), "cor": "#1A5276", "campo": "pont_total"},
}

SCQ_OPCOES = [
    {"valor": 0, "label": "Não"},
    {"valor": 1, "label": "Sim"},
]

SCQ_CORTE = {
    "total": [
        ("Rastreio Negativo", 0, 14),
        ("Rastreio Positivo", 15, 40),
    ],
}
