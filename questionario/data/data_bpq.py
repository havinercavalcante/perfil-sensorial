# BPQ — Borderline Personality Questionnaire (Poreh et al., 2006)
# 80 itens Verdadeiro/Falso (1=Verdadeiro, 0=Falso)
# 9 subescalas de acordo com os critérios do DSM para TPB
# Pontuação: soma dos itens "chave" (verdadeiro) por subescala

BPQ_ITENS = [
    # Subescala 1 — Impulsividade (9 itens)
    {"numero":  1, "texto": "Ajo impulsivamente e depois me arrependo",                                                "subescala": "impulsividade", "chave": 1},
    {"numero":  2, "texto": "Tenho dificuldade em controlar minha raiva",                                              "subescala": "impulsividade", "chave": 1},
    {"numero":  3, "texto": "Às vezes faço coisas sem pensar nas consequências",                                       "subescala": "impulsividade", "chave": 1},
    {"numero":  4, "texto": "Tenho o hábito de gastar dinheiro de forma irresponsável",                                "subescala": "impulsividade", "chave": 1},
    {"numero":  5, "texto": "Já tive problemas com uso de substâncias (álcool, drogas)",                               "subescala": "impulsividade", "chave": 1},
    {"numero":  6, "texto": "Já dirigi com imprudência pondo em risco a minha vida",                                   "subescala": "impulsividade", "chave": 1},
    {"numero":  7, "texto": "Tenho dificuldade em parar de comer mesmo quando não estou com fome",                     "subescala": "impulsividade", "chave": 1},
    {"numero":  8, "texto": "Faço coisas perigosas para obter emoção",                                                 "subescala": "impulsividade", "chave": 1},
    {"numero":  9, "texto": "Frequentemente começo relacionamentos intensos muito rapidamente",                        "subescala": "impulsividade", "chave": 1},

    # Subescala 2 — Instabilidade Afetiva (8 itens)
    {"numero": 10, "texto": "Meu humor muda de repente e sem motivo aparente",                                         "subescala": "inst_afetiva", "chave": 1},
    {"numero": 11, "texto": "Sou muito sensível às críticas",                                                          "subescala": "inst_afetiva", "chave": 1},
    {"numero": 12, "texto": "Pequenas coisas podem me deixar muito triste ou muito feliz",                             "subescala": "inst_afetiva", "chave": 1},
    {"numero": 13, "texto": "Às vezes me sinto muito bem, outras vezes me sinto péssimo(a)",                          "subescala": "inst_afetiva", "chave": 1},
    {"numero": 14, "texto": "Tenho acessos de raiva que não consigo controlar",                                        "subescala": "inst_afetiva", "chave": 1},
    {"numero": 15, "texto": "Meu relacionamento com as pessoas tende a ser instável",                                  "subescala": "inst_afetiva", "chave": 1},
    {"numero": 16, "texto": "Fico magoado(a) muito facilmente",                                                        "subescala": "inst_afetiva", "chave": 1},
    {"numero": 17, "texto": "Às vezes me sinto eufórico(a), outras vezes deprimido(a), sem razão clara",              "subescala": "inst_afetiva", "chave": 1},

    # Subescala 3 — Problemas de Identidade (9 itens)
    {"numero": 18, "texto": "Frequentemente não sei quem sou ou o que quero da vida",                                  "subescala": "identidade", "chave": 1},
    {"numero": 19, "texto": "Minha opinião sobre mim mesmo(a) muda muito",                                            "subescala": "identidade", "chave": 1},
    {"numero": 20, "texto": "Às vezes me sinto vazio(a) por dentro",                                                   "subescala": "identidade", "chave": 1},
    {"numero": 21, "texto": "Muitas vezes não tenho certeza dos meus valores e crenças",                               "subescala": "identidade", "chave": 1},
    {"numero": 22, "texto": "Sinto que sou uma pessoa diferente com pessoas diferentes",                               "subescala": "identidade", "chave": 1},
    {"numero": 23, "texto": "Não sei quais são os meus objetivos de longo prazo",                                      "subescala": "identidade", "chave": 1},
    {"numero": 24, "texto": "Mudo minha opinião sobre mim mesmo(a) com base no que os outros pensam",                 "subescala": "identidade", "chave": 1},
    {"numero": 25, "texto": "Frequentemente me pergunto quem realmente sou",                                           "subescala": "identidade", "chave": 1},
    {"numero": 26, "texto": "Tenho dificuldade em manter metas de longo prazo",                                        "subescala": "identidade", "chave": 1},

    # Subescala 4 — Relações Interpessoais (9 itens)
    {"numero": 27, "texto": "Meus relacionamentos tendem a ser muito intensos e instáveis",                            "subescala": "relacoes", "chave": 1},
    {"numero": 28, "texto": "Frequentemente idealizo as pessoas e depois as desvalorizo",                              "subescala": "relacoes", "chave": 1},
    {"numero": 29, "texto": "Tenho dificuldade em manter relacionamentos por muito tempo",                             "subescala": "relacoes", "chave": 1},
    {"numero": 30, "texto": "Frequentemente sinto que os outros me abandonam",                                         "subescala": "relacoes", "chave": 1},
    {"numero": 31, "texto": "Faço grandes esforços para evitar o abandono",                                            "subescala": "relacoes", "chave": 1},
    {"numero": 32, "texto": "Alterno entre adorar e odiar pessoas próximas",                                           "subescala": "relacoes", "chave": 1},
    {"numero": 33, "texto": "Sinto que as pessoas não me entendem",                                                    "subescala": "relacoes", "chave": 1},
    {"numero": 34, "texto": "Tenho dificuldade em confiar nas pessoas",                                                "subescala": "relacoes", "chave": 1},
    {"numero": 35, "texto": "Frequentemente sinto que as pessoas são cruéis ou indiferentes comigo",                   "subescala": "relacoes", "chave": 1},

    # Subescala 5 — Automutilação e Comportamentos Suicidas (7 itens)
    {"numero": 36, "texto": "Já me machuquei de propósito (cortes, queimaduras, etc.)",                               "subescala": "automutilacao", "chave": 1},
    {"numero": 37, "texto": "Já pensei em me matar",                                                                   "subescala": "automutilacao", "chave": 1},
    {"numero": 38, "texto": "Já tentei me matar",                                                                      "subescala": "automutilacao", "chave": 1},
    {"numero": 39, "texto": "Às vezes sinto que seria melhor estar morto(a)",                                          "subescala": "automutilacao", "chave": 1},
    {"numero": 40, "texto": "Machucar-me fisicamente me ajuda a lidar com a dor emocional",                           "subescala": "automutilacao", "chave": 1},
    {"numero": 41, "texto": "Já usei ameaças de me matar para influenciar os outros",                                  "subescala": "automutilacao", "chave": 1},
    {"numero": 42, "texto": "Quando estou muito angustiado(a), sinto vontade de me machucar",                         "subescala": "automutilacao", "chave": 1},

    # Subescala 6 — Medo de Abandono (9 itens)
    {"numero": 43, "texto": "Tenho muito medo de ser abandonado(a)",                                                   "subescala": "medo_abandono", "chave": 1},
    {"numero": 44, "texto": "Faço tudo que posso para que as pessoas não me deixem",                                   "subescala": "medo_abandono", "chave": 1},
    {"numero": 45, "texto": "A ideia de ficar sozinho(a) me apavora",                                                  "subescala": "medo_abandono", "chave": 1},
    {"numero": 46, "texto": "Quando alguém próximo vai embora, fico muito ansioso(a)",                                 "subescala": "medo_abandono", "chave": 1},
    {"numero": 47, "texto": "Prefiro estar em relacionamentos ruins a ficar sozinho(a)",                               "subescala": "medo_abandono", "chave": 1},
    {"numero": 48, "texto": "Sinto que minha vida não tem sentido quando estou sozinho(a)",                            "subescala": "medo_abandono", "chave": 1},
    {"numero": 49, "texto": "O medo de abandono me faz agir de formas que depois me arrependerei",                    "subescala": "medo_abandono", "chave": 1},
    {"numero": 50, "texto": "Frequentemente verifico se as pessoas ainda gostam de mim",                              "subescala": "medo_abandono", "chave": 1},
    {"numero": 51, "texto": "Fico muito perturbado(a) quando alguém parte, mesmo que por pouco tempo",                "subescala": "medo_abandono", "chave": 1},

    # Subescala 7 — Ideias Paranoides / Dissociação (9 itens)
    {"numero": 52, "texto": "Às vezes suspeito que as pessoas querem me prejudicar",                                   "subescala": "paranoia", "chave": 1},
    {"numero": 53, "texto": "Quando estou estressado(a), às vezes me sinto 'fora do meu corpo'",                      "subescala": "paranoia", "chave": 1},
    {"numero": 54, "texto": "Às vezes sinto que as coisas ao meu redor não são reais",                                "subescala": "paranoia", "chave": 1},
    {"numero": 55, "texto": "Às vezes ouço vozes ou vejo coisas que os outros não percebem",                          "subescala": "paranoia", "chave": 1},
    {"numero": 56, "texto": "Às vezes sinto que estou me tornando outra pessoa",                                       "subescala": "paranoia", "chave": 1},
    {"numero": 57, "texto": "Frequentemente desconfio das intenções das pessoas",                                      "subescala": "paranoia", "chave": 1},
    {"numero": 58, "texto": "Tenho pensamentos perturbadores e repetitivos",                                           "subescala": "paranoia", "chave": 1},
    {"numero": 59, "texto": "Às vezes me dissocio — perco a noção do tempo",                                          "subescala": "paranoia", "chave": 1},
    {"numero": 60, "texto": "Em situações de estresse, tenho experiências incomuns",                                   "subescala": "paranoia", "chave": 1},

    # Subescala 8 — Sentimento Crônico de Vazio (9 itens)
    {"numero": 61, "texto": "Frequentemente me sinto vazio(a) por dentro",                                             "subescala": "vazio", "chave": 1},
    {"numero": 62, "texto": "Sinto que falta algo importante na minha vida",                                           "subescala": "vazio", "chave": 1},
    {"numero": 63, "texto": "Sinto um vazio interior que nunca consigo preencher",                                     "subescala": "vazio", "chave": 1},
    {"numero": 64, "texto": "Frequentemente me sinto entorpecido(a) emocionalmente",                                   "subescala": "vazio", "chave": 1},
    {"numero": 65, "texto": "Às vezes faço coisas arriscadas para me sentir vivo(a)",                                  "subescala": "vazio", "chave": 1},
    {"numero": 66, "texto": "Sinto que minha vida não tem propósito",                                                  "subescala": "vazio", "chave": 1},
    {"numero": 67, "texto": "Frequentemente me sinto desconectado(a) das minhas emoções",                             "subescala": "vazio", "chave": 1},
    {"numero": 68, "texto": "Sinto que nunca estou realmente feliz",                                                   "subescala": "vazio", "chave": 1},
    {"numero": 69, "texto": "Sinto que vivo no piloto automático sem envolvimento real",                               "subescala": "vazio", "chave": 1},

    # Subescala 9 — Raiva Intensa e Inapropriada (11 itens)
    {"numero": 70, "texto": "Tenho explosões de raiva que me surpreendem",                                             "subescala": "raiva", "chave": 1},
    {"numero": 71, "texto": "Minha raiva causa problemas nos meus relacionamentos",                                    "subescala": "raiva", "chave": 1},
    {"numero": 72, "texto": "Às vezes fico com tanta raiva que perco o controle",                                      "subescala": "raiva", "chave": 1},
    {"numero": 73, "texto": "Minha raiva é intensa em comparação com a maioria das pessoas",                           "subescala": "raiva", "chave": 1},
    {"numero": 74, "texto": "Frequentemente sinto raiva de pessoas próximas",                                          "subescala": "raiva", "chave": 1},
    {"numero": 75, "texto": "Depois de uma explosão de raiva, me sinto envergonhado(a)",                               "subescala": "raiva", "chave": 1},
    {"numero": 76, "texto": "Tenho dificuldade em perdoar os outros quando me machucam",                               "subescala": "raiva", "chave": 1},
    {"numero": 77, "texto": "Pessoas me dizem que reajo de forma exagerada",                                           "subescala": "raiva", "chave": 1},
    {"numero": 78, "texto": "Frequentemente me sinto hostil em relação aos outros",                                    "subescala": "raiva", "chave": 1},
    {"numero": 79, "texto": "Minha raiva faz com que eu tome decisões ruins",                                          "subescala": "raiva", "chave": 1},
    {"numero": 80, "texto": "Às vezes desejo fazer mal a alguém quando estou com raiva",                              "subescala": "raiva", "chave": 1},
]

for item in BPQ_ITENS:
    item["reverso"] = False

BPQ_SUBESCALAS = {
    "impulsividade":  {"nome": "Impulsividade",                    "itens": list(range(1, 10)),  "cor": "#E74C3C", "campo": "pont_impulsividade"},
    "inst_afetiva":   {"nome": "Instabilidade Afetiva",            "itens": list(range(10, 18)), "cor": "#E67E22", "campo": "pont_inst_afetiva"},
    "identidade":     {"nome": "Problemas de Identidade",          "itens": list(range(18, 27)), "cor": "#F1C40F", "campo": "pont_identidade"},
    "relacoes":       {"nome": "Relações Interpessoais",           "itens": list(range(27, 36)), "cor": "#27AE60", "campo": "pont_relacoes"},
    "automutilacao":  {"nome": "Automutilação / Suicídio",         "itens": list(range(36, 43)), "cor": "#2C3E50", "campo": "pont_automutilacao"},
    "medo_abandono":  {"nome": "Medo de Abandono",                 "itens": list(range(43, 52)), "cor": "#9B59B6", "campo": "pont_medo_abandono"},
    "paranoia":       {"nome": "Ideias Paranoides / Dissociação",  "itens": list(range(52, 61)), "cor": "#1ABC9C", "campo": "pont_paranoia"},
    "vazio":          {"nome": "Sentimento de Vazio",              "itens": list(range(61, 70)), "cor": "#3498DB", "campo": "pont_vazio"},
    "raiva":          {"nome": "Raiva Intensa",                    "itens": list(range(70, 81)), "cor": "#C0392B", "campo": "pont_raiva"},
}

BPQ_OPCOES = [
    {"valor": 0, "label": "Falso"},
    {"valor": 1, "label": "Verdadeiro"},
]

BPQ_CORTE = {
    "total": [
        ("Baixo",  0, 25),
        ("Médio", 26, 55),
        ("Alto",  56, 80),
    ],
}
