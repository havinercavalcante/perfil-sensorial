# BIS-11 — Barratt Impulsiveness Scale (Patton et al., 1995)
# Itens REVERSOS (menor impulsividade = escore maior): 9,20,30
BIS11_REVERSOS = {9, 20, 30}
BIS11_OPCOES = [
    {"valor": 1, "label": "Raramente / Nunca"},
    {"valor": 2, "label": "De vez em quando"},
    {"valor": 3, "label": "Frequentemente"},
    {"valor": 4, "label": "Quase sempre / Sempre"},
]
BIS11_ITENS = [
    (1,  "Planejo minhas tarefas com cuidado."),
    (2,  "Faço coisas sem pensar."),
    (3,  "Tomo decisões rapidamente."),
    (4,  "Sou uma pessoa sem preocupações."),
    (5,  "Não presto atenção."),
    (6,  "Tenho pensamentos que se sucedem rapidamente."),
    (7,  "Planejo viagens com antecedência."),
    (8,  "Tenho autocontrole."),
    (9,  "Concentro-me facilmente."),
    (10, "Poupo dinheiro regularmente."),
    (11, "Fico me mexendo nos cinemas ou palestra."),
    (12, "Sou um(a) pensador(a) cuidadoso(a)."),
    (13, "Planejo minha segurança no trabalho."),
    (14, "Digo coisas sem pensar."),
    (15, "Gosto de pensar sobre problemas complexos."),
    (16, "Troco de emprego."),
    (17, "Ajo por impulso."),
    (18, "Fico entediado(a) com facilidade ao resolver problemas mentais."),
    (19, "Ajo no impulso do momento."),
    (20, "Sou uma pessoa que pensa sobre os problemas."),
    (21, "Troco de residência."),
    (22, "Compro coisas por impulso."),
    (23, "Só consigo pensar em uma coisa de cada vez."),
    (24, "Troco de passatempo."),
    (25, "Gasto mais do que ganho."),
    (26, "Quando estou pensando, tenho outros pensamentos paralelos."),
    (27, "Estou mais interessado no presente do que no futuro."),
    (28, "Fico inquieto(a) em palestras ou aulas."),
    (29, "Gosto de quebra-cabeças."),
    (30, "Penso no futuro."),
]
BIS11_CORTE = [
    ("Baixa impulsividade",     30, 52),
    ("Impulsividade média",     53, 70),
    ("Alta impulsividade",      71, 120),
]