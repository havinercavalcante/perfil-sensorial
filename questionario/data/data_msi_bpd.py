# MSI-BPD — McLean Screening Instrument for BPD (Zanarini et al., 2003)
# 10 itens Sim/Não. Sim=1, Não=0 para todos. Corte ≥7.
MSI_BPD_ITENS = [
    {"numero": 1, "texto": "Alguma vez você se machucar intencionalmente (ex: cortar ou queimar a pele), mesmo que não fosse para se suicidar?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 2, "texto": "Você já tentou suicídio?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 3, "texto": "Você tem mudanças frequentes e intensas de humor (ex: sentir euforia de repente e logo depois se sentir triste ou irritado)?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 4, "texto": "Você frequentemente fica com muita raiva?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 5, "texto": "Você frequentemente age impulsivamente (ex: gastos excessivos, promiscuidade, uso de drogas, direção perigosa, compulsão alimentar)?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 6, "texto": "Você já teve relacionamentos intensos e instáveis com pessoas próximas (amigos, cônjuge, filhos) marcados por alternâncias entre idealização e desvalorização?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 7, "texto": "Você faz esforços desesperados para evitar abandono (real ou imaginário)?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 8, "texto": "Você frequentemente sente que não existe, ou que não é real?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 9, "texto": "Você frequentemente sente um vazio crônico e tedioso?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 10, "texto": "Você tem dificuldade em manter um sentido estável de quem você é (valores, objetivos, orientação sexual, identidade)?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
]
MSI_BPD_CORTE = [
    ("Sem indicativo de TPB",    0, 6),
    ("Indicativo provável de TPB", 7, 10),
]