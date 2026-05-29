# Checklist de Dislexia — Triagem Sim/Não
# 3 subescalas, Sim=1 / Não=0
# Corte: total >= 7 = rastreio positivo

CHECKLIST_DISLEXIA_ITENS = [
    {"numero": 1,  "subescala": "leitura",       "texto": "Lê mais devagar que os colegas da mesma idade"},
    {"numero": 2,  "subescala": "leitura",       "texto": "Omite, substitui ou inverte letras ao ler"},
    {"numero": 3,  "subescala": "leitura",       "texto": "Perde o fio ao ler (volta à mesma linha ou pula linhas)"},
    {"numero": 4,  "subescala": "leitura",       "texto": "Lê palavras por partes sem conseguir decodificar o todo"},
    {"numero": 5,  "subescala": "leitura",       "texto": "Tem dificuldade em compreender o que leu"},
    {"numero": 6,  "subescala": "leitura",       "texto": "Evita ler em voz alta"},
    {"numero": 7,  "subescala": "leitura",       "texto": "Confunde letras visualmente parecidas (b/d, p/q)"},
    {"numero": 8,  "subescala": "leitura",       "texto": "Precisa de muito esforço para ler textos curtos"},
    {"numero": 9,  "subescala": "escrita",       "texto": "Caligrafia irregular ou letras de tamanhos diferentes"},
    {"numero": 10, "subescala": "escrita",       "texto": "Omite letras ou sílabas ao escrever"},
    {"numero": 11, "subescala": "escrita",       "texto": "Escreve letras ou palavras espelhadas"},
    {"numero": 12, "subescala": "escrita",       "texto": "Comete muitos erros ortográficos mesmo em palavras frequentes"},
    {"numero": 13, "subescala": "escrita",       "texto": "Produção escrita muito abaixo do nível verbal"},
    {"numero": 14, "subescala": "escrita",       "texto": "Dificuldade em organizar ideias por escrito"},
    {"numero": 15, "subescala": "escrita",       "texto": "Copia muito devagar do quadro ou do livro"},
    {"numero": 16, "subescala": "processamento", "texto": "Dificuldade em segmentar palavras em sílabas"},
    {"numero": 17, "subescala": "processamento", "texto": "Dificuldade em identificar rimas"},
    {"numero": 18, "subescala": "processamento", "texto": "Dificuldade em manipular sons dentro das palavras"},
    {"numero": 19, "subescala": "processamento", "texto": "Confusão com conceitos de direita/esquerda"},
    {"numero": 20, "subescala": "processamento", "texto": "Dificuldade em automatizar sequências (alfabeto, tabuada)"},
]

CHECKLIST_DISLEXIA_SUBESCALAS = {
    "leitura":       {"nome": "Leitura",                 "cor": "#E74C3C", "campo": "pont_leitura",       "itens": list(range(1, 9))},
    "escrita":       {"nome": "Escrita",                 "cor": "#3498DB", "campo": "pont_escrita",       "itens": list(range(9, 16))},
    "processamento": {"nome": "Processamento Fonológico", "cor": "#27AE60", "campo": "pont_processamento", "itens": list(range(16, 21))},
}

CHECKLIST_DISLEXIA_OPCOES = [(1, "Sim"), (0, "Não")]
CHECKLIST_DISLEXIA_CORTE = 7  # total >= 7 = rastreio positivo
