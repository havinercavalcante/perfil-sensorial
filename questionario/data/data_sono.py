# Avaliação de Sono Infantil — Pediatria / Neuropediatria
# Baseada em BEARS / CSHQ (adaptação clínica)
# Escala: 1 = Nunca | 2 = Às vezes (1–2×/semana) | 3 = Frequentemente (3+×/semana)
# Score mais alto = mais dificuldades

SONO_DOMINIOS = [
    {
        "key": "inicio", "nome": "Início do Sono", "campo": "pont_inicio", "cor": "#3E73D1",
        "itens": [
            (1,  "A criança tem dificuldade para adormecer no horário adequado"),
            (2,  "A criança demora mais de 30 minutos para adormecer após deitar"),
            (3,  "A criança precisa de presença de adulto para adormecer"),
            (4,  "A criança pede água, comida ou mais atenção ao deitar"),
        ],
    },
    {
        "key": "manutencao", "nome": "Manutenção do Sono", "campo": "pont_manutencao", "cor": "#9B59B6",
        "itens": [
            (1,  "A criança acorda mais de uma vez por noite"),
            (2,  "A criança tem dificuldade para voltar a dormir depois de acordar"),
            (3,  "A criança vai para a cama dos pais durante a noite"),
            (4,  "A criança apresenta movimentos excessivos durante o sono"),
        ],
    },
    {
        "key": "sonolencia", "nome": "Sonolência Diurna", "campo": "pont_sonolencia", "cor": "#E67E22",
        "itens": [
            (1,  "A criança está com sono excessivo durante o dia"),
            (2,  "A criança dorme no carro ou em outros locais além do quarto"),
            (3,  "A criança tem dificuldade de acordar de manhã"),
            (4,  "A criança está irritada ou de mau humor por cansaço"),
        ],
    },
    {
        "key": "resistencia", "nome": "Resistência ao Sono", "campo": "pont_resistencia", "cor": "#E74C3C",
        "itens": [
            (1,  "A criança se recusa a ir para a cama no horário combinado"),
            (2,  "A criança tem dificuldade em seguir a rotina noturna"),
            (3,  "A criança chora ou faz birra ao ser colocada na cama"),
            (4,  "A criança sai repetidamente da cama depois de ser colocada para dormir"),
        ],
    },
    {
        "key": "ansiedade", "nome": "Ansiedade do Sono", "campo": "pont_ansiedade", "cor": "#27AE60",
        "itens": [
            (1,  "A criança tem medo de dormir sozinha"),
            (2,  "A criança tem pesadelos frequentes"),
            (3,  "A criança acorda gritando ou assustada (terror noturno)"),
            (4,  "A criança tem medo do escuro ou de monstros"),
        ],
    },
    {
        "key": "ronco_apneia", "nome": "Ronco / Respiração", "campo": "pont_ronco_apneia", "cor": "#E91E8C",
        "itens": [
            (1,  "A criança ronca alto durante o sono"),
            (2,  "A criança parece parar de respirar durante o sono"),
            (3,  "A criança respira pela boca durante o sono"),
            (4,  "A criança range os dentes durante o sono (bruxismo)"),
        ],
    },
]

SONO_OPCOES = [
    {"valor": 1, "label": "Nunca"},
    {"valor": 2, "label": "Às vezes (1–2×/semana)"},
    {"valor": 3, "label": "Frequentemente (3+×/semana)"},
]

SONO_TOTAL_MAX = 72   # 6 domínios × 4 itens × 3 pontos
