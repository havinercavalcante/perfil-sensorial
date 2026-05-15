# Triagem de Alimentação Seletiva — Fonoaudiologia / Pediatria
# Escala: 0 = Não / 1 = Às vezes / 2 = Sim (para itens positivos)
# Itens marcados com reverso=True: pontuação invertida (Sim=0, Não=2)

ALIMENTACAO_DOMINIOS = [
    {
        "key": "variedade", "nome": "Variedade Alimentar", "campo": "pont_variedade", "cor": "#27AE60",
        "itens": [
            (1,  "Aceita alimentos de diferentes grupos (proteínas, carboidratos, vegetais, frutas)", False),
            (2,  "Come mais de 20 alimentos diferentes", False),
            (3,  "Experimenta alimentos novos com alguma disposição", False),
            (4,  "Aceita variações de preparo (cozido, assado, cru) do mesmo alimento", False),
            (5,  "Mantém cardápio variado ao longo da semana", False),
        ],
    },
    {
        "key": "sensibilidade", "nome": "Sensibilidade Sensorial Alimentar", "campo": "pont_sensibilidade", "cor": "#E74C3C",
        "itens": [
            (1,  "Recusa alimentos por textura específica (cremoso, pegajoso, crocante)", True),
            (2,  "Recusa alimentos por cheiro", True),
            (3,  "Recusa alimentos apenas pela aparência (cor, formato)", True),
            (4,  "Apresenta reações de náusea ou engasgo a alimentos comuns", True),
            (5,  "Reage de forma intensa a novas sensações na boca", True),
        ],
    },
    {
        "key": "recusa_rituais", "nome": "Rituais e Recusa Alimentar", "campo": "pont_recusa_rituais", "cor": "#E67E22",
        "itens": [
            (1,  "Precisa que alimentos estejam separados no prato", True),
            (2,  "Exige sempre o mesmo prato, utensílio ou local", True),
            (3,  "Apresenta crises comportamentais na hora das refeições", True),
            (4,  "Come apenas alimentos de marcas específicas", True),
            (5,  "Recusa alimento se parecer diferente do habitual (forma, embalagem)", True),
        ],
    },
    {
        "key": "motricidade_oral", "nome": "Motricidade Oral", "campo": "pont_motricidade_oral", "cor": "#3498DB",
        "itens": [
            (1,  "Mastiga eficientemente alimentos de consistências variadas", False),
            (2,  "Mantém alimentos na boca sem derramar", False),
            (3,  "Realiza movimentos laterais de língua durante a mastigação", False),
            (4,  "Coordena mastigação e deglutição de forma eficiente", False),
            (5,  "Não apresenta resíduos alimentares excessivos na boca após engolir", False),
        ],
    },
    {
        "key": "degluticao", "nome": "Deglutição", "campo": "pont_degluticao", "cor": "#9B59B6",
        "itens": [
            (1,  "Engole líquidos sem engasgos ou tosse", False),
            (2,  "Engole pastosos sem engasgos ou tosse", False),
            (3,  "Engole sólidos sem engasgos ou tosse", False),
            (4,  "Não há relato de voz molhada após as refeições", False),
            (5,  "Não há histórico de pneumonias de repetição sugestivas de aspiração", False),
        ],
    },
]

ALIMENTACAO_OPCOES = [
    {"valor": 0, "label": "Não"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Sim"},
]
