# Marcos de Desenvolvimento Infantil — Pediatria / Neuropediatria
# Escala: 0 = Não atingido | 1 = Em aquisição | 2 = Atingido

DESENVOLVIMENTO_DOMINIOS = [
    {
        "key": "motor_grosso", "nome": "Motor Grosso", "campo": "pont_motor_grosso", "cor": "#E74C3C",
        "itens": [
            (1,  "Sustenta a cabeça com firmeza"),
            (2,  "Rola de barriga para cima e de barriga para baixo"),
            (3,  "Senta-se sem apoio"),
            (4,  "Engatinha com alternância de braços e pernas"),
            (5,  "Fica em pé com apoio"),
            (6,  "Anda sem apoio"),
            (7,  "Sobe escadas com apoio"),
            (8,  "Corre sem cair com frequência"),
            (9,  "Pula com os dois pés"),
            (10, "Anda em superfícies irregulares com equilíbrio adequado"),
        ],
    },
    {
        "key": "motor_fino", "nome": "Motor Fino", "campo": "pont_motor_fino", "cor": "#3498DB",
        "itens": [
            (1,  "Abre e fecha as mãos intencionalmente"),
            (2,  "Transfere objetos de uma mão para outra"),
            (3,  "Usa pinça polegar-indicador"),
            (4,  "Empilha 3 ou mais cubos"),
            (5,  "Passa páginas de livros"),
            (6,  "Segura o lápis de forma funcional"),
            (7,  "Faz rabiscos e traços intencionais"),
            (8,  "Copia círculo ou linha horizontal"),
            (9,  "Usa tesoura com supervisão"),
            (10, "Escreve ou desenha figuras reconhecíveis"),
        ],
    },
    {
        "key": "linguagem", "nome": "Linguagem e Comunicação", "campo": "pont_linguagem", "cor": "#27AE60",
        "itens": [
            (1,  "Sorri de forma responsiva"),
            (2,  "Balbucia e produz sons variados"),
            (3,  "Usa mama/dada com intenção"),
            (4,  "Produz 3 ou mais palavras com significado"),
            (5,  "Combina 2 palavras espontaneamente"),
            (6,  "Usa frases de 3 ou mais palavras"),
            (7,  "Conta e relata experiências simples"),
            (8,  "Faz perguntas usando Quem, Por quê, Como"),
            (9,  "Mantém conversa com troca de turnos"),
            (10, "Fala é inteligível para desconhecidos"),
        ],
    },
    {
        "key": "social", "nome": "Social / Emocional", "campo": "pont_social", "cor": "#9B59B6",
        "itens": [
            (1,  "Mantém contato visual"),
            (2,  "Sorri para cuidadores"),
            (3,  "Demonstra angústia de separação"),
            (4,  "Brinca ao lado de outras crianças (jogo paralelo)"),
            (5,  "Brinca com outras crianças de forma cooperativa"),
            (6,  "Mostra empatia (consola quem está triste)"),
            (7,  "Aguarda sua vez em atividades ou brincadeiras"),
            (8,  "Resolve conflitos com pares sem agressão constante"),
        ],
    },
    {
        "key": "cognitivo", "nome": "Cognitivo / Adaptativo", "campo": "pont_cognitivo", "cor": "#E67E22",
        "itens": [
            (1,  "Busca objeto escondido (permanência do objeto)"),
            (2,  "Imita ações simples do cotidiano"),
            (3,  "Brincadeira simbólica / faz-de-conta"),
            (4,  "Identifica formas e cores básicas"),
            (5,  "Classifica objetos por categoria"),
            (6,  "Compreende sequência de eventos (antes/depois)"),
            (7,  "Resolve quebra-cabeças de 4 ou mais peças"),
            (8,  "Reconhece letras ou números do cotidiano"),
        ],
    },
]

DESENVOLVIMENTO_OPCOES = [
    {"valor": 0, "label": "Não atingido"},
    {"valor": 1, "label": "Em aquisição"},
    {"valor": 2, "label": "Atingido"},
]
