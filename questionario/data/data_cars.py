# CARS-2 — Childhood Autism Rating Scale, 2ª edição (Schopler, 2010)
# 15 itens, escala 1–4 (com meios pontos: 1 / 1.5 / 2 / 2.5 / 3 / 3.5 / 4)
# Score total: <30 = Sem Autismo | 30–36.5 = Leve-Moderado | ≥37 = Grave

CARS_ITENS = [
    {
        "numero": 1, "titulo": "Relação com as Pessoas",
        "niveis": {
            1:   "Sem evidência de dificuldade — comportamento e atitudes adequados para a situação.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — ocasionalmente evita contato visual, prefere ficar sozinho, responde apenas quando muito estimulado.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — frequentemente distante, pode se irritar ao ser tocado ou ter contato.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — raramente ou nunca responde à presença ou ao contato humano.",
        },
    },
    {
        "numero": 2, "titulo": "Imitação",
        "niveis": {
            1:   "Imita sons, palavras e ações facilmente e de modo adequado para a faixa etária.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — imita a maior parte do tempo, mas pode necessitar de estímulo adicional.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — imita apenas às vezes; frequentemente precisa de ajuda e insistência.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — raramente ou nunca imita sons, palavras ou movimentos.",
        },
    },
    {
        "numero": 3, "titulo": "Resposta Emocional",
        "niveis": {
            1:   "Resposta emocional adequada ao tipo e grau da situação.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — respostas emocionais discretamente inapropriadas.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — respostas claramente inapropriadas; reações exageradas ou ausentes.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — quase nenhuma resposta emocional adequada.",
        },
    },
    {
        "numero": 4, "titulo": "Uso do Corpo",
        "niveis": {
            1:   "Movimentos dentro do padrão normal para a faixa etária.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — alguns maneirismos ou movimentos estereotipados, leves e ocasionais.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — maneirismos ou movimentos estereotipados frequentes.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — movimentos estereotipados quase constantes; muito difícil de redirecionar.",
        },
    },
    {
        "numero": 5, "titulo": "Uso de Objetos (Interesse e Persistência)",
        "niveis": {
            1:   "Brinca com brinquedos de modo adequado, variado e criativo para a faixa etária.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — leve preocupação com objetos; uso um tanto incomum.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — interesse intenso em objetos específicos ou uso inapropriado.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — interesse exclusivo e persistente; explora objetos de modo extremamente inadequado.",
        },
    },
    {
        "numero": 6, "titulo": "Adaptação a Mudanças (Resistência à Rotina)",
        "niveis": {
            1:   "Aceita mudanças prontamente; sem resistência incomum.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — pode ficar inquieto quando as rotinas são alteradas.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — fica perturbado ao perceber mudanças; difícil de reconfortar.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — resistência intensa e prolongada a qualquer mudança de rotina.",
        },
    },
    {
        "numero": 7, "titulo": "Resposta Visual",
        "niveis": {
            1:   "Usa a visão de modo normal e consistente para explorar o ambiente.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — pode evitar contato visual ou ser fascinado por certas imagens.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — frequentemente deve ser estimulado a olhar para objetos.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — evita olhar; olha para objetos de ângulos incomuns.",
        },
    },
    {
        "numero": 8, "titulo": "Resposta Auditiva",
        "niveis": {
            1:   "Resposta auditiva adequada para o tipo e grau do som.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — pode ignorar sons ocasionalmente ou ter reação leve.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — reage de modo diverso ao mesmo som; ou super ou sub-rresponsivo.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — não reage ou apresenta reações exageradas de modo consistente.",
        },
    },
    {
        "numero": 9, "titulo": "Uso e Resposta ao Paladar, Olfato e Tato",
        "niveis": {
            1:   "Explora paladar, olfato e tato de modo normal para a faixa etária.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — leve preocupação com exploração via paladar, olfato e tato.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — pode cheirar ou lamber objetos; toque de pele inapropriado.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — preocupação intensa; explora via paladar/olfato/tato de modo muito inadequado.",
        },
    },
    {
        "numero": 10, "titulo": "Medo ou Ansiedade",
        "niveis": {
            1:   "Comportamento de medo ou ansiedade normal para a faixa etária e situação.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — medo ou ansiedade discretamente mais ou menos intenso que o esperado.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — medos que persistem mesmo com reasseguramento.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — medo ou ansiedade extremamente intensos e muito difíceis de reassegurar.",
        },
    },
    {
        "numero": 11, "titulo": "Comunicação Verbal",
        "niveis": {
            1:   "Fala normal e adequada para a faixa etária e situação.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — ecolalia leve, palavras incomuns ou jargão.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — fala ausente ou com ecolalia frequente; pouca função comunicativa.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — fala ausente ou com mínima função comunicativa.",
        },
    },
    {
        "numero": 12, "titulo": "Comunicação Não-Verbal",
        "niveis": {
            1:   "Usa comunicação não-verbal de modo normal para a faixa etária.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — uso impreciso de gestos; pode apontar de modo ineficiente.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — raramente usa gestos para comunicar necessidades.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — raramente ou nunca usa gestos ou expressões faciais comunicativas.",
        },
    },
    {
        "numero": 13, "titulo": "Nível de Atividade",
        "niveis": {
            1:   "Nível de atividade adequado para a faixa etária e contexto.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — ligeiramente hiperativo ou hipoativo em alguns momentos.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — pode ser difícil de redirecionar para atividades.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — nível de atividade extremamente inapropriado; muito difícil de controlar.",
        },
    },
    {
        "numero": 14, "titulo": "Nível e Consistência da Resposta Intelectual",
        "niveis": {
            1:   "Funcionamento intelectual consistente e dentro do esperado para a faixa etária.",
            1.5: "Leve (próximo ao normal).",
            2:   "Levemente anormal — algumas áreas abaixo do esperado; leve inconsistência.",
            2.5: "Moderado-leve.",
            3:   "Moderadamente anormal — inconsistências evidentes entre habilidades.",
            3.5: "Moderado-grave.",
            4:   "Gravemente anormal — inconsistências marcadas; habilidades específicas com déficits acentuados.",
        },
    },
    {
        "numero": 15, "titulo": "Impressão Geral",
        "niveis": {
            1:   "Não apresenta sintomas de autismo; funcionamento dentro do esperado.",
            1.5: "Leve (próximo ao normal).",
            2:   "Sintomas de autismo leves; discretamente fora do padrão típico.",
            2.5: "Moderado-leve.",
            3:   "Sintomas de autismo moderados; claramente atípico em vários aspectos.",
            3.5: "Moderado-grave.",
            4:   "Sintomas de autismo graves; perfil atípico em múltiplos aspectos.",
        },
    },
]

CARS_OPCOES = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]

# Classificação pelo score total (soma dos 15 itens)
CARS_CLASSIFICACAO = [
    ("sem_autismo",   "Sem Autismo",              0.0,  29.9, "#27AE60"),
    ("leve_moderado", "Autismo Leve-Moderado",    30.0, 36.5, "#E67E22"),
    ("grave",         "Autismo Grave",            37.0, 60.0, "#E74C3C"),
]
