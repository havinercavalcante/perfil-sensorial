# AQ-10 Criança — Autism Quotient 10-item (Baron-Cohen, 2009) — versão criança (6–17 anos)
# 10 itens, respondido por pais/cuidadores
# Pontuação: 1 ponto se resposta indica traço autístico
#   Itens onde "Concordo/Concordo Totalmente" = 1 ponto: 1, 5, 7, 9, 10
#   Itens onde "Discordo/Discordo Totalmente" = 1 ponto: 2, 3, 4, 6, 8
# Corte: ≥ 6 indica rastreio positivo

AQ10_CHILD_ITENS = [
    {"numero":  1, "texto": "A criança presta atenção em pequenos sons que os outros não notam",                       "direcao": "concordo"},
    {"numero":  2, "texto": "A criança costuma usar gestos espontaneamente ao falar",                                  "direcao": "discordo"},
    {"numero":  3, "texto": "A criança consegue se colocar no lugar dos outros facilmente",                            "direcao": "discordo"},
    {"numero":  4, "texto": "A criança gosta de encontros sociais e conversar com outras crianças",                    "direcao": "discordo"},
    {"numero":  5, "texto": "A criança tem dificuldade em entender as regras de conversação (vez de falar, pausas)",   "direcao": "concordo"},
    {"numero":  6, "texto": "A criança consegue perceber facilmente se alguém está ficando entediado",                 "direcao": "discordo"},
    {"numero":  7, "texto": "A criança gosta de colecionar coisas (brinquedos, objetos, listas)",                     "direcao": "concordo"},
    {"numero":  8, "texto": "A criança compreende o humor de piadas e brincadeiras facilmente",                       "direcao": "discordo"},
    {"numero":  9, "texto": "A criança tem interesses muito restritos e intensos",                                     "direcao": "concordo"},
    {"numero": 10, "texto": "A criança tem dificuldade em fazer amigos e interagir com crianças da mesma idade",       "direcao": "concordo"},
]

for item in AQ10_CHILD_ITENS:
    item["subescala"] = "total"
    item["reverso"] = False

AQ10_CHILD_SUBESCALAS = {
    "total": {"nome": "Pontuação Total", "itens": list(range(1, 11)), "cor": "#1A5276", "campo": "pont_total"},
}

AQ10_CHILD_OPCOES = [
    {"valor": 0, "label": "Discordo Totalmente"},
    {"valor": 1, "label": "Discordo"},
    {"valor": 2, "label": "Concordo"},
    {"valor": 3, "label": "Concordo Totalmente"},
]

AQ10_CHILD_CORTE = {
    "total": [
        ("Rastreio Negativo", 0,  5),
        ("Rastreio Positivo", 6, 10),
    ],
}
