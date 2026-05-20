# Triagem de Voz Infantil — Fonoaudiologia / Voz
# Referências: pVHI — Pediatric Voice Handicap Index (Zur et al., 2007),
#              adaptação brasileira (Ribeiro et al., 2014)
# Escala: 0 = Nunca | 1 = Às vezes | 2 = Frequentemente | 3 = Sempre
# Todos os itens têm polaridade positiva (maior pontuação = melhor desempenho)

VOZ_INFANTIL_DOMINIOS = [
    {
        "key": "funcional",
        "nome": "Impacto Funcional",
        "campo": "pont_funcional",
        "cor": "#3E73D1",
        "itens": [
            (1,  "A voz da criança é ouvida com clareza pelos interlocutores em situações habituais", False),
            (2,  "A criança é compreendida em ambientes com ruído de fundo (sala de aula, refeitório)", False),
            (3,  "A criança não precisa repetir o que disse para ser compreendida com frequência", False),
            (4,  "A voz permite participação plena em atividades escolares e sociais", False),
            (5,  "A voz não limita a comunicação da criança em nenhuma situação do dia a dia", False),
            (6,  "A criança consegue falar no volume adequado para o contexto sem dificuldade", False),
            (7,  "A voz não leva a criança a evitar situações de comunicação", False),
            (8,  "A qualidade vocal é consistente ao longo do dia, sem variações importantes", False),
        ],
    },
    {
        "key": "fisico",
        "nome": "Aspectos Físicos",
        "campo": "pont_fisico",
        "cor": "#E67E22",
        "itens": [
            (1,  "A criança não precisa pigarrear ou tossir durante ou após falar", False),
            (2,  "A voz não apresenta cansaço ou fadiga após períodos de conversa", False),
            (3,  "A voz não apresenta rouquidão ou aspereza perceptível", False),
            (4,  "A voz não some, falha ou quebra de forma inesperada durante a fala", False),
            (5,  "A criança não relata desconforto, dor ou sensação estranha na garganta ao falar", False),
            (6,  "A voz soa da mesma forma todos os dias, sem variações inexplicáveis", False),
            (7,  "A criança não demonstra esforço ou tensão para produzir a voz", False),
            (8,  "A voz não apresenta fadiga ao final do dia após uso habitual", False),
        ],
    },
    {
        "key": "emocional",
        "nome": "Impacto Emocional",
        "campo": "pont_emocional",
        "cor": "#9B59B6",
        "itens": [
            (1,  "A criança não demonstra vergonha ou constrangimento relacionado à sua voz", False),
            (2,  "A criança não fica angustiada quando alguém faz comentários sobre a sua voz", False),
            (3,  "A voz não é fonte de estresse emocional para a criança", False),
            (4,  "A criança fala com confiança em grupos, sem hesitação por causa da voz", False),
            (5,  "A voz não afeta negativamente a autoestima ou autoimagem da criança", False),
            (6,  "A criança não demonstra relutância em falar em público ou em sala de aula", False),
            (7,  "Os responsáveis não demonstram preocupação frequente com a qualidade vocal da criança", False),
        ],
    },
]

VOZ_INFANTIL_OPCOES = [
    {"valor": 0, "label": "Nunca"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Frequentemente"},
    {"valor": 3, "label": "Sempre"},
]

VOZ_INFANTIL_CLASSIFICACAO = {
    "funcional":  [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "fisico":     [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "emocional":  [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "total":      [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
}
