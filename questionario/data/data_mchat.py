# M-CHAT-R — Modified Checklist for Autism in Toddlers, Revised (2013)
# Faixa etária: 16–30 meses | Respondente: pais/cuidadores
# risco_sim=True → resposta SIM é item de risco (pontua 1)
# risco_sim=False → resposta NÃO é item de risco (pontua 1)

MCHAT_ITENS = [
    {
        "numero":  1,
        "texto":   "Se você aponta para algo do outro lado do quarto, seu filho(a) olha para lá?",
        "detalhe": "Por exemplo: se você aponta para um brinquedo ou animal, seu filho(a) olha para o brinquedo ou o animal?",
        "risco_sim": False,
    },
    {
        "numero":  2,
        "texto":   "Você já se perguntou se seu filho(a) pode ser surdo(a)?",
        "detalhe": "",
        "risco_sim": True,
    },
    {
        "numero":  3,
        "texto":   "Seu filho(a) brinca de faz-de-conta?",
        "detalhe": "Por exemplo: finge que fala ao telefone, cuida de uma boneca como se fosse um bebê de verdade, ou faz de conta que bebe de um copo vazio?",
        "risco_sim": False,
    },
    {
        "numero":  4,
        "texto":   "Seu filho(a) gosta de subir nas coisas?",
        "detalhe": "Por exemplo: móveis, brinquedos ou escadas.",
        "risco_sim": False,
    },
    {
        "numero":  5,
        "texto":   "Seu filho(a) faz movimentos incomuns com os dedos perto dos olhos?",
        "detalhe": "Por exemplo: balança os dedos perto dos olhos.",
        "risco_sim": True,
    },
    {
        "numero":  6,
        "texto":   "Seu filho(a) aponta com o dedo indicador para pedir alguma coisa ou pedir ajuda?",
        "detalhe": "Por exemplo: aponta para um biscoito ou brinquedo que está fora de alcance.",
        "risco_sim": False,
    },
    {
        "numero":  7,
        "texto":   "Seu filho(a) aponta com o dedo indicador para mostrar algo interessante para você?",
        "detalhe": "Por exemplo: aponta para um avião no céu ou um caminhão grande na rua.",
        "risco_sim": False,
    },
    {
        "numero":  8,
        "texto":   "Seu filho(a) se interessa por outras crianças?",
        "detalhe": "Por exemplo: observa outras crianças, sorri para elas ou vai até elas.",
        "risco_sim": False,
    },
    {
        "numero":  9,
        "texto":   "Seu filho(a) mostra coisas para você, trazendo-as ou levantando-as para você ver — não para pedir ajuda, mas apenas para compartilhar?",
        "detalhe": "Por exemplo: mostra uma flor, um bicho de pelúcia ou um caminhão de brinquedo.",
        "risco_sim": False,
    },
    {
        "numero": 10,
        "texto":   "Seu filho(a) responde quando você chama pelo nome dele(a)?",
        "detalhe": "Por exemplo: olha para você, fala ou balbucia, ou para o que está fazendo.",
        "risco_sim": False,
    },
    {
        "numero": 11,
        "texto":   "Quando você sorri para seu filho(a), ele(a) sorri de volta?",
        "detalhe": "",
        "risco_sim": False,
    },
    {
        "numero": 12,
        "texto":   "Seu filho(a) fica perturbado(a) por barulhos do dia a dia?",
        "detalhe": "Por exemplo: fica com raiva ou chora com aspirador de pó, música alta ou crianças chorando.",
        "risco_sim": True,
    },
    {
        "numero": 13,
        "texto":   "Seu filho(a) anda?",
        "detalhe": "",
        "risco_sim": False,
    },
    {
        "numero": 14,
        "texto":   "Seu filho(a) olha nos seus olhos quando você fala com ele(a), brinca com ele(a) ou veste-o/a?",
        "detalhe": "",
        "risco_sim": False,
    },
    {
        "numero": 15,
        "texto":   "Seu filho(a) tenta imitar o que você faz?",
        "detalhe": "Por exemplo: acenar adeus, bater palmas ou fazer um barulhinho engraçado.",
        "risco_sim": False,
    },
    {
        "numero": 16,
        "texto":   "Se você vira a cabeça para olhar para alguma coisa, seu filho(a) olha ao redor para ver o que você está olhando?",
        "detalhe": "",
        "risco_sim": False,
    },
    {
        "numero": 17,
        "texto":   "Seu filho(a) tenta fazer com que você olhe para ele(a)?",
        "detalhe": "Por exemplo: olha para você em busca de elogio ou diz 'Olha!' quando está fazendo algo.",
        "risco_sim": False,
    },
    {
        "numero": 18,
        "texto":   "Seu filho(a) entende quando você pede para ele(a) fazer alguma coisa?",
        "detalhe": "Por exemplo: se você disser 'Coloca o livro aqui' ou 'Me traz o cobertor' sem apontar, ele/ela entende?",
        "risco_sim": False,
    },
    {
        "numero": 19,
        "texto":   "Quando algo novo acontece, seu filho(a) olha para o seu rosto para ver como você reage?",
        "detalhe": "Por exemplo: se ele/ela ouve um barulho estranho ou vê um brinquedo novo.",
        "risco_sim": False,
    },
    {
        "numero": 20,
        "texto":   "Seu filho(a) gosta de atividades com movimento?",
        "detalhe": "Por exemplo: ser balançado no colo ou ficar pulando no joelho.",
        "risco_sim": False,
    },
]

# Classificação de risco pelo score total (0–20)
MCHAT_RISCO = [
    ("baixo",  "Baixo Risco",  0, 2,  "Nenhuma ação adicional necessária, a não ser que a triagem indique risco."),
    ("medio",  "Médio Risco",  3, 7,  "Recomenda-se aplicar o M-CHAT-R/F (entrevista de acompanhamento)."),
    ("alto",   "Alto Risco",   8, 20, "Encaminhar imediatamente para avaliação diagnóstica de autismo."),
]
