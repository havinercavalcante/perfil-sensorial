# UCLA Loneliness Scale — Versão 3 (Russell, 1996)
# Itens 1,5,6,9,10,15,16,19,20 são POSITIVOS (escore invertido: 4→1, 3→2, 2→3, 1→4)
# Demais são negativos (escore direto)
UCLA_REVERSOS = {1, 5, 6, 9, 10, 15, 16, 19, 20}
UCLA_OPCOES = [
    {"valor": 1, "label": "Nunca"},
    {"valor": 2, "label": "Raramente"},
    {"valor": 3, "label": "Às vezes"},
    {"valor": 4, "label": "Frequentemente"},
]
UCLA_ITENS = [
    (1,  "Com que frequência você sente que está 'em sintonia' com as pessoas ao seu redor?"),
    (2,  "Com que frequência você sente que está com falta de companhia?"),
    (3,  "Com que frequência você sente que não há ninguém com quem você possa recorrer?"),
    (4,  "Com que frequência você se sente sozinho(a)?"),
    (5,  "Com que frequência você sente que faz parte de um grupo de amigos?"),
    (6,  "Com que frequência você sente que tem muito em comum com as pessoas ao seu redor?"),
    (7,  "Com que frequência você sente que não está mais próximo de ninguém?"),
    (8,  "Com que frequência você sente que seus interesses e ideias não são compartilhados por outras pessoas?"),
    (9,  "Com que frequência você sente que é uma pessoa sociável e amigável?"),
    (10, "Com que frequência você sente que há pessoas próximas de você?"),
    (11, "Com que frequência você sente que está sendo deixado(a) de lado?"),
    (12, "Com que frequência você sente que seus relacionamentos sociais não são significativos?"),
    (13, "Com que frequência você sente que ninguém realmente te conhece bem?"),
    (14, "Com que frequência você sente que está isolado(a) das outras pessoas?"),
    (15, "Com que frequência você consegue encontrar companhia quando quer?"),
    (16, "Com que frequência você sente que há pessoas que realmente te entendem?"),
    (17, "Com que frequência você sente que é tímido(a)?"),
    (18, "Com que frequência você sente que há pessoas ao seu redor, mas que não estão com você?"),
    (19, "Com que frequência você sente que há pessoas com quem você pode conversar?"),
    (20, "Com que frequência você sente que há pessoas com quem você pode recorrer?"),
]
UCLA_CORTE = [
    ("Solidão mínima",    20, 34),
    ("Solidão moderada",  35, 49),
    ("Solidão elevada",   50, 64),
    ("Solidão muito alta",65, 80),
]