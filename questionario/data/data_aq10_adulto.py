# AQ-10 Adulto — Autism Quotient 10-item screening version (Baron-Cohen, 2009)
# 10 itens, escala Likert 4 pontos
# Pontuação: 1 ponto se resposta indica traço autístico:
#   Itens onde "Concordo/Concordo Totalmente" = 1 ponto: 1, 7, 8, 10 (direção concordo)
#   Itens onde "Discordo/Discordo Totalmente" = 1 ponto: 2, 3, 4, 5, 6, 9 (direção discordo)
# Corte: ≥ 6 indica rastreio positivo

AQ10_ADULTO_ITENS = [
    {"numero":  1, "texto": "Eu noto com frequência pequenos sons que os outros não percebem",              "direcao": "concordo"},
    {"numero":  2, "texto": "Eu normalmente concentro-me mais no todo do que nos detalhes",                "direcao": "discordo"},
    {"numero":  3, "texto": "Acho fácil fazer duas coisas ao mesmo tempo",                                 "direcao": "discordo"},
    {"numero":  4, "texto": "Se há uma interrupção, posso voltar facilmente ao que estava fazendo",        "direcao": "discordo"},
    {"numero":  5, "texto": "Acho fácil 'ler nas entrelinhas' em conversas",                              "direcao": "discordo"},
    {"numero":  6, "texto": "Eu sei como dizer se alguém que está me ouvindo está ficando entediado",     "direcao": "discordo"},
    {"numero":  7, "texto": "Quando estou lendo uma história, tenho dificuldade em perceber as intenções dos personagens", "direcao": "concordo"},
    {"numero":  8, "texto": "Gosto de colecionar informações sobre categorias de coisas (ex.: tipos de carros, pássaros, trens, plantas)", "direcao": "concordo"},
    {"numero":  9, "texto": "Acho fácil perceber o que alguém está pensando ou sentindo, olhando para a expressão do rosto", "direcao": "discordo"},
    {"numero": 10, "texto": "Tenho dificuldade em entender a vez de falar em conversas",                  "direcao": "concordo"},
]

for item in AQ10_ADULTO_ITENS:
    item["subescala"] = "total"
    item["reverso"] = False

AQ10_ADULTO_SUBESCALAS = {
    "total": {"nome": "Pontuação Total", "itens": list(range(1, 11)), "cor": "#1A5276", "campo": "pont_total"},
}

AQ10_ADULTO_OPCOES = [
    {"valor": 0, "label": "Discordo Totalmente"},
    {"valor": 1, "label": "Discordo"},
    {"valor": 2, "label": "Concordo"},
    {"valor": 3, "label": "Concordo Totalmente"},
]

AQ10_ADULTO_CORTE = {
    "total": [
        ("Rastreio Negativo", 0,  5),
        ("Rastreio Positivo", 6, 10),
    ],
}
