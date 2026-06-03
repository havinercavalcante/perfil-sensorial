# Conners-3 — Conners 3rd Edition (Conners, 2008)
# Versões: Pais e Professor
# 45 itens, escala 0–3 (nunca/raramente/às vezes/frequentemente)
# 6 subescalas

CONNERS_ITENS_PAIS = [
    # Desatenção
    {"numero":  1, "texto": "Tem dificuldade em prestar atenção em detalhes ou comete erros por descuido nas tarefas",              "subescala": "desatencao"},
    {"numero":  2, "texto": "Tem dificuldade em manter atenção em tarefas ou jogos",                                               "subescala": "desatencao"},
    {"numero":  3, "texto": "Parece não ouvir quando lhe falam diretamente",                                                       "subescala": "desatencao"},
    {"numero":  4, "texto": "Não segue instruções e não termina as tarefas",                                                       "subescala": "desatencao"},
    {"numero":  5, "texto": "Tem dificuldade em organizar tarefas e atividades",                                                   "subescala": "desatencao"},
    {"numero":  6, "texto": "Evita tarefas que exigem esforço mental sustentado",                                                  "subescala": "desatencao"},
    {"numero":  7, "texto": "Perde coisas necessárias para as atividades",                                                        "subescala": "desatencao"},
    {"numero":  8, "texto": "Distrai-se com estímulos externos",                                                                  "subescala": "desatencao"},
    {"numero":  9, "texto": "Esquece atividades do dia a dia",                                                                    "subescala": "desatencao"},
    # Hiperatividade/Impulsividade
    {"numero": 10, "texto": "Mexe ou torce as mãos ou os pés ou se contorce no assento",                                          "subescala": "hiperativ"},
    {"numero": 11, "texto": "Levanta do lugar em que devia ficar sentado(a)",                                                     "subescala": "hiperativ"},
    {"numero": 12, "texto": "Corre ou sobe em coisas em situações inapropriadas",                                                 "subescala": "hiperativ"},
    {"numero": 13, "texto": "Tem dificuldade em brincar calmamente",                                                             "subescala": "hiperativ"},
    {"numero": 14, "texto": "Está 'a mil' ou age como se tivesse com 'motor ligado'",                                            "subescala": "hiperativ"},
    {"numero": 15, "texto": "Fala excessivamente",                                                                               "subescala": "hiperativ"},
    {"numero": 16, "texto": "Responde antes que a pergunta seja concluída",                                                      "subescala": "hiperativ"},
    {"numero": 17, "texto": "Tem dificuldade em esperar a sua vez",                                                              "subescala": "hiperativ"},
    {"numero": 18, "texto": "Interrompe ou se intromete nas atividades dos outros",                                              "subescala": "hiperativ"},
    # Problemas de Aprendizagem
    {"numero": 19, "texto": "Tem dificuldades com leitura",                                                                     "subescala": "aprend"},
    {"numero": 20, "texto": "Tem dificuldades com escrita/soletração",                                                         "subescala": "aprend"},
    {"numero": 21, "texto": "Tem dificuldades com matemática",                                                                  "subescala": "aprend"},
    {"numero": 22, "texto": "Aprende lentamente",                                                                               "subescala": "aprend"},
    {"numero": 23, "texto": "Tem dificuldades para entender o que lê",                                                          "subescala": "aprend"},
    # Problemas de Execução
    {"numero": 24, "texto": "Tem dificuldade para iniciar tarefas sem apoio",                                                    "subescala": "exec"},
    {"numero": 25, "texto": "Tem dificuldade em mudar de uma atividade para outra",                                             "subescala": "exec"},
    {"numero": 26, "texto": "Tem dificuldade em planejar tarefas complexas",                                                    "subescala": "exec"},
    {"numero": 27, "texto": "Tem dificuldade em verificar se fez os trabalhos corretamente",                                    "subescala": "exec"},
    {"numero": 28, "texto": "Tem dificuldade em trabalhar de forma independente",                                               "subescala": "exec"},
    # Problemas com Relacionamentos com Pares
    {"numero": 29, "texto": "Fica fora dos grupos",                                                                             "subescala": "pares"},
    {"numero": 30, "texto": "Tem poucos amigos",                                                                                "subescala": "pares"},
    {"numero": 31, "texto": "Tem dificuldade em manter amizades",                                                              "subescala": "pares"},
    {"numero": 32, "texto": "Não é aceito pelos colegas",                                                                      "subescala": "pares"},
    {"numero": 33, "texto": "Sente-se rejeitado pelos colegas",                                                                "subescala": "pares"},
    # Agressividade
    {"numero": 34, "texto": "Fica com raiva facilmente",                                                                       "subescala": "agressiv"},
    {"numero": 35, "texto": "Discute com adultos",                                                                             "subescala": "agressiv"},
    {"numero": 36, "texto": "Não segue as regras deliberadamente",                                                             "subescala": "agressiv"},
    {"numero": 37, "texto": "Aborrece deliberadamente os outros",                                                              "subescala": "agressiv"},
    {"numero": 38, "texto": "Culpa outros por seus erros",                                                                     "subescala": "agressiv"},
    {"numero": 39, "texto": "Fica ressentido facilmente",                                                                      "subescala": "agressiv"},
    {"numero": 40, "texto": "É rancoroso(a) ou vingativo(a)",                                                                  "subescala": "agressiv"},
    {"numero": 41, "texto": "Ameaça ou intimida os outros",                                                                    "subescala": "agressiv"},
    {"numero": 42, "texto": "Inicia brigas",                                                                                   "subescala": "agressiv"},
    {"numero": 43, "texto": "Mente para conseguir coisas ou para evitar obrigações",                                           "subescala": "agressiv"},
    {"numero": 44, "texto": "Destrói propositalmente bens de outros",                                                         "subescala": "agressiv"},
    {"numero": 45, "texto": "Age cruelmente com os outros",                                                                    "subescala": "agressiv"},
]

for item in CONNERS_ITENS_PAIS:
    item["reverso"] = False

# Versão professor usa os mesmos itens com linguagem adaptada para o contexto escolar
CONNERS_ITENS_PROF = [
    {"numero":  1, "texto": "Tem dificuldade em prestar atenção a detalhes ou comete erros por descuido nas atividades escolares", "subescala": "desatencao"},
    {"numero":  2, "texto": "Tem dificuldade em manter atenção em tarefas ou atividades de aula",                                  "subescala": "desatencao"},
    {"numero":  3, "texto": "Parece não ouvir quando lhe falam diretamente na sala de aula",                                       "subescala": "desatencao"},
    {"numero":  4, "texto": "Não segue instruções e não termina as tarefas escolares",                                             "subescala": "desatencao"},
    {"numero":  5, "texto": "Tem dificuldade em organizar tarefas escolares",                                                      "subescala": "desatencao"},
    {"numero":  6, "texto": "Evita tarefas que exigem esforço mental sustentado",                                                  "subescala": "desatencao"},
    {"numero":  7, "texto": "Perde materiais escolares necessários",                                                              "subescala": "desatencao"},
    {"numero":  8, "texto": "Distrai-se com estímulos externos durante a aula",                                                   "subescala": "desatencao"},
    {"numero":  9, "texto": "Esquece atividades escolares do dia a dia",                                                          "subescala": "desatencao"},
    {"numero": 10, "texto": "Mexe ou torce as mãos, pés ou se contorce no assento durante a aula",                               "subescala": "hiperativ"},
    {"numero": 11, "texto": "Levanta do lugar sem permissão",                                                                     "subescala": "hiperativ"},
    {"numero": 12, "texto": "Corre ou sobe em coisas em situações inapropriadas na escola",                                      "subescala": "hiperativ"},
    {"numero": 13, "texto": "Tem dificuldade em brincar ou realizar atividades calmamente",                                      "subescala": "hiperativ"},
    {"numero": 14, "texto": "Está sempre em movimento, como se tivesse motor ligado",                                            "subescala": "hiperativ"},
    {"numero": 15, "texto": "Fala excessivamente em sala de aula",                                                               "subescala": "hiperativ"},
    {"numero": 16, "texto": "Responde antes que a pergunta seja concluída",                                                      "subescala": "hiperativ"},
    {"numero": 17, "texto": "Tem dificuldade em esperar a sua vez",                                                              "subescala": "hiperativ"},
    {"numero": 18, "texto": "Interrompe ou se intromete nas atividades dos outros",                                              "subescala": "hiperativ"},
    {"numero": 19, "texto": "Tem dificuldades com leitura",                                                                     "subescala": "aprend"},
    {"numero": 20, "texto": "Tem dificuldades com escrita/soletração",                                                         "subescala": "aprend"},
    {"numero": 21, "texto": "Tem dificuldades com matemática",                                                                  "subescala": "aprend"},
    {"numero": 22, "texto": "Aprende lentamente em relação aos colegas",                                                        "subescala": "aprend"},
    {"numero": 23, "texto": "Tem dificuldades para compreender textos",                                                         "subescala": "aprend"},
    {"numero": 24, "texto": "Tem dificuldade para iniciar tarefas sem apoio do professor",                                      "subescala": "exec"},
    {"numero": 25, "texto": "Tem dificuldade em mudar de uma atividade para outra",                                             "subescala": "exec"},
    {"numero": 26, "texto": "Tem dificuldade em planejar tarefas complexas",                                                    "subescala": "exec"},
    {"numero": 27, "texto": "Não verifica se completou os trabalhos corretamente",                                              "subescala": "exec"},
    {"numero": 28, "texto": "Tem dificuldade em trabalhar de forma independente na escola",                                     "subescala": "exec"},
    {"numero": 29, "texto": "Fica de fora dos grupos na escola",                                                               "subescala": "pares"},
    {"numero": 30, "texto": "Tem poucos amigos na escola",                                                                     "subescala": "pares"},
    {"numero": 31, "texto": "Tem dificuldade em manter amizades com colegas",                                                  "subescala": "pares"},
    {"numero": 32, "texto": "Não é aceito pelos colegas",                                                                      "subescala": "pares"},
    {"numero": 33, "texto": "Parece sentir-se rejeitado pelos colegas",                                                        "subescala": "pares"},
    {"numero": 34, "texto": "Fica com raiva facilmente na escola",                                                             "subescala": "agressiv"},
    {"numero": 35, "texto": "Discute com adultos na escola",                                                                   "subescala": "agressiv"},
    {"numero": 36, "texto": "Não segue as regras da escola deliberadamente",                                                   "subescala": "agressiv"},
    {"numero": 37, "texto": "Aborrece deliberadamente os colegas",                                                             "subescala": "agressiv"},
    {"numero": 38, "texto": "Culpa outros por seus erros",                                                                     "subescala": "agressiv"},
    {"numero": 39, "texto": "Fica ressentido facilmente",                                                                      "subescala": "agressiv"},
    {"numero": 40, "texto": "É rancoroso(a) ou vingativo(a)",                                                                  "subescala": "agressiv"},
    {"numero": 41, "texto": "Ameaça ou intimida os colegas",                                                                   "subescala": "agressiv"},
    {"numero": 42, "texto": "Inicia brigas",                                                                                   "subescala": "agressiv"},
    {"numero": 43, "texto": "Mente para conseguir coisas",                                                                     "subescala": "agressiv"},
    {"numero": 44, "texto": "Destrói materiais ou pertences dos outros",                                                       "subescala": "agressiv"},
    {"numero": 45, "texto": "Age cruelmente com os colegas",                                                                   "subescala": "agressiv"},
]

for item in CONNERS_ITENS_PROF:
    item["reverso"] = False

CONNERS_SUBESCALAS = {
    "desatencao": {"nome": "Desatenção",                 "itens": list(range(1, 10)),  "cor": "#3498DB", "campo": "pont_desatencao"},
    "hiperativ":  {"nome": "Hiperatividade/Impulsividade","itens": list(range(10, 19)), "cor": "#E74C3C", "campo": "pont_hiperativ"},
    "aprend":     {"nome": "Problemas de Aprendizagem",  "itens": list(range(19, 24)), "cor": "#F1C40F", "campo": "pont_aprend"},
    "exec":       {"nome": "Funções Executivas",         "itens": list(range(24, 29)), "cor": "#27AE60", "campo": "pont_exec"},
    "pares":      {"nome": "Relação com Pares",          "itens": list(range(29, 34)), "cor": "#9B59B6", "campo": "pont_pares"},
    "agressiv":   {"nome": "Agressividade/TOD",          "itens": list(range(34, 46)), "cor": "#E67E22", "campo": "pont_agressiv"},
}

CONNERS_OPCOES = [
    {"valor": 0, "label": "Nunca / Raramente"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Frequentemente"},
    {"valor": 3, "label": "Quase sempre / Sempre"},
]

CONNERS_CORTE = {
    "desatencao": [("Normal", 0, 9),  ("Limítrofe", 10, 13), ("Elevado", 14, 27)],
    "hiperativ":  [("Normal", 0, 9),  ("Limítrofe", 10, 13), ("Elevado", 14, 27)],
    "aprend":     [("Normal", 0, 5),  ("Limítrofe",  6,  7), ("Elevado",  8, 15)],
    "exec":       [("Normal", 0, 5),  ("Limítrofe",  6,  7), ("Elevado",  8, 15)],
    "pares":      [("Normal", 0, 4),  ("Limítrofe",  5,  6), ("Elevado",  7, 15)],
    "agressiv":   [("Normal", 0, 12), ("Limítrofe", 13, 16), ("Elevado", 17, 36)],
    "total":      [("Normal", 0, 45), ("Limítrofe", 46, 59), ("Elevado", 60, 135)],
}
