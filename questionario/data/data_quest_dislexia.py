# Questionário de Dislexia (Pais) — Primeira Infância
# 4 subescalas, escala 0-3

QUEST_DISLEXIA_ITENS = [
    {"numero": 1,  "subescala": "linguagem_oral", "texto": "Apresentou atraso na fala (primeiras palavras após 18 meses)"},
    {"numero": 2,  "subescala": "linguagem_oral", "texto": "Tem dificuldade em pronunciar palavras longas ou complexas"},
    {"numero": 3,  "subescala": "linguagem_oral", "texto": "Confunde palavras parecidas (ex: fada/vada, bolo/polo)"},
    {"numero": 4,  "subescala": "linguagem_oral", "texto": "Tem dificuldade em aprender rimas e poesias"},
    {"numero": 5,  "subescala": "linguagem_oral", "texto": "Tem vocabulário reduzido para a idade"},
    {"numero": 6,  "subescala": "leitura_escrita", "texto": "Tem dificuldade em aprender o alfabeto"},
    {"numero": 7,  "subescala": "leitura_escrita", "texto": "Confunde letras parecidas (b/d, p/q, m/n)"},
    {"numero": 8,  "subescala": "leitura_escrita", "texto": "Lê muito devagar ou com muitos erros"},
    {"numero": 9,  "subescala": "leitura_escrita", "texto": "Perde a linha ao ler ou pula palavras/linhas"},
    {"numero": 10, "subescala": "leitura_escrita", "texto": "Tem caligrafia muito irregular ou ilegível"},
    {"numero": 11, "subescala": "leitura_escrita", "texto": "Comete muitos erros ortográficos mesmo após treino"},
    {"numero": 12, "subescala": "leitura_escrita", "texto": "Escreve letras ou números espelhados"},
    {"numero": 13, "subescala": "memoria", "texto": "Tem dificuldade em memorizar sequências (dias da semana, meses)"},
    {"numero": 14, "subescala": "memoria", "texto": "Esquece palavras conhecidas ao falar"},
    {"numero": 15, "subescala": "memoria", "texto": "Tem dificuldade em seguir instruções com várias etapas"},
    {"numero": 16, "subescala": "memoria", "texto": "Confunde direita e esquerda frequentemente"},
    {"numero": 17, "subescala": "atencao", "texto": "Tem dificuldade em manter atenção durante a leitura"},
    {"numero": 18, "subescala": "atencao", "texto": "Evita atividades que envolvam leitura ou escrita"},
    {"numero": 19, "subescala": "atencao", "texto": "Apresenta frustração ou ansiedade ao ler/escrever"},
    {"numero": 20, "subescala": "atencao", "texto": "Tem desempenho muito abaixo do esperado para a idade na leitura"},
]

QUEST_DISLEXIA_SUBESCALAS = {
    "linguagem_oral":  {"nome": "Linguagem Oral",   "cor": "#3498DB", "campo": "pont_linguagem_oral",  "itens": [1, 2, 3, 4, 5]},
    "leitura_escrita": {"nome": "Leitura e Escrita", "cor": "#E74C3C", "campo": "pont_leitura_escrita", "itens": [6, 7, 8, 9, 10, 11, 12]},
    "memoria":         {"nome": "Memória/Sequência", "cor": "#9B59B6", "campo": "pont_memoria",        "itens": [13, 14, 15, 16]},
    "atencao":         {"nome": "Atenção/Motivação", "cor": "#E67E22", "campo": "pont_atencao",        "itens": [17, 18, 19, 20]},
}

QUEST_DISLEXIA_OPCOES = [(0, "Nunca"), (1, "Às vezes"), (2, "Frequentemente"), (3, "Sempre")]
QUEST_DISLEXIA_CORTE = 2  # >= 2 por subescala = indicativo
