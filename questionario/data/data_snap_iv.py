SNAP_IV_ITENS = [
    # ── Desatenção (1–9) ──────────────────────────────────────────────────────
    {"numero":  1, "texto": "Com frequência não presta atenção em detalhes ou comete erros por descuido em tarefas escolares ou outras atividades", "subescala": "desatencao"},
    {"numero":  2, "texto": "Com frequência tem dificuldade de manter a atenção em tarefas ou atividades lúdicas",                                  "subescala": "desatencao"},
    {"numero":  3, "texto": "Com frequência parece não estar ouvindo quando se fala diretamente com ele/ela",                                        "subescala": "desatencao"},
    {"numero":  4, "texto": "Com frequência não segue instruções e não termina tarefas escolares, domésticas ou outras",                             "subescala": "desatencao"},
    {"numero":  5, "texto": "Com frequência tem dificuldade de organizar tarefas e atividades",                                                      "subescala": "desatencao"},
    {"numero":  6, "texto": "Com frequência evita ou reluta em se envolver em tarefas que exijam esforço mental constante",                          "subescala": "desatencao"},
    {"numero":  7, "texto": "Com frequência perde coisas necessárias para tarefas ou atividades",                                                    "subescala": "desatencao"},
    {"numero":  8, "texto": "Com frequência se distrai com estímulos externos",                                                                      "subescala": "desatencao"},
    {"numero":  9, "texto": "Com frequência se esquece de atividades cotidianas",                                                                    "subescala": "desatencao"},
    # ── Hiperatividade / Impulsividade (10–18) ────────────────────────────────
    {"numero": 10, "texto": "Com frequência agita as mãos ou os pés, ou se contorce na cadeira",                                                     "subescala": "hiperatividade"},
    {"numero": 11, "texto": "Com frequência abandona o lugar na sala de aula ou em outras situações em que se espera que permaneça sentado",          "subescala": "hiperatividade"},
    {"numero": 12, "texto": "Com frequência corre ou escala objetos em situações inapropriadas",                                                      "subescala": "hiperatividade"},
    {"numero": 13, "texto": "Com frequência tem dificuldade de brincar ou se envolver em atividades de lazer de forma calma",                         "subescala": "hiperatividade"},
    {"numero": 14, "texto": "Com frequência está \"a mil\" ou age como se estivesse com o motor ligado",                                              "subescala": "hiperatividade"},
    {"numero": 15, "texto": "Com frequência fala em excesso",                                                                                         "subescala": "hiperatividade"},
    {"numero": 16, "texto": "Com frequência dá respostas precipitadas antes que as perguntas sejam concluídas",                                       "subescala": "hiperatividade"},
    {"numero": 17, "texto": "Com frequência tem dificuldade de aguardar sua vez",                                                                     "subescala": "hiperatividade"},
    {"numero": 18, "texto": "Com frequência interrompe ou se intromete em conversas ou jogos alheios",                                                "subescala": "hiperatividade"},
    # ── TOD — Transtorno Opositivo Desafiador (19–26) ─────────────────────────
    {"numero": 19, "texto": "Com frequência perde o controle",                                                                                        "subescala": "tod"},
    {"numero": 20, "texto": "Com frequência discute com adultos",                                                                                     "subescala": "tod"},
    {"numero": 21, "texto": "Com frequência desafia ativamente ou se recusa a obedecer às solicitações dos adultos",                                  "subescala": "tod"},
    {"numero": 22, "texto": "Com frequência faz coisas de propósito que incomodam outras pessoas",                                                    "subescala": "tod"},
    {"numero": 23, "texto": "Com frequência responsabiliza outras pessoas pelos seus erros ou por seu mau comportamento",                              "subescala": "tod"},
    {"numero": 24, "texto": "Com frequência fica bravo e aborrece-se facilmente",                                                                     "subescala": "tod"},
    {"numero": 25, "texto": "Com frequência fica irritado e ressentido",                                                                              "subescala": "tod"},
    {"numero": 26, "texto": "Com frequência é rancoroso(a) ou vingativo(a)",                                                                          "subescala": "tod"},
]

SNAP_IV_SUBESCALAS = {
    "desatencao":     {"nome": "Desatenção",                       "itens": list(range(1, 10)),  "cor": "#3498DB", "campo": "media_desatencao"},
    "hiperatividade": {"nome": "Hiperatividade / Impulsividade",   "itens": list(range(10, 19)), "cor": "#E74C3C", "campo": "media_hiperatividade"},
    "tod":            {"nome": "TOD (Opositivo Desafiador)",        "itens": list(range(19, 27)), "cor": "#E67E22", "campo": "media_tod"},
}

SNAP_IV_OPCOES = [
    {"valor": 0, "label": "Nunca ou raramente"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Com frequência"},
    {"valor": 3, "label": "Muito frequentemente"},
]

# Ponto de corte: média ≥ 1,5 por subescala é clinicamente significativa
SNAP_IV_CORTE = 1.5
