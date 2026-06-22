SEPS_OPCOES = [
    {"valor": 0, "label": "Nunca"},
    {"valor": 1, "label": "Raramente"},
    {"valor": 2, "label": "Às vezes"},
    {"valor": 3, "label": "Frequentemente"},
    {"valor": 4, "label": "Sempre"},
]

SEPS_ITENS = [
    (1,  "A minha criança só come comidas que sejam quentes."),
    (2,  "A minha criança apenas aceita um sabor de cada tipo de comida (p.ex., iogurte de morango)."),
    (3,  "A minha criança come uma mesma comida por semanas ou meses seguidos."),
    (4,  "A minha criança claramente não gosta quando a comida toca os seus lábios."),
    (5,  "A minha criança não gosta quando a comida toca os seus dentes."),
    (6,  "A minha criança é sensível à temperatura da comida."),
    (7,  "A minha criança só come comidas frias."),
    (8,  "A minha criança só come comidas que estejam à temperatura ambiente."),
    (9,  "A minha criança tem arranques de vômito quando a comida toca na sua língua."),
    (10, "A minha criança expele comida ou líquidos pela boca."),
    (11, "A minha criança usa os seus dedos para tirar comida da sua boca."),
    (12, "A minha criança tem dificuldade em tocar na comida com os seus dedos."),
    (13, "A minha criança tem um reflexo de vômito muito sensível."),
    (14, "A minha criança recusa categorias inteiras de comida (ex. todos os frutos, todos os vegetais)."),
    (15, "A minha criança fica chateada quando a comida ou líquidos tocam os seus lábios."),
    (16, "A minha criança enche demasiado a boca com comida."),
    (17, "A minha criança tenta engolir pedaços demasiado grandes de comida."),
    (18, "A minha criança tenta engolir pedaços de comida sem mastigar."),
    (19, "A minha criança tem arranques de vômito quando uma colher é colocada diretamente na sua língua."),
    (20, "A minha criança cospe comida ou líquidos."),
    (21, "A minha criança evita misturas de diferentes texturas na comida (ex. spaghetti e almôndegas)."),
    (22, "A minha criança puxa para vomitar ou vomita quando vê comidas novas."),
]

# Subescalas: nome -> lista de números de itens
SEPS_SUBESCALAS = {
    "aversao_toque":  {"nome": "Aversão ao toque da comida",   "itens": [4, 5, 12, 15], "max": 16},
    "foco_unica":     {"nome": "Foco numa única comida",        "itens": [2, 3, 14, 21], "max": 16},
    "vomito":         {"nome": "Vômito",                        "itens": [9, 13, 19, 22], "max": 16},
    "sensib_temp":    {"nome": "Sensibilidade à temperatura",   "itens": [1, 6, 7, 8],   "max": 16},
    "expulsao":       {"nome": "Expulsão",                      "itens": [10, 11, 20],   "max": 12},
    "encher":         {"nome": "Encher demasiado",              "itens": [16, 17, 18],   "max": 12},
}
