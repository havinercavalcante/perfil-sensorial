# AUDIT — Alcohol Use Disorders Identification Test (WHO, 1992)
AUDIT_ITENS = [
    {"numero": 1, "texto": "Com que frequência você toma bebidas alcoólicas?",
     "opcoes": [{"valor": 0, "label": "Nunca"}, {"valor": 1, "label": "Mensalmente ou menos"}, {"valor": 2, "label": "De 2 a 4 vezes por mês"}, {"valor": 3, "label": "De 2 a 3 vezes por semana"}, {"valor": 4, "label": "4 vezes ou mais por semana"}]},
    {"numero": 2, "texto": "Quantas doses você costuma tomar em um dia normal?",
     "opcoes": [{"valor": 0, "label": "1 ou 2"}, {"valor": 1, "label": "3 ou 4"}, {"valor": 2, "label": "5 ou 6"}, {"valor": 3, "label": "7 a 9"}, {"valor": 4, "label": "10 ou mais"}]},
    {"numero": 3, "texto": "Com que frequência você toma 6 doses ou mais em uma ocasião?",
     "opcoes": [{"valor": 0, "label": "Nunca"}, {"valor": 1, "label": "Menos de uma vez por mês"}, {"valor": 2, "label": "Mensalmente"}, {"valor": 3, "label": "Semanalmente"}, {"valor": 4, "label": "Todo dia ou quase todo dia"}]},
    {"numero": 4, "texto": "Com que frequência, no último ano, você achou que não conseguia parar de beber depois de começar?",
     "opcoes": [{"valor": 0, "label": "Nunca"}, {"valor": 1, "label": "Menos de uma vez por mês"}, {"valor": 2, "label": "Mensalmente"}, {"valor": 3, "label": "Semanalmente"}, {"valor": 4, "label": "Todo dia ou quase todo dia"}]},
    {"numero": 5, "texto": "Com que frequência, no último ano, você deixou de fazer o que era esperado por causa do álcool?",
     "opcoes": [{"valor": 0, "label": "Nunca"}, {"valor": 1, "label": "Menos de uma vez por mês"}, {"valor": 2, "label": "Mensalmente"}, {"valor": 3, "label": "Semanalmente"}, {"valor": 4, "label": "Todo dia ou quase todo dia"}]},
    {"numero": 6, "texto": "Com que frequência, no último ano, precisou beber de manhã para poder se sentir bem?",
     "opcoes": [{"valor": 0, "label": "Nunca"}, {"valor": 1, "label": "Menos de uma vez por mês"}, {"valor": 2, "label": "Mensalmente"}, {"valor": 3, "label": "Semanalmente"}, {"valor": 4, "label": "Todo dia ou quase todo dia"}]},
    {"numero": 7, "texto": "Com que frequência, no último ano, você se sentiu culpado(a) após beber?",
     "opcoes": [{"valor": 0, "label": "Nunca"}, {"valor": 1, "label": "Menos de uma vez por mês"}, {"valor": 2, "label": "Mensalmente"}, {"valor": 3, "label": "Semanalmente"}, {"valor": 4, "label": "Todo dia ou quase todo dia"}]},
    {"numero": 8, "texto": "Com que frequência, no último ano, você não conseguiu lembrar o que aconteceu na noite anterior por causa do álcool?",
     "opcoes": [{"valor": 0, "label": "Nunca"}, {"valor": 1, "label": "Menos de uma vez por mês"}, {"valor": 2, "label": "Mensalmente"}, {"valor": 3, "label": "Semanalmente"}, {"valor": 4, "label": "Todo dia ou quase todo dia"}]},
    {"numero": 9, "texto": "Você ou alguém já se machucou por causa do seu comportamento ao beber?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 2, "label": "Sim, mas não no último ano"}, {"valor": 4, "label": "Sim, no último ano"}]},
    {"numero": 10, "texto": "Algum parente, amigo, médico ou profissional de saúde já demonstrou preocupação com o seu consumo de álcool?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 2, "label": "Sim, mas não no último ano"}, {"valor": 4, "label": "Sim, no último ano"}]},
]
AUDIT_CORTE = [
    ("Baixo risco",       0,  7),
    ("Uso nocivo",        8, 15),
    ("Provável dependência", 16, 19),
    ("Dependência grave", 20, 40),
]