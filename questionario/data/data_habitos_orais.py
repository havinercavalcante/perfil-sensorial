# Triagem de Hábitos Orais — Fonoaudiologia / Motricidade Orofacial
# Referências: Protocolo MBGR (Marchesan, Berretin-Felix, Genaro, Rehder),
#              OPT (Oral Placement Therapy), avaliação clínica de MOF
# Escala: 0 = Nunca | 1 = Às vezes | 2 = Frequentemente | 3 = Sempre
# Todos os itens têm polaridade positiva (maior pontuação = melhor desempenho)

HABITOS_ORAIS_DOMINIOS = [
    {
        "key": "respiracao",
        "nome": "Respiração Nasal",
        "campo": "pont_respiracao",
        "cor": "#3498DB",
        "itens": [
            (1,  "Respira predominantemente pelo nariz, inclusive durante atividades cotidianas", False),
            (2,  "Mantém a boca fechada durante o repouso (sentado, assistindo TV, etc.)", False),
            (3,  "Apresenta lábios com aspecto hidratado, sem ressecamento ou fissuras frequentes", False),
            (4,  "Mantém postura de boca fechada ao dormir, sem boca aberta observada pelos responsáveis", False),
            (5,  "Não apresenta ronco ou ruído respiratório perceptível durante o sono", False),
            (6,  "A passagem nasal parece desobstruída, sem queixas frequentes de nariz entupido", False),
        ],
    },
    {
        "key": "succao",
        "nome": "Sucção Não-Nutritiva",
        "campo": "pont_succao",
        "cor": "#E74C3C",
        "itens": [
            (1,  "A chupeta foi abandonada na faixa etária adequada (até 2 anos de idade)", False),
            (2,  "Não apresenta hábito de sucção de dedo ou dedos atualmente", False),
            (3,  "Não apresenta hábito de morder ou sugar objetos, brinquedos ou roupas", False),
            (4,  "Os hábitos de sucção não-nutritiva foram completamente abandonados", False),
            (5,  "Não há alterações dentárias ou oclusais aparentes associadas a hábitos de sucção", False),
        ],
    },
    {
        "key": "mastigacao",
        "nome": "Mastigação",
        "campo": "pont_mastigacao",
        "cor": "#27AE60",
        "itens": [
            (1,  "Realiza mastigação bilateral alternada, utilizando ambos os lados da boca", False),
            (2,  "Mastiga com a boca fechada, sem exposição dos alimentos", False),
            (3,  "Mastiga por tempo adequado antes de engolir, sem pressa excessiva", False),
            (4,  "Aceita e mastiga alimentos de diferentes texturas (macio, firme, crocante)", False),
            (5,  "Não apresenta preferência exclusiva por alimentos pastosos ou líquidos", False),
            (6,  "Não deixa resíduo alimentar excessivo na boca ou ao redor dos lábios após as refeições", False),
        ],
    },
    {
        "key": "degluticao",
        "nome": "Padrão de Deglutição",
        "campo": "pont_degluticao",
        "cor": "#9B59B6",
        "itens": [
            (1,  "Engole com os lábios fechados e em contato", False),
            (2,  "Não apresenta interposição de língua entre os dentes durante a deglutição", False),
            (3,  "Não apresenta tensão muscular facial visível (bochechas, queixo) ao engolir", False),
            (4,  "Engole de forma silenciosa, sem ruído perceptível", False),
            (5,  "Bebe líquidos sem derramamento excessivo pelos cantos da boca", False),
        ],
    },
    {
        "key": "postura",
        "nome": "Postura e Bruxismo",
        "campo": "pont_postura",
        "cor": "#E67E22",
        "itens": [
            (1,  "Apresenta tônus labial adequado, com vedamento dos lábios em repouso sem esforço", False),
            (2,  "Não apresenta relato de ranger ou apertar os dentes (bruxismo)", False),
            (3,  "Não apresenta hábito de roer unhas ou morder objetos de forma recorrente", False),
            (4,  "Não apresenta salivação excessiva ou escape de saliva após os 3 anos de idade", False),
            (5,  "Mantém vedamento labial adequado durante o repouso sem necessidade de esforço aparente", False),
        ],
    },
]

HABITOS_ORAIS_OPCOES = [
    {"valor": 0, "label": "Nunca"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Frequentemente"},
    {"valor": 3, "label": "Sempre"},
]

HABITOS_ORAIS_CLASSIFICACAO = {
    "respiracao":  [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "succao":      [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "mastigacao":  [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "degluticao":  [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "postura":     [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "total":       [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
}
