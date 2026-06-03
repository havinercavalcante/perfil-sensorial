# Triagem de Risco de Suicídio — baseada no Columbia Protocol (C-SSRS)
# Itens Yes/No. Itens 1-6 ideação; 7-10 comportamento.
RISCO_SUICIDIO_ITENS = [
    {"numero": 1, "texto": "Você já desejou estar morto(a) ou que pudesse dormir e não acordar?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 2, "texto": "Você já teve pensamentos de se matar?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 3, "texto": "Você já pensou em como poderia se matar?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 4, "texto": "Você já teve intenção de agir sobre esses pensamentos ou sentiu alguma urgência em se matar?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 5, "texto": "Você já tomou alguma atitude para se preparar para se matar (ex: juntar comprimidos, pesquisar meios)?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 6, "texto": "Você alguma vez se feriu intencionalmente sem querer morrer (ex: se cortou, queimou)?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 7, "texto": "Você já tentou se matar?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 8, "texto": "Você pensa nisso atualmente (na última semana)?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
    {"numero": 9, "texto": "Existe algum fator de proteção que impeça esses pensamentos (família, religião, planos futuros)?",
     "opcoes": [{"valor": 1, "label": "Não"}, {"valor": 0, "label": "Sim"}]},
    {"numero": 10, "texto": "Você tem acesso a meios letais (armas, medicamentos em grandes quantidades)?",
     "opcoes": [{"valor": 0, "label": "Não"}, {"valor": 1, "label": "Sim"}]},
]
RISCO_SUICIDIO_CORTE = [
    ("Baixo risco",      0, 2),
    ("Risco moderado",   3, 5),
    ("Risco elevado",    6, 8),
    ("Risco muito alto", 9, 10),
]