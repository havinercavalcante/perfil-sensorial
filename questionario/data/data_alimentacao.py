# Triagem de Alimentação Seletiva — Fonoaudiologia / Pediatria
# Referências: EBAI/Montreal CHF Feeding Scale (validação BR 2021), Pedi-EAT,
#              BAMBI, ARFID (DSM-5), Sensory Profile (Dunn) — seção oral
# Escala: 0 = Nunca | 1 = Às vezes | 2 = Frequentemente | 3 = Sempre
# Todos os itens têm polaridade positiva (maior pontuação = melhor desempenho)

ALIMENTACAO_DOMINIOS = [
    {
        "key": "variedade",
        "nome": "Variedade Alimentar",
        "campo": "pont_variedade",
        "cor": "#27AE60",
        "itens": [
            (1,  "Come alimentos de pelo menos três grupos alimentares (proteínas, carboidratos, vegetais ou frutas)", False),
            (2,  "Aceita pelo menos 20 alimentos diferentes na dieta habitual", False),
            (3,  "Experimenta alimentos novos quando oferecidos, mesmo que não consuma toda a porção", False),
            (4,  "Aceita variações no preparo do mesmo alimento (cozido, assado, cru)", False),
            (5,  "Mantém cardápio variado ao longo da semana", False),
            (6,  "Aceita alimentos de cores diferentes (verde, laranja, vermelho, amarelo)", False),
            (7,  "Demonstra interesse em experimentar o que outras pessoas ao redor estão comendo", False),
        ],
    },
    {
        "key": "sensibilidade",
        "nome": "Tolerância Sensorial",
        "campo": "pont_sensibilidade",
        "cor": "#E74C3C",
        "itens": [
            (1,  "Aceita alimentos de diferentes texturas (macio, crocante, pegajoso, granulado)", False),
            (2,  "Tolera diferentes consistências no mesmo prato sem recusar a refeição", False),
            (3,  "Aceita alimentos com cheiros mais intensos (peixe, alho, temperos)", False),
            (4,  "Tolera variações de temperatura nos alimentos (frio, morno, quente)", False),
            (5,  "Não demonstra reações exageradas de nojo diante de alimentos comuns", False),
            (6,  "Aceita alimentos sem recusar apenas pela cor ou aparência visual", False),
            (7,  "Não apresenta engasgo ou náusea ao contato com textura ou sabor novo", False),
        ],
    },
    {
        "key": "recusa_rituais",
        "nome": "Comportamento nas Refeições",
        "campo": "pont_recusa_rituais",
        "cor": "#E67E22",
        "itens": [
            (1,  "Senta-se à mesa e permanece durante a refeição sem crises comportamentais", False),
            (2,  "Aceita o mesmo alimento servido em diferentes apresentações ou embalagens", False),
            (3,  "Tolera ter alimentos encostados ou misturados no prato", False),
            (4,  "A hora das refeições transcorre sem conflitos intensos com frequência", False),
            (5,  "Aceita refeições em locais ou com utensílios diferentes dos habituais", False),
            (6,  "Não exige marcas, formatos ou embalagens específicas de forma rígida", False),
        ],
    },
    {
        "key": "interesse_apetite",
        "nome": "Interesse e Apetite",
        "campo": "pont_interesse",
        "cor": "#F39C12",
        "itens": [
            (1,  "Demonstra fome nos horários regulares de refeição", False),
            (2,  "Finaliza porções adequadas para a faixa etária", False),
            (3,  "Demonstra prazer ou satisfação durante as refeições", False),
            (4,  "Solicita ou indica alimentos quando está com fome", False),
            (5,  "Come quantidade suficiente para manter crescimento adequado", False),
            (6,  "Não precisa ser convencido, distraído ou entretido para se alimentar", False),
        ],
    },
    {
        "key": "motricidade_oral",
        "nome": "Motricidade Orofacial",
        "campo": "pont_motricidade_oral",
        "cor": "#3498DB",
        "itens": [
            (1,  "Mastiga alimentos sólidos de forma eficiente, sem esforço excessivo", False),
            (2,  "Realiza movimentos laterais de língua durante a mastigação", False),
            (3,  "Não deixa resíduos alimentares excessivos na boca após engolir", False),
            (4,  "Mantém alimentos dentro da boca sem derramar pela comissura labial", False),
            (5,  "Aceita e mastiga alimentos de consistência mais firme (cenoura crua, biscoito)", False),
            (6,  "Mantém os lábios fechados durante a mastigação a maior parte do tempo", False),
        ],
    },
    {
        "key": "degluticao",
        "nome": "Deglutição e Segurança",
        "campo": "pont_degluticao",
        "cor": "#9B59B6",
        "itens": [
            (1,  "Engole líquidos sem engasgos ou tosse", False),
            (2,  "Engole pastosos e semissólidos sem engasgos ou tosse", False),
            (3,  "Engole sólidos sem engasgos ou tosse", False),
            (4,  "Não apresenta voz molhada ou rouca após as refeições", False),
            (5,  "Sem histórico de pneumonias de repetição sugestivas de aspiração silente", False),
        ],
    },
]

ALIMENTACAO_OPCOES = [
    {"valor": 0, "label": "Nunca"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Frequentemente"},
    {"valor": 3, "label": "Sempre"},
]

ALIMENTACAO_CLASSIFICACAO = {
    "variedade":         [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "sensibilidade":     [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "recusa_rituais":    [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "interesse_apetite": [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "motricidade_oral":  [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "degluticao":        [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "total":             [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
}
