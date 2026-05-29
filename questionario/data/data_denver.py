# Denver II — Checklist de Desenvolvimento Infantil
# 4 domínios: pessoal_social, motor_fino, linguagem, motor_grosseiro
# Cada item: Passa (1), Falha (0), Não testado (None)

DENVER_ITENS = [
    # Pessoal-Social
    {"numero": 1,  "dominio": "pessoal_social", "texto": "Sorriso responsivo", "faixa": "0-2 meses"},
    {"numero": 2,  "dominio": "pessoal_social", "texto": "Reconhece a mãe/cuidador", "faixa": "1-3 meses"},
    {"numero": 3,  "dominio": "pessoal_social", "texto": "Sorri espontaneamente", "faixa": "1-3 meses"},
    {"numero": 4,  "dominio": "pessoal_social", "texto": "Brinca com mãos", "faixa": "2-4 meses"},
    {"numero": 5,  "dominio": "pessoal_social", "texto": "Sorri para o espelho", "faixa": "3-6 meses"},
    {"numero": 6,  "dominio": "pessoal_social", "texto": "Come biscoito sozinho", "faixa": "4-8 meses"},
    {"numero": 7,  "dominio": "pessoal_social", "texto": "Brinca de esconde-esconde (objeto)", "faixa": "6-10 meses"},
    {"numero": 8,  "dominio": "pessoal_social", "texto": "Bate palmas / tchau-tchau", "faixa": "7-12 meses"},
    {"numero": 9,  "dominio": "pessoal_social", "texto": "Bebe no copo com ajuda", "faixa": "9-14 meses"},
    {"numero": 10, "dominio": "pessoal_social", "texto": "Imita atividades domésticas", "faixa": "12-18 meses"},
    {"numero": 11, "dominio": "pessoal_social", "texto": "Usa colher/garfo", "faixa": "14-20 meses"},
    {"numero": 12, "dominio": "pessoal_social", "texto": "Tira peça de roupa", "faixa": "18-24 meses"},
    {"numero": 13, "dominio": "pessoal_social", "texto": "Lava e seca as mãos", "faixa": "20-30 meses"},
    {"numero": 14, "dominio": "pessoal_social", "texto": "Veste-se com supervisão", "faixa": "3-4 anos"},
    {"numero": 15, "dominio": "pessoal_social", "texto": "Brinca em grupo com outras crianças", "faixa": "3-5 anos"},
    # Motor Fino-Adaptativo
    {"numero": 16, "dominio": "motor_fino", "texto": "Acompanha objeto com os olhos (180°)", "faixa": "1-3 meses"},
    {"numero": 17, "dominio": "motor_fino", "texto": "Agarra objetos por 1 segundo", "faixa": "2-4 meses"},
    {"numero": 18, "dominio": "motor_fino", "texto": "Leva objeto à boca", "faixa": "3-6 meses"},
    {"numero": 19, "dominio": "motor_fino", "texto": "Pega objeto com preensão palmar", "faixa": "4-7 meses"},
    {"numero": 20, "dominio": "motor_fino", "texto": "Pega com polegar e indicador (pinça)", "faixa": "8-12 meses"},
    {"numero": 21, "dominio": "motor_fino", "texto": "Bate dois cubos um no outro", "faixa": "8-13 meses"},
    {"numero": 22, "dominio": "motor_fino", "texto": "Coloca cubos em recipiente", "faixa": "10-14 meses"},
    {"numero": 23, "dominio": "motor_fino", "texto": "Rabisca espontaneamente", "faixa": "12-18 meses"},
    {"numero": 24, "dominio": "motor_fino", "texto": "Torre de 2 cubos", "faixa": "13-18 meses"},
    {"numero": 25, "dominio": "motor_fino", "texto": "Torre de 4 cubos", "faixa": "16-22 meses"},
    {"numero": 26, "dominio": "motor_fino", "texto": "Torre de 8 cubos", "faixa": "20-30 meses"},
    {"numero": 27, "dominio": "motor_fino", "texto": "Imita linha vertical", "faixa": "24-36 meses"},
    {"numero": 28, "dominio": "motor_fino", "texto": "Copia círculo", "faixa": "3-4 anos"},
    {"numero": 29, "dominio": "motor_fino", "texto": "Desenha pessoa com 3 partes", "faixa": "3-5 anos"},
    {"numero": 30, "dominio": "motor_fino", "texto": "Copia cruz (+)", "faixa": "4-5 anos"},
    # Linguagem
    {"numero": 31, "dominio": "linguagem", "texto": "Reage a som (vira a cabeça)", "faixa": "0-2 meses"},
    {"numero": 32, "dominio": "linguagem", "texto": "Vocaliza (não-choro)", "faixa": "1-3 meses"},
    {"numero": 33, "dominio": "linguagem", "texto": "Ri alto", "faixa": "2-5 meses"},
    {"numero": 34, "dominio": "linguagem", "texto": "Volta-se para a voz", "faixa": "3-6 meses"},
    {"numero": 35, "dominio": "linguagem", "texto": "Balbucia (ba, da, ga)", "faixa": "4-8 meses"},
    {"numero": 36, "dominio": "linguagem", "texto": "Imita sons da fala", "faixa": "6-10 meses"},
    {"numero": 37, "dominio": "linguagem", "texto": "Papai / mamãe (inespecífico)", "faixa": "7-11 meses"},
    {"numero": 38, "dominio": "linguagem", "texto": "1 palavra com significado", "faixa": "10-14 meses"},
    {"numero": 39, "dominio": "linguagem", "texto": "3 palavras diferentes", "faixa": "11-16 meses"},
    {"numero": 40, "dominio": "linguagem", "texto": "6 palavras diferentes", "faixa": "14-20 meses"},
    {"numero": 41, "dominio": "linguagem", "texto": "Combina 2 palavras", "faixa": "16-24 meses"},
    {"numero": 42, "dominio": "linguagem", "texto": "Aponta 2 figuras nomeadas", "faixa": "18-28 meses"},
    {"numero": 43, "dominio": "linguagem", "texto": "Usa frases de 3 palavras", "faixa": "24-36 meses"},
    {"numero": 44, "dominio": "linguagem", "texto": "Diz seu próprio nome e sobrenome", "faixa": "2-3 anos"},
    {"numero": 45, "dominio": "linguagem", "texto": "Conta uma história simples", "faixa": "4-5 anos"},
    # Motor Grosseiro
    {"numero": 46, "dominio": "motor_grosseiro", "texto": "Levanta a cabeça (prono)", "faixa": "0-2 meses"},
    {"numero": 47, "dominio": "motor_grosseiro", "texto": "Sustenta a cabeça em 90°", "faixa": "1-4 meses"},
    {"numero": 48, "dominio": "motor_grosseiro", "texto": "Rola de prono para supino", "faixa": "2-5 meses"},
    {"numero": 49, "dominio": "motor_grosseiro", "texto": "Senta com apoio", "faixa": "3-6 meses"},
    {"numero": 50, "dominio": "motor_grosseiro", "texto": "Senta sem apoio", "faixa": "5-8 meses"},
    {"numero": 51, "dominio": "motor_grosseiro", "texto": "Fica em pé com apoio", "faixa": "6-10 meses"},
    {"numero": 52, "dominio": "motor_grosseiro", "texto": "Engatinha", "faixa": "6-11 meses"},
    {"numero": 53, "dominio": "motor_grosseiro", "texto": "Fica em pé sozinho", "faixa": "9-13 meses"},
    {"numero": 54, "dominio": "motor_grosseiro", "texto": "Anda sozinho", "faixa": "10-15 meses"},
    {"numero": 55, "dominio": "motor_grosseiro", "texto": "Sobe escadas com apoio", "faixa": "12-18 meses"},
    {"numero": 56, "dominio": "motor_grosseiro", "texto": "Corre", "faixa": "14-24 meses"},
    {"numero": 57, "dominio": "motor_grosseiro", "texto": "Sobe escadas alternando os pés", "faixa": "2-3 anos"},
    {"numero": 58, "dominio": "motor_grosseiro", "texto": "Pula com os dois pés", "faixa": "2-3 anos"},
    {"numero": 59, "dominio": "motor_grosseiro", "texto": "Anda na ponta dos pés", "faixa": "2-4 anos"},
    {"numero": 60, "dominio": "motor_grosseiro", "texto": "Equilibra-se em 1 pé por 2 segundos", "faixa": "3-5 anos"},
]

DENVER_DOMINIOS = {
    "pessoal_social":  {"nome": "Pessoal-Social",         "cor": "#E74C3C", "campo": "pont_pessoal_social"},
    "motor_fino":      {"nome": "Motor Fino-Adaptativo",  "cor": "#3498DB", "campo": "pont_motor_fino"},
    "linguagem":       {"nome": "Linguagem",               "cor": "#27AE60", "campo": "pont_linguagem"},
    "motor_grosseiro": {"nome": "Motor Grosseiro",         "cor": "#E67E22", "campo": "pont_motor_grosseiro"},
}

DENVER_OPCOES = [
    (1,    "Passa (P)"),
    (0,    "Falha (F)"),
    (None, "Não testado (NT)"),
]
