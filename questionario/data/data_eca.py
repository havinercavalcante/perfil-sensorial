ECA_OPCOES = [
    {"valor": 1, "label": "Não"},
    {"valor": 2, "label": "Raramente"},
    {"valor": 3, "label": "Às vezes"},
    {"valor": 4, "label": "Frequentemente"},
    {"valor": 5, "label": "Sempre"},
]

ECA_ITENS = [
    # Subescala: Motricidade na Mastigação (itens 1-6)
    (1,  "Dificuldades de mastigar os alimentos"),
    (2,  "Dificuldades na sucção de líquidos (canudo, mamadeira, peito)"),
    (3,  "Engole os alimentos sem mastigar suficientemente"),
    (4,  "Engasga com alimentos"),
    (5,  "Regurgita os alimentos, durante ou imediatamente após as refeições"),
    (6,  "Rumina os alimentos (regurgita e mastiga novamente)"),
    # Subescala: Seletividade Alimentar (itens 7-23)
    (7,  "Seleciona alimentos pela marca"),
    (8,  "Seleciona alimentos pela embalagem (ex: somente de caixa ou saco plástico)"),
    (9,  "Seleciona alimentos por determinada temperatura (só quente ou só frio)"),
    (10, "Seleciona alimentos pela cor"),
    (11, "Seleciona alimentos de uma determinada textura ou rejeita em função da textura"),
    (12, "Seletivo por refeições molhadas (ex: alimentos com molhos ou caldo de feijão)"),
    (13, "Seletivo por refeições mais secas (ex: sem nenhum molho ou caldo de feijão)"),
    (14, "Seletivo por alimentos crocantes"),
    (15, "Seletivo por alimentos com textura macia (ex: purê)"),
    (16, "Seletivo por alimentos amassados"),
    (17, "Seletivo por alimentos liquidificados"),
    (18, "Seletivo por alimentos liquidificados e coados (passados na peneira ou na flanela)"),
    (19, "Evita comer carnes"),
    (20, "Evita comer frango"),
    (21, "Evita comer vegetais"),
    (22, "Evita comer frutas"),
    (23, "Retira o tempero da comida (ex: pedaços de coentro, cebolinha ou tomate)"),
    # Subescala: Aspectos Comportamentais (itens 24-35, exceto 34)
    (24, "Cospe a comida"),
    (25, "Possui ritual para comer (alimentos arrumados de forma específica; fica irritado se alterado)"),
    (26, "Come sempre no mesmo lugar"),
    (27, "Come sempre com os mesmos utensílios (mesmo prato, garfo, colher ou copo)"),
    (28, "Possui comportamento agressivo durante as refeições (auto-lesão, destruição de objetos)"),
    (29, "Possui um padrão rígido na arrumação do local onde faz as refeições"),
    (30, "Come uma grande quantidade de alimento num período de tempo curto"),
    (31, "Pega sem permissão comida de outras pessoas durante as refeições"),
    (32, "Pega sem permissão comida fora do horário das refeições"),
    (33, "Vomita, durante ou imediatamente após as refeições"),
    (35, "Ingere objetos estranhos/bizarros (ex. sabão, terra, plástico, chiclete)"),
    # Subescala: Sintomas Gastrointestinais (itens 36-42)
    (36, "Refluxo"),
    (37, "Constipação"),
    (38, "Diarreia"),
    (39, "Vômito"),
    (40, "Alergia alimentar (ex: amendoim, frutos do mar)"),
    (41, "Intolerância ao glúten"),
    (42, "Intolerância à lactose"),
    # Subescala: Sensibilidade Sensorial (itens 43-47)
    (43, "Incomoda-se com barulhos (ex: som alto, voz, liquidificador)"),
    (44, "Incomoda-se com cheiros fortes (ex: comida, gasolina, tinta, perfume)"),
    (45, "Incomoda-se com coisas pegajosas (ex: hidratante, tinta, massa de modelar)"),
    (46, "Incomoda-se com o toque"),
    (47, "Incomoda-se em trocar de roupas, tomar banho, etiqueta das roupas"),
    # Subescala: Habilidades nas Refeições (itens 48-51)
    (48, "Tem dificuldades de sentar-se à mesa para fazer as refeições (ex: almoça no chão, sofá, cama)"),
    (49, "Derrama muito a comida na mesa ou na roupa quando se alimenta"),
    (50, "Meu filho tem mais de 3 anos e só come com a ajuda de outra pessoa"),
    (51, "Tem dificuldades de utilizar os talheres"),
]

# Subescalas: nome -> lista de números de itens
ECA_SUBESCALAS = {
    "mastigacao":     {"nome": "Motricidade na Mastigação",   "itens": [1, 2, 3, 4, 5, 6],                       "max": 30},
    "seletividade":   {"nome": "Seletividade Alimentar",      "itens": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], "max": 85},
    "comportamental": {"nome": "Aspectos Comportamentais",    "itens": [24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 35], "max": 55},
    "gi":             {"nome": "Sintomas Gastrointestinais",  "itens": [36, 37, 38, 39, 40, 41, 42],              "max": 35},
    "sensorial":      {"nome": "Sensibilidade Sensorial",     "itens": [43, 44, 45, 46, 47],                      "max": 25},
    "habilidades":    {"nome": "Habilidades nas Refeições",   "itens": [48, 49, 50, 51],                          "max": 20},
}
