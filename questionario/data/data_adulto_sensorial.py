# Perfil Sensorial do Adulto/Adolescente — Catana Brown & Winnie Dunn
# 60 itens, escala: 1=Quase nunca, 2=Raramente, 3=Ocasionalmente,
#                   4=Frequentemente, 5=Quase sempre

SECOES_ADULTO = [
    {"id": "tatil_olfativo", "nome": "A. Processamento Tátil / Olfativo", "itens": list(range(1, 9))},
    {"id": "movimento",      "nome": "B. Processamento de Movimento",      "itens": list(range(9, 17))},
    {"id": "visual",         "nome": "C. Processamento Visual",            "itens": list(range(17, 27))},
    {"id": "tatil",          "nome": "D. Processamento Tátil",             "itens": list(range(27, 40))},
    {"id": "atividade",      "nome": "E. Nível de Atividade",              "itens": list(range(40, 50))},
    {"id": "auditivo",       "nome": "F. Processamento Auditivo",          "itens": list(range(50, 61))},
]

PERGUNTAS_ADULTO = {
    # A. Tátil/Olfativo
    1:  "Saio ou mudo para outra parte de loja (por ex. produtos para banho, velas, perfumes).",
    2:  "Acrescento temperos na minha comida.",
    3:  "Não sinto cheiros que outras pessoas sentem.",
    4:  "Gosto de estar próxima a pessoas usando perfume.",
    5:  "Só como comidas familiares.",
    6:  "Muitas comidas parecem sem sabor para mim (parece sem graça ou não tem muito sabor).",
    7:  "Não gosto de balas de sabor muito forte (por ex., canela forte ou azedas).",
    8:  "Vou cheirar flores frescas quando as vejo.",
    # B. Movimento
    9:  "Tenho medo de alturas.",
    10: "Gosta da sensação de movimento (dançar, correr, por ex.).",
    11: "Evito elevadores e escadas rolantes porque não gosto de movimento.",
    12: "Tropeço nas coisas.",
    13: "Não gosto do movimento de andar de carro.",
    14: "Escolho me envolver em atividades físicas.",
    15: "Não me sinto muito seguro quando descendo ou subindo escadas (por ex., tropeço, perco o equilíbrio).",
    16: "Fico tonto facilmente (por ex., após me curvar ou levantar muito rapidamente).",
    # C. Visual
    17: "Gosto de ir a lugares com iluminação brilhante e que são coloridos.",
    18: "Mantenho as persianas fechadas durante o dia.",
    19: "Gosto de usar roupa muito colorida.",
    20: "Fico frustrado quando tento encontrar alguma coisa em uma gaveta cheia ou sala bagunçada.",
    21: "Não vejo a rua, prédio, ou placas de salas quando tento ir a um lugar novo.",
    22: "Imagens visuais que se movem rapidamente no cinema ou TV me incomodam.",
    23: "Não noto quando pessoas entram na sala.",
    24: "Escolho fazer compras em lojas menores porque me desoriento em lojas grandes.",
    25: "Incomoda-me quando há muito movimento ao meu redor (por ex. shopping cheio, desfile, parquinho).",
    26: "Limito as distrações enquanto trabalho (por ex., fecho a porta ou desligo a TV).",
    # D. Tátil
    27: "Não gosto que me esfreguem as costas.",
    28: "Gosto da sensação quando corto o cabelo.",
    29: "Evito ou uso luvas em atividades que vão sujar as minhas mãos.",
    30: "Toco outros enquanto falo (por ex., ponho minha mão em seus ombros ou sacudo suas mãos).",
    31: "Incomoda-me o modo que sinto minha boca quando acordo.",
    32: "Gosto de andar descalço.",
    33: "Sinto-me mal usando alguns tecidos (por ex, lã, seda, veludo cotelê, etiquetas em roupas).",
    34: "Não gosto de certas texturas de alimentos (por ex., pêssegos com casca, purê de maçã).",
    35: "Afasto-me quando chegam muito perto de mim.",
    36: "Não pareço notar quando meu rosto e mãos estão sujos.",
    37: "Arranho-me ou tenho marcas roxas mas não me lembro como os fiz.",
    38: "Evito ficar em filas ou ficar próximo a outras pessoas porque não gosto de ficar próximo demais.",
    39: "Não pareço notar quando alguém toca meu braço ou costas.",
    # E. Nível de Atividade
    40: "Trabalho em duas ou mais tarefas ao mesmo tempo.",
    41: "Levo mais tempo que outras pessoas para acordar de manhã.",
    42: "Faço as coisas de improviso (faço coisas sem planejar antes).",
    43: "Acho tempo para me afastar da minha vida ocupada e passar tempo sozinho.",
    44: "Pareço mais lenta que outros quando tento seguir uma atividade ou tarefa.",
    45: "Não pego piadas tão rapidamente quanto outros.",
    46: "Afasto-me de multidões.",
    47: "Acho atividades para fazer em frente a outros (por ex., música, esportes, falar em público).",
    48: "Acho difícil me concentrar por todo o tempo em uma aula ou reunião longos.",
    49: "Evito situações em que possam acontecer coisas inesperadas.",
    # F. Auditivo
    50: "Cantarolo, assobio, canto ou faço outros barulhos.",
    51: "Assusto-me facilmente com sons altos ou inesperados.",
    52: "Tenho dificuldade em seguir o que as pessoas estão falando quando falam rapidamente.",
    53: "Saio da sala quando outros assistem TV ou peço a eles que desliguem.",
    54: "Distraio-me se há muito barulho em volta.",
    55: "Não noto quando meu nome é chamado.",
    56: "Uso estratégias para abafar sons (por ex., fecho a porta, cubro os ouvidos).",
    57: "Fico longe de ambientes barulhentos.",
    58: "Gosto de ir a lugares com muita música.",
    59: "Tenho de pedir a pessoas que repitam coisas.",
    60: "Acho difícil trabalhar com barulho de fundo (por ex., ventilador, rádio).",
}

