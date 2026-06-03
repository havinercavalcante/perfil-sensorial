# LSAS — Liebowitz Social Anxiety Scale (Liebowitz, 1987)
# Simplificado: apenas Fear subscale, 24 itens, 0-3
LSAS_OPCOES = [
    {"valor": 0, "label": "Nenhum"},
    {"valor": 1, "label": "Leve"},
    {"valor": 2, "label": "Moderado"},
    {"valor": 3, "label": "Grave"},
]
LSAS_ITENS = [
    (1,  "Telefonar para lugares públicos (ex: restaurante, lojas)"),
    (2,  "Participar de grupos pequenos"),
    (3,  "Comer em lugares públicos"),
    (4,  "Beber com outras pessoas em lugares públicos"),
    (5,  "Conversar com pessoas em posição de autoridade"),
    (6,  "Atuar, realizar ou dar um discurso em frente a uma audiência"),
    (7,  "Ir a uma festa"),
    (8,  "Trabalhar enquanto está sendo observado(a)"),
    (9,  "Escrever enquanto está sendo observado(a)"),
    (10, "Telefonar para alguém que você não conhece bem"),
    (11, "Falar com pessoas que não conhece bem"),
    (12, "Encontrar pessoas estranhas"),
    (13, "Urinar em banheiro público"),
    (14, "Entrar em uma sala onde outras pessoas já estejam sentadas"),
    (15, "Ser o centro das atenções"),
    (16, "Falar em uma reunião"),
    (17, "Fazer um teste"),
    (18, "Expressar desacordo ou desaprovação a pessoas que você não conhece bem"),
    (19, "Olhar nos olhos de pessoas que você não conhece bem"),
    (20, "Dar relatório a um grupo"),
    (21, "Tentar paquerar alguém"),
    (22, "Devolver mercadoria para uma loja"),
    (23, "Dar uma festa"),
    (24, "Resistir à pressão de um vendedor insistente"),
]
LSAS_CORTE = [
    ("Sem fobia social", 0, 29),
    ("Fobia social moderada", 30, 49),
    ("Fobia social acentuada", 50, 64),
    ("Fobia social grave", 65, 79),
    ("Fobia social muito grave", 80, 72),
]