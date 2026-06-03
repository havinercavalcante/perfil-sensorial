# Questionário de Rastreio de Agorafobia (adaptado clínico)
AGORAFOBIA_OPCOES = [
    {"valor": 0, "label": "Nenhum medo / Não evito"},
    {"valor": 1, "label": "Medo / Evitação leve"},
    {"valor": 2, "label": "Medo / Evitação moderada"},
    {"valor": 3, "label": "Medo / Evitação acentuada"},
    {"valor": 4, "label": "Medo / Evitação grave — situação sempre evitada"},
]
AGORAFOBIA_ITENS = [
    (1,  "Usar transporte público (ônibus, metrô, trem)"),
    (2,  "Estar em espaços abertos (estacionamentos, praças, pontes)"),
    (3,  "Estar em locais fechados (lojas, cinemas, teatros)"),
    (4,  "Ficar em fila ou em multidão"),
    (5,  "Estar fora de casa sozinho(a)"),
    (6,  "Sair de casa sabendo que pode não conseguir escapar facilmente"),
    (7,  "Estar em elevadores"),
    (8,  "Frequentar restaurantes ou shoppings movimentados"),
    (9,  "Viajar de carro longas distâncias"),
    (10, "Ficar sozinho(a) em casa"),
    (11, "Lugares de onde seria difícil sair rapidamente"),
    (12, "Andar de avião"),
    (13, "Assistir eventos esportivos ou shows com muita gente"),
    (14, "Cruzar pontes ou túneis"),
]
AGORAFOBIA_CORTE = [
    ("Sem agorafobia",       0, 13),
    ("Agorafobia leve",     14, 27),
    ("Agorafobia moderada", 28, 41),
    ("Agorafobia grave",    42, 56),
]