# Protocolo Dislexia — Avaliação Escolar (Professor)
# 4 subescalas, escala 0-3

PROT_DISLEXIA_PROF_ITENS = [
    {"numero": 1,  "subescala": "leitura",     "texto": "O aluno lê abaixo do esperado para a série/ano"},
    {"numero": 2,  "subescala": "leitura",     "texto": "Comete erros de omissão (ex.: 'pato' por 'prato')"},
    {"numero": 3,  "subescala": "leitura",     "texto": "Comete erros de adição (ex.: 'palato' por 'pato')"},
    {"numero": 4,  "subescala": "leitura",     "texto": "Comete erros de inversão (ex.: 'pal' por 'lap')"},
    {"numero": 5,  "subescala": "leitura",     "texto": "Lê sem entonação ou fluência"},
    {"numero": 6,  "subescala": "leitura",     "texto": "Tem dificuldade em decodificar palavras novas/desconhecidas"},
    {"numero": 7,  "subescala": "escrita",     "texto": "Apresenta erros ortográficos frequentes"},
    {"numero": 8,  "subescala": "escrita",     "texto": "Omite, troca ou acrescenta letras ao escrever"},
    {"numero": 9,  "subescala": "escrita",     "texto": "Escreve letras espelhadas (b/d, p/q)"},
    {"numero": 10, "subescala": "escrita",     "texto": "Produção escrita é muito inferior ao nível de comunicação oral"},
    {"numero": 11, "subescala": "escrita",     "texto": "Tem dificuldade em copiar do quadro com precisão"},
    {"numero": 12, "subescala": "matematica",  "texto": "Comete erros em sequências numéricas"},
    {"numero": 13, "subescala": "matematica",  "texto": "Confunde sinais matemáticos (+, -, ×, ÷)"},
    {"numero": 14, "subescala": "matematica",  "texto": "Dificuldade em memorizar tabuada"},
    {"numero": 15, "subescala": "organizacao", "texto": "Dificuldade em organizar material escolar"},
    {"numero": 16, "subescala": "organizacao", "texto": "Perde objetos e esquece tarefas com frequência"},
    {"numero": 17, "subescala": "organizacao", "texto": "Dificuldade em seguir instruções orais em sala"},
    {"numero": 18, "subescala": "organizacao", "texto": "Rendimento escolar inconsistente (ora vai bem, ora muito mal)"},
]

PROT_DISLEXIA_PROF_SUBESCALAS = {
    "leitura":     {"nome": "Leitura",     "cor": "#E74C3C", "campo": "pont_leitura",    "itens": [1, 2, 3, 4, 5, 6]},
    "escrita":     {"nome": "Escrita",     "cor": "#3498DB", "campo": "pont_escrita",    "itens": [7, 8, 9, 10, 11]},
    "matematica":  {"nome": "Matemática",  "cor": "#9B59B6", "campo": "pont_matematica", "itens": [12, 13, 14]},
    "organizacao": {"nome": "Organização", "cor": "#E67E22", "campo": "pont_organizacao", "itens": [15, 16, 17, 18]},
}

PROT_DISLEXIA_PROF_OPCOES = [
    {"valor": 0, "label": "Nunca"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Frequentemente"},
    {"valor": 3, "label": "Sempre"},
]
PROT_DISLEXIA_PROF_CORTE = 2  # media >= 2 por subescala
