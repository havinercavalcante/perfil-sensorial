# Avaliação de Linguagem — Fonoaudiologia
# Escala: 0 = Nunca | 1 = Às vezes | 2 = Frequentemente | 3 = Sempre

LINGUAGEM_DOMINIOS = [
    {
        "key": "recepcao", "nome": "Recepção / Compreensão", "campo": "pont_recepcao", "cor": "#3E73D1",
        "itens": [
            (1,  "Reage ao próprio nome quando chamado"),
            (2,  "Segue instruções simples de 1 etapa (ex.: 'Pega o copo')"),
            (3,  "Segue instruções de 2 etapas sem apoio gestual"),
            (4,  "Identifica objetos e figuras por nome"),
            (5,  "Compreende preposições espaciais básicas (em, sobre, embaixo, atrás)"),
            (6,  "Responde a perguntas simples (Quem? O quê? Onde?)"),
            (7,  "Compreende frases negativas e orações com subordinadas"),
            (8,  "Acompanha história narrada sem apoio visual e responde perguntas sobre ela"),
        ],
    },
    {
        "key": "expressao", "nome": "Expressão Oral", "campo": "pont_expressao", "cor": "#27AE60",
        "itens": [
            (1,  "Produz sons, vocalizações ou palavras isoladas com intenção comunicativa"),
            (2,  "Combina duas palavras formando mini-frases (ex.: 'mais água')"),
            (3,  "Usa frases de 3 ou mais palavras com estrutura SVO"),
            (4,  "Nomeia objetos, pessoas e ações do cotidiano"),
            (5,  "Relata experiências passadas de forma espontânea"),
            (6,  "Usa pronomes pessoais corretamente (eu, você, ele/ela)"),
            (7,  "Conjuga verbos em diferentes tempos (presente, passado, futuro)"),
            (8,  "Produz narrativa coerente com início, meio e fim em situação de jogo"),
        ],
    },
    {
        "key": "pragmatica", "nome": "Pragmática", "campo": "pont_pragmatica", "cor": "#9B59B6",
        "itens": [
            (1,  "Mantém contato visual adequado durante a comunicação"),
            (2,  "Inicia comunicação espontânea com o interlocutor"),
            (3,  "Toma turnos na conversa (espera sua vez de falar)"),
            (4,  "Usa linguagem para diferentes funções: pedir, informar, negar, cumprimentar"),
            (5,  "Repara falhas de comunicação quando não é compreendido"),
            (6,  "Adapta o estilo de fala ao interlocutor (criança vs adulto)"),
            (7,  "Compreende e usa linguagem não-literal (ironia, humor, metáforas simples)"),
        ],
    },
    {
        "key": "fonologia", "nome": "Fonologia / Articulação", "campo": "pont_fonologia", "cor": "#E67E22",
        "itens": [
            (1,  "Produz sons consonantais simples (/p/, /b/, /m/, /n/, /t/, /d/)"),
            (2,  "Produz sílabas e palavras com estrutura CV e VC sem omissões"),
            (3,  "Produz sílabas complexas (CCV, CVC) sem simplificações frequentes"),
            (4,  "Fala inteligível para familiares em ≥ 75% do tempo"),
            (5,  "Fala inteligível para desconhecidos em ≥ 75% do tempo"),
            (6,  "Ausência ou redução significativa de processos fonológicos simplificatórios"),
        ],
    },
    {
        "key": "fluencia", "nome": "Fluência", "campo": "pont_fluencia", "cor": "#16A085",
        "itens": [
            (1,  "Fala com ritmo e velocidade adequados, sem pausas ou bloqueios frequentes"),
            (2,  "Não apresenta repetições de sons ou sílabas com esforço visivelmente aumentado"),
            (3,  "Não apresenta prolongamentos involuntários de sons"),
            (4,  "Não demonstra tensão muscular visível, tiques ou esquiva ao falar"),
            (5,  "Mantém fluência adequada em diferentes contextos (conversa espontânea, leitura, situações de pressão)"),
        ],
    },
    {
        "key": "consciencia_fono", "nome": "Consciência Fonológica", "campo": "pont_consciencia_fono", "cor": "#C0392B",
        "itens": [
            (1,  "Identifica e produz rimas (ex.: 'gato' rima com 'pato')"),
            (2,  "Segmenta palavras em sílabas (ex.: ba-ta-ta = 3 sílabas)"),
            (3,  "Identifica o som/sílaba inicial de palavras"),
            (4,  "Realiza supressão silábica (ex.: 'casa' sem /ca/ = 'sa')"),
            (5,  "Identifica fonemas individuais dentro de palavras"),
            (6,  "Realiza síntese fonêmica (junta /g/ /a/ /t/ /o/ = 'gato')"),
        ],
    },
]

LINGUAGEM_OPCOES = [
    {"valor": 0, "label": "Nunca"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Frequentemente"},
    {"valor": 3, "label": "Sempre"},
]

# Classificação por percentual de acerto em cada domínio
# Referência: critério clínico funcional (não normatizado por idade)
LINGUAGEM_CLASSIFICACAO = {
    "recepcao":        [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "expressao":       [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "pragmatica":      [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "fonologia":       [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "fluencia":        [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "consciencia_fono":[("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "total":           [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
}
