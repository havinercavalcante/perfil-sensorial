# Avaliação Psicopedagógica — Psicopedagogia
# Escala: 0 = Dificuldade significativa | 1 = Dificuldade leve / Em desenvolvimento | 2 = Adequado

PSICOPEDAGOGICA_DOMINIOS = [
    {
        "key": "leitura", "nome": "Leitura", "campo": "pont_leitura", "cor": "#3E73D1",
        "itens": [
            (1,  "Reconhece letras do alfabeto"),
            (2,  "Decodifica sílabas simples (CV: ma, pe, ti)"),
            (3,  "Lê palavras isoladas com compreensão"),
            (4,  "Lê frases curtas com fluidez"),
            (5,  "Compreende textos simples após leitura silenciosa"),
            (6,  "Leitura em voz alta é fluente e expressiva"),
        ],
    },
    {
        "key": "escrita", "nome": "Escrita", "campo": "pont_escrita", "cor": "#27AE60",
        "itens": [
            (1,  "Copia palavras do quadro ou cartão com precisão"),
            (2,  "Escreve palavras simples por ditado"),
            (3,  "Produz frases simples espontaneamente"),
            (4,  "Apresenta ortografia adequada para o nível escolar"),
            (5,  "Organiza texto com início, meio e fim"),
            (6,  "Caligrafia é legível"),
        ],
    },
    {
        "key": "matematica", "nome": "Matemática", "campo": "pont_matematica", "cor": "#E74C3C",
        "itens": [
            (1,  "Reconhece e escreve números"),
            (2,  "Realiza contagem com correspondência um a um"),
            (3,  "Executa adições e subtrações simples"),
            (4,  "Executa multiplicação e divisão adequadas ao nível escolar"),
            (5,  "Resolve problemas matemáticos contextualizados"),
            (6,  "Compreende conceitos de medida, tempo e dinheiro"),
        ],
    },
    {
        "key": "atencao_escolar", "nome": "Atenção Escolar", "campo": "pont_atencao_escolar", "cor": "#9B59B6",
        "itens": [
            (1,  "Mantém atenção durante explicações do professor"),
            (2,  "Copia do quadro em tempo hábil"),
            (3,  "Completa tarefas em sala sem precisar de apoio constante"),
            (4,  "Revisa e corrige erros nas próprias atividades"),
            (5,  "Segue instruções escritas sem auxílio verbal"),
        ],
    },
    {
        "key": "comportamento", "nome": "Comportamento Escolar", "campo": "pont_comportamento", "cor": "#E67E22",
        "itens": [
            (1,  "Interage adequadamente com professores e colegas"),
            (2,  "Aguarda sua vez para falar ou realizar atividades"),
            (3,  "Aceita regras e limites do ambiente escolar"),
            (4,  "Lida com frustrações (notas, erros) de forma proporcional"),
            (5,  "Demonstra motivação e interesse nas atividades escolares"),
        ],
    },
]

PSICOPEDAGOGICA_OPCOES = [
    {"valor": 0, "label": "Dificuldade significativa"},
    {"valor": 1, "label": "Em desenvolvimento / Dificuldade leve"},
    {"valor": 2, "label": "Adequado para o nível escolar"},
]
