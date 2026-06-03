# ETDAH — Escala de Transtorno de Déficit de Atenção/Hiperatividade
# Versões: Pais e Professor
# 25 itens, escala 0–3 (nunca/às vezes/frequentemente/sempre)
# 3 subescalas: Desatenção (12 itens), Hiperatividade/Impulsividade (9 itens), TOD (4 itens)
# Ponto de corte por subescala: média ≥ 1,5 é clinicamente significativa

ETDAH_ITENS_PAIS = [
    # Desatenção (itens 1–12)
    {"numero":  1, "texto": "Não presta atenção suficiente a detalhes ou comete erros por descuido",                  "subescala": "desatencao"},
    {"numero":  2, "texto": "Tem dificuldade em manter a atenção em tarefas ou atividades lúdicas",                   "subescala": "desatencao"},
    {"numero":  3, "texto": "Parece não ouvir quando chamado(a) diretamente",                                         "subescala": "desatencao"},
    {"numero":  4, "texto": "Não segue as instruções e não termina as tarefas",                                       "subescala": "desatencao"},
    {"numero":  5, "texto": "Tem dificuldade para organizar tarefas e atividades",                                    "subescala": "desatencao"},
    {"numero":  6, "texto": "Evita, não gosta ou reluta em envolver-se em tarefas que exijam esforço mental",        "subescala": "desatencao"},
    {"numero":  7, "texto": "Perde objetos necessários para as tarefas ou atividades",                               "subescala": "desatencao"},
    {"numero":  8, "texto": "Distrai-se facilmente com estímulos externos",                                          "subescala": "desatencao"},
    {"numero":  9, "texto": "É esquecido(a) nas atividades diárias",                                                 "subescala": "desatencao"},
    {"numero": 10, "texto": "Tem dificuldade em começar atividades sem precisar de incentivo",                       "subescala": "desatencao"},
    {"numero": 11, "texto": "Tem dificuldade em concluir o que começa",                                              "subescala": "desatencao"},
    {"numero": 12, "texto": "Tem dificuldade em seguir sequências de instruções",                                    "subescala": "desatencao"},
    # Hiperatividade/Impulsividade (itens 13–21)
    {"numero": 13, "texto": "Agita as mãos ou os pés ou se mexe no assento",                                        "subescala": "hiperativ"},
    {"numero": 14, "texto": "Levanta do lugar quando deveria permanecer sentado(a)",                                 "subescala": "hiperativ"},
    {"numero": 15, "texto": "Corre ou sobe em coisas excessivamente em situações em que é inadequado",              "subescala": "hiperativ"},
    {"numero": 16, "texto": "Tem dificuldade para brincar silenciosamente",                                         "subescala": "hiperativ"},
    {"numero": 17, "texto": "Fala excessivamente",                                                                  "subescala": "hiperativ"},
    {"numero": 18, "texto": "Dá respostas antes que as perguntas tenham sido concluídas",                           "subescala": "hiperativ"},
    {"numero": 19, "texto": "Tem dificuldade em aguardar a sua vez",                                                "subescala": "hiperativ"},
    {"numero": 20, "texto": "Interrompe ou se intromete nos assuntos de outros",                                    "subescala": "hiperativ"},
    {"numero": 21, "texto": "Age como se estivesse com motor ligado",                                               "subescala": "hiperativ"},
    # TOD — Transtorno Opositivo Desafiador (itens 22–25)
    {"numero": 22, "texto": "Perde a calma facilmente",                                                             "subescala": "tod"},
    {"numero": 23, "texto": "Discute com adultos",                                                                  "subescala": "tod"},
    {"numero": 24, "texto": "Desafia ou recusa seguir as regras dos adultos",                                       "subescala": "tod"},
    {"numero": 25, "texto": "Culpa os outros pelos seus erros ou comportamento inadequado",                         "subescala": "tod"},
]

for item in ETDAH_ITENS_PAIS:
    item["reverso"] = False

ETDAH_ITENS_PROF = [
    {"numero":  1, "texto": "Não presta atenção suficiente a detalhes ou comete erros por descuido nas tarefas escolares", "subescala": "desatencao"},
    {"numero":  2, "texto": "Tem dificuldade em manter a atenção durante as aulas",                                        "subescala": "desatencao"},
    {"numero":  3, "texto": "Parece não ouvir quando chamado(a) diretamente na sala de aula",                              "subescala": "desatencao"},
    {"numero":  4, "texto": "Não segue as instruções e não termina as tarefas escolares",                                  "subescala": "desatencao"},
    {"numero":  5, "texto": "Tem dificuldade para organizar tarefas e materiais escolares",                                "subescala": "desatencao"},
    {"numero":  6, "texto": "Evita tarefas que exijam esforço mental sustentado",                                         "subescala": "desatencao"},
    {"numero":  7, "texto": "Perde materiais necessários para as atividades escolares",                                    "subescala": "desatencao"},
    {"numero":  8, "texto": "Distrai-se facilmente com estímulos da sala de aula",                                        "subescala": "desatencao"},
    {"numero":  9, "texto": "Esquece de entregar tarefas ou trazer materiais",                                             "subescala": "desatencao"},
    {"numero": 10, "texto": "Precisa de incentivo constante para começar as atividades",                                   "subescala": "desatencao"},
    {"numero": 11, "texto": "Tem dificuldade em concluir as tarefas escolares",                                            "subescala": "desatencao"},
    {"numero": 12, "texto": "Tem dificuldade em seguir sequências de instruções na escola",                                "subescala": "desatencao"},
    {"numero": 13, "texto": "Agita as mãos ou os pés ou se mexe no assento durante a aula",                               "subescala": "hiperativ"},
    {"numero": 14, "texto": "Levanta do lugar sem permissão",                                                              "subescala": "hiperativ"},
    {"numero": 15, "texto": "Corre ou sobe em coisas em situações inapropriadas na escola",                               "subescala": "hiperativ"},
    {"numero": 16, "texto": "Tem dificuldade para se engajar silenciosamente em atividades",                              "subescala": "hiperativ"},
    {"numero": 17, "texto": "Fala excessivamente na aula",                                                                "subescala": "hiperativ"},
    {"numero": 18, "texto": "Responde antes que as perguntas tenham sido concluídas",                                     "subescala": "hiperativ"},
    {"numero": 19, "texto": "Tem dificuldade em esperar a sua vez na sala de aula",                                      "subescala": "hiperativ"},
    {"numero": 20, "texto": "Interrompe ou se intromete em atividades dos colegas",                                      "subescala": "hiperativ"},
    {"numero": 21, "texto": "Está sempre em movimento durante a aula",                                                   "subescala": "hiperativ"},
    {"numero": 22, "texto": "Perde a calma facilmente na escola",                                                        "subescala": "tod"},
    {"numero": 23, "texto": "Discute com o professor ou outros adultos",                                                 "subescala": "tod"},
    {"numero": 24, "texto": "Desafia ou recusa seguir as regras da escola",                                              "subescala": "tod"},
    {"numero": 25, "texto": "Culpa os outros pelos seus erros",                                                          "subescala": "tod"},
]

for item in ETDAH_ITENS_PROF:
    item["reverso"] = False

ETDAH_SUBESCALAS = {
    "desatencao": {"nome": "Desatenção",                    "itens": list(range(1, 13)),  "cor": "#3498DB", "campo": "pont_desatencao"},
    "hiperativ":  {"nome": "Hiperatividade/Impulsividade",  "itens": list(range(13, 22)), "cor": "#E74C3C", "campo": "pont_hiperativ"},
    "tod":        {"nome": "TOD",                           "itens": list(range(22, 26)), "cor": "#E67E22", "campo": "pont_tod"},
}

ETDAH_OPCOES = [
    {"valor": 0, "label": "Nunca"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Frequentemente"},
    {"valor": 3, "label": "Sempre"},
]

ETDAH_CORTE = {
    "desatencao": [("Normal", 0, 11), ("Limítrofe", 12, 14), ("Elevado", 15, 36)],
    "hiperativ":  [("Normal", 0,  8), ("Limítrofe",  9, 11), ("Elevado", 12, 27)],
    "tod":        [("Normal", 0,  3), ("Limítrofe",  4,  5), ("Elevado",  6, 12)],
    "total":      [("Normal", 0, 22), ("Limítrofe", 23, 30), ("Elevado", 31, 75)],
}
