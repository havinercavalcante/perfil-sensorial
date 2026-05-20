# Índice de Desvantagem Vocal — 10 itens (IDV-10 / VHI-10)
# Referências: VHI-10 — Voice Handicap Index (Rosen et al., 2004),
#              IDV-10 — adaptação brasileira (Behlau et al., 2011)
# Aplicação: autorrelato para adolescentes e adultos; relato de responsável para crianças
# Escala: 0 = Nunca | 1 = Às vezes | 2 = Frequentemente | 3 = Sempre
# Todos os itens têm polaridade positiva (maior pontuação = melhor desempenho)

IDV10_DOMINIOS = [
    {
        "key": "comunicativo",
        "nome": "Impacto Comunicativo",
        "campo": "pont_comunicativo",
        "cor": "#C0392B",
        "itens": [
            (1,  "A voz é ouvida com facilidade pelos interlocutores em situações habituais de comunicação", False),
            (2,  "Sou compreendido(a) sem precisar repetir o que disse", False),
            (3,  "A voz permite o uso normal do telefone, videochamadas e demais meios de comunicação", False),
            (4,  "A voz não limita atividades sociais, profissionais ou escolares", False),
            (5,  "Consigo participar plenamente de conversas sem restrições causadas pela voz", False),
        ],
    },
    {
        "key": "fisico",
        "nome": "Aspectos Físicos e Orgânicos",
        "campo": "pont_fisico",
        "cor": "#8E44AD",
        "itens": [
            (1,  "Não sinto ressecamento, irritação ou desconforto na garganta ao falar", False),
            (2,  "A voz não apresenta cansaço ou fadiga ao longo do dia com o uso habitual", False),
            (3,  "A voz não some, falha ou quebra de forma inesperada durante a fala", False),
            (4,  "Não sinto esforço físico ou tensão ao produzir a voz", False),
            (5,  "A qualidade vocal é consistente e estável, sem necessidade de esforço para mantê-la", False),
        ],
    },
]

IDV10_OPCOES = [
    {"valor": 0, "label": "Nunca"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Frequentemente"},
    {"valor": 3, "label": "Sempre"},
]

IDV10_CLASSIFICACAO = {
    "comunicativo": [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "fisico":       [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "total":        [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
}
