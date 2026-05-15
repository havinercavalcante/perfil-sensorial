# Habilidades Adaptativas (ABA) — Análise do Comportamento Aplicada
# Escala: 0 = Não faz | 1 = Faz com ajuda | 2 = Faz de forma independente

HABILIDADES_DOMINIOS = [
    {
        "key": "comunicacao", "nome": "Comunicação Funcional", "campo": "pont_comunicacao", "cor": "#3E73D1",
        "itens": [
            (1,  "Faz pedidos usando palavras, gestos ou figuras (PECS, CAA)"),
            (2,  "Expressa 'não' ou recusa de forma adequada"),
            (3,  "Usa cumprimentos (olá, tchau) de forma espontânea"),
            (4,  "Responde perguntas simples (nome, idade)"),
            (5,  "Pede ajuda quando precisa"),
            (6,  "Comenta ou compartilha informações espontaneamente"),
        ],
    },
    {
        "key": "autocuidado", "nome": "Autocuidado", "campo": "pont_autocuidado", "cor": "#27AE60",
        "itens": [
            (1,  "Come sozinho(a) com utensílios"),
            (2,  "Bebe em copo sem derramar"),
            (3,  "Usa o banheiro com independência (ou indica necessidade)"),
            (4,  "Lava as mãos sozinho(a)"),
            (5,  "Veste e despe roupas simples"),
            (6,  "Escova os dentes com supervisão mínima"),
        ],
    },
    {
        "key": "socializacao", "nome": "Socialização", "campo": "pont_socializacao", "cor": "#9B59B6",
        "itens": [
            (1,  "Responde quando chamado pelo nome"),
            (2,  "Mantém contato visual adequado durante interações"),
            (3,  "Brinca ao lado de outras crianças"),
            (4,  "Brinca de forma cooperativa com pares"),
            (5,  "Aguarda sua vez em jogos e atividades"),
            (6,  "Compartilha brinquedos ou materiais"),
        ],
    },
    {
        "key": "autonomia", "nome": "Autonomia / Independência", "campo": "pont_autonomia", "cor": "#E67E22",
        "itens": [
            (1,  "Segue rotinas estruturadas com mínima supervisão"),
            (2,  "Transita entre atividades sem crises frequentes"),
            (3,  "Permanece em atividade dirigida por período adequado à faixa etária"),
            (4,  "Organiza materiais ou pertences pessoais"),
            (5,  "Realiza deslocamentos seguros (casa, escola) com supervisão proporcional"),
            (6,  "Toma decisões simples de forma independente"),
        ],
    },
    {
        "key": "comportamento", "nome": "Comportamento Adaptativo", "campo": "pont_comportamento", "cor": "#E74C3C",
        "itens": [
            (1,  "Aceita 'não' sem crises prolongadas"),
            (2,  "Tolera frustrações com reações proporcionais"),
            (3,  "Solicita pausas ou expressa desconforto de forma adequada"),
            (4,  "Mantém comportamentos adequados em ambientes públicos"),
            (5,  "Generaliza habilidades aprendidas para novos contextos"),
            (6,  "Frequência de comportamentos autolesivos ou heteroagressivos é baixa ou ausente"),
        ],
    },
]

HABILIDADES_OPCOES = [
    {"valor": 0, "label": "Não faz"},
    {"valor": 1, "label": "Faz com ajuda"},
    {"valor": 2, "label": "Faz de forma independente"},
]