# Quadrantes (da Folha de Sumário de Resultados)
# Q1=Baixo Registro, Q2=Procura Sensação, Q3=Sensitividade, Q4=Evita Sensação
QUADRANTE_ADULTO = {
    3: "Q1", 6: "Q1", 12: "Q1", 15: "Q1", 21: "Q1", 23: "Q1",
    36: "Q1", 37: "Q1", 39: "Q1", 41: "Q1", 44: "Q1", 45: "Q1",
    52: "Q1", 55: "Q1", 59: "Q1",

    2: "Q2", 4: "Q2", 8: "Q2", 10: "Q2", 14: "Q2", 17: "Q2",
    19: "Q2", 28: "Q2", 30: "Q2", 32: "Q2", 40: "Q2", 42: "Q2",
    47: "Q2", 50: "Q2", 58: "Q2",

    7: "Q3", 9: "Q3", 13: "Q3", 16: "Q3", 20: "Q3", 22: "Q3",
    25: "Q3", 27: "Q3", 31: "Q3", 33: "Q3", 34: "Q3", 48: "Q3",
    51: "Q3", 54: "Q3", 60: "Q3",

    1: "Q4", 5: "Q4", 11: "Q4", 18: "Q4", 24: "Q4", 26: "Q4",
    29: "Q4", 35: "Q4", 38: "Q4", 43: "Q4", 46: "Q4", 49: "Q4",
    53: "Q4", 56: "Q4", 57: "Q4",
}

ITENS_Q1 = [i for i, q in QUADRANTE_ADULTO.items() if q == "Q1"]
ITENS_Q2 = [i for i, q in QUADRANTE_ADULTO.items() if q == "Q2"]
ITENS_Q3 = [i for i, q in QUADRANTE_ADULTO.items() if q == "Q3"]
ITENS_Q4 = [i for i, q in QUADRANTE_ADULTO.items() if q == "Q4"]

TOTAL_ITENS_ADULTO = 60

OPCOES_ADULTO = [
    (1, "Quase nunca"),
    (2, "Raramente"),
    (3, "Ocasionalmente"),
    (4, "Frequentemente"),
    (5, "Quase sempre"),
]

# Faixas de classificação por quadrante (idades 18-64)
QUADRANTES_CONFIG_ADULTO = {
    "Q1": {"nome": "Baixo Registro",      "max": 75,
           "faixas": [(15,18,"Muito menos"),(19,23,"Menos"),(24,35,"Típico"),(36,44,"Mais"),(45,75,"Muito mais")]},
    "Q2": {"nome": "Procura Sensação",    "max": 75,
           "faixas": [(15,35,"Muito menos"),(36,42,"Menos"),(43,56,"Típico"),(57,62,"Mais"),(63,75,"Muito mais")]},
    "Q3": {"nome": "Sensitividade Sensorial","max": 75,
           "faixas": [(15,18,"Muito menos"),(19,25,"Menos"),(26,41,"Típico"),(42,48,"Mais"),(49,75,"Muito mais")]},
    "Q4": {"nome": "Evita Sensação",      "max": 75,
           "faixas": [(15,19,"Muito menos"),(20,26,"Menos"),(27,41,"Típico"),(42,49,"Mais"),(50,75,"Muito mais")]},
}


def calcular_pontuacao_adulto(respostas: dict) -> dict:
    """respostas: {numero_item: valor (1-5)}"""
    result = {}
    for secao in SECOES_ADULTO:
        result[secao["id"]] = sum(respostas.get(i, 0) for i in secao["itens"])
    result["Q1"] = sum(respostas.get(i, 0) for i in ITENS_Q1)
    result["Q2"] = sum(respostas.get(i, 0) for i in ITENS_Q2)
    result["Q3"] = sum(respostas.get(i, 0) for i in ITENS_Q3)
    result["Q4"] = sum(respostas.get(i, 0) for i in ITENS_Q4)
    return result
