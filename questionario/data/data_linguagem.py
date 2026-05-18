# Avaliação de Linguagem — Fonoaudiologia
# Escala: 0 = Ausente | 1 = Emergente | 2 = Presente

LINGUAGEM_DOMINIOS = [
    {
        "key": "recepcao", "nome": "Recepção / Compreensão", "campo": "pont_recepcao", "cor": "#3E73D1",
        "itens": [
            (1,  "Reage ao próprio nome"),
            (2,  "Segue instruções simples de 1 etapa (ex.: 'Pega o copo')"),
            (3,  "Segue instruções de 2 etapas (ex.: 'Pega o lápis e coloca na caixa')"),
            (4,  "Identifica objetos e figuras por nome"),
            (5,  "Compreende preposições espaciais básicas (em, sobre, embaixo, atrás)"),
            (6,  "Responde a perguntas simples (Quem? O quê? Onde?)"),
            (7,  "Compreende frases negativas e orações complexas"),
            (8,  "Acompanha história simples narrada sem apoio visual"),
        ],
    },
    {
        "key": "expressao", "nome": "Expressão Oral", "campo": "pont_expressao", "cor": "#27AE60",
        "itens": [
            (1,  "Produz sons, vocalizações ou palavras isoladas"),
            (2,  "Combina duas palavras com intenção comunicativa"),
            (3,  "Usa frases de 3 ou mais palavras"),
            (4,  "Nomeia objetos e pessoas do cotidiano"),
            (5,  "Relata experiências simples de forma espontânea"),
            (6,  "Usa pronomes pessoais corretamente (eu, você, ele)"),
            (7,  "Usa verbos conjugados em diferentes tempos"),
            (8,  "Articula um discurso coerente em situação de jogo simbólico"),
        ],
    },
    {
        "key": "pragmatica", "nome": "Pragmática", "campo": "pont_pragmatica", "cor": "#9B59B6",
        "itens": [
            (1,  "Mantém contato visual durante a comunicação"),
            (2,  "Inicia comunicação espontânea com o interlocutor"),
            (3,  "Toma turnos na conversa (espera sua vez de falar)"),
            (4,  "Usa linguagem para diferentes funções: pedir, informar, cumprimentar"),
            (5,  "Repara falhas de comunicação quando não é compreendido"),
            (6,  "Adapta o estilo de fala ao interlocutor (criança vs adulto)"),
            (7,  "Compreende e usa linguagem não-literal (ironia, humor)"),
        ],
    },
    {
        "key": "fonologia", "nome": "Fonologia / Articulação", "campo": "pont_fonologia", "cor": "#E67E22",
        "itens": [
            (1,  "Produz sons consonantais simples (/p/, /b/, /m/, /n/, /t/, /d/)"),
            (2,  "Produz sílabas e palavras com estrutura CV e VC"),
            (3,  "Produz sílabas complexas (CCV, CVC) sem omissões frequentes"),
            (4,  "Fala é inteligível para familiares (≥75% do tempo)"),
            (5,  "Fala é inteligível para desconhecidos (≥75% do tempo)"),
            (6,  "Apresenta ausência ou redução de processos fonológicos simplificatórios"),
        ],
    },
]

LINGUAGEM_OPCOES = [
    {"valor": 0, "label": "Ausente"},
    {"valor": 1, "label": "Emergente"},
    {"valor": 2, "label": "Presente"},
]
