# Cada item: (numero, texto, polo_esquerdo, polo_direito)
EBAI_ITENS = [
    (1,  "O que você acha dos momentos de refeições com a sua criança?",
         "Muito difícil", "Fácil"),
    (2,  "Quão preocupado você está com a alimentação da sua criança?",
         "Não estou preocupado", "Estou muito preocupado"),
    (3,  "Quanto de apetite (fome) sua criança tem?",
         "Nunca tem fome", "Tem um bom apetite"),
    (4,  "Quando a sua criança começa a se recusar a comer durante as refeições?",
         "No início da refeição", "No fim da refeição"),
    (5,  "Quanto tempo (em minutos) dura a refeição da sua criança?",
         "1–10 min", "Mais de 60 min"),
    (6,  "Como a sua criança se comporta durante a refeição?",
         "Se comporta bem", "Faz birra / bagunça / manha"),
    (7,  "A sua criança nauseia, cospe ou vomita com algum tipo de alimento?",
         "Nunca", "Na maioria das vezes"),
    (8,  "A sua criança fica com a comida parada na boca sem engolir?",
         "Na maioria das vezes", "Nunca"),
    (9,  "Você precisa ir atrás da sua criança ou usar distrações (TV, brinquedos) durante a refeição para que ela coma?",
         "Nunca", "Na maioria das vezes"),
    (10, "Você precisa forçar a sua criança a comer ou beber?",
         "Na maioria das vezes", "Nunca"),
    (11, "Como é a habilidade de mastigação (ou sucção) da sua criança?",
         "Boa", "Muito ruim"),
    (12, "O que você acha do crescimento da sua criança?",
         "Crescendo bem", "Crescendo pouco"),
    (13, "Como a alimentação da sua criança influencia a sua relação com ela?",
         "De forma muito negativa", "Não influencia nada"),
    (14, "Como a alimentação da sua criança influencia as suas relações familiares?",
         "Não influencia nada", "De forma muito negativa"),
]

# Itens que devem ter a pontuação invertida (escore_invertido = 8 - valor)
EBAI_ITENS_INVERTIDOS = {1, 3, 4, 8, 10, 12, 13}

# Tabela de conversão Escore Bruto -> Escore T
EBAI_TABELA_T = {
    14: 35, 15: 36, 16: 37, 17: 38, 18: 39, 19: 39, 20: 40, 21: 41, 22: 42, 23: 43,
    24: 43, 25: 44, 26: 45, 27: 46, 28: 46, 29: 47, 30: 48, 31: 49, 32: 50, 33: 50,
    34: 51, 35: 52, 36: 53, 37: 54, 38: 54, 39: 55, 40: 56, 41: 57, 42: 57, 43: 58,
    44: 59, 45: 60, 46: 61, 47: 61, 48: 62, 49: 63, 50: 64, 51: 65, 52: 65, 53: 66,
    54: 67, 55: 68, 56: 68, 57: 69, 58: 70, 59: 71, 60: 72, 61: 72, 62: 73, 63: 74,
    64: 75, 65: 76, 66: 76, 67: 77, 68: 78, 69: 79, 70: 80, 71: 80, 72: 81, 73: 82,
    74: 83, 75: 83, 76: 84, 77: 85, 78: 86, 79: 87, 80: 87, 81: 88, 82: 89, 83: 90,
    84: 91, 85: 91, 86: 92, 87: 93, 88: 94, 89: 94, 90: 95, 91: 96, 92: 97, 93: 98,
    94: 98, 95: 99, 96: 100, 97: 101, 98: 102,
}

EBAI_CORTE = [
    ("Sem dificuldades significativas", 0,  60),
    ("Dificuldades leves",              61, 65),
    ("Dificuldades moderadas",          66, 70),
    ("Dificuldades severas",            71, 999),
]
