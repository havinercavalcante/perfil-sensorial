# Avaliação de Comportamento Funcional (ABA)
# Escala: 0 = Nunca / 1 = Às vezes / 2 = Frequentemente / Com consistência

COMPORTAMENTO_DOMINIOS = [
    {
        "key": "iniciacao", "nome": "Iniciação de Tarefa", "campo": "pont_iniciacao", "cor": "#3E73D1",
        "itens": [
            (1,  "Inicia tarefas após instrução verbal sem necessidade de prompts físicos"),
            (2,  "Inicia atividades preferidas de forma espontânea"),
            (3,  "Busca materiais necessários para iniciar uma atividade"),
            (4,  "Retoma tarefa após breve interrupção"),
            (5,  "Inicia atividades não-preferidas com mínima resistência"),
        ],
    },
    {
        "key": "manutencao", "nome": "Manutenção de Tarefa", "campo": "pont_manutencao", "cor": "#27AE60",
        "itens": [
            (1,  "Mantém atenção em tarefas estruturadas por período adequado à faixa etária"),
            (2,  "Completa tarefas de curta duração (até 5 minutos) de forma independente"),
            (3,  "Completa tarefas de maior duração (5–15 minutos) com supervisão mínima"),
            (4,  "Resiste a distrações durante a execução de tarefas"),
            (5,  "Pede ajuda quando encontra dificuldade, sem abandonar a tarefa"),
        ],
    },
    {
        "key": "flexibilidade", "nome": "Flexibilidade / Transições", "campo": "pont_flexibilidade", "cor": "#E67E22",
        "itens": [
            (1,  "Tolera mudanças na rotina com reação proporcional"),
            (2,  "Transita entre atividades ao sinal de aviso (5 minutos antes)"),
            (3,  "Aceita substituição de atividade preferida por outra"),
            (4,  "Adapta-se a novos ambientes ou profissionais sem crise prolongada"),
            (5,  "Tolera erros ou resultados diferentes do esperado"),
        ],
    },
    {
        "key": "generalizacao", "nome": "Generalização", "campo": "pont_generalizacao", "cor": "#9B59B6",
        "itens": [
            (1,  "Aplica habilidades aprendidas em sessão para contextos naturais"),
            (2,  "Mantém habilidades com diferentes profissionais e cuidadores"),
            (3,  "Generaliza habilidades para diferentes locais (casa, escola, clínica)"),
            (4,  "Usa habilidades com materiais ou pistas variadas"),
            (5,  "Mantém habilidades após período sem prática (manutenção)"),
        ],
    },
    {
        "key": "comunicacao", "nome": "Comunicação Funcional em Contexto", "campo": "pont_comunicacao", "cor": "#3E73D1",
        "itens": [
            (1,  "Usa comunicação funcional para evitar ou encerrar situações aversivas"),
            (2,  "Solicita pausa de forma adequada antes de atingir o limiar de tolerância"),
            (3,  "Expressa preferências entre opções apresentadas"),
            (4,  "Sinaliza dor, mal-estar ou cansaço de forma compreensível"),
            (5,  "Pede atenção ou interação de forma socialmente adequada"),
        ],
    },
    {
        "key": "autocontrole", "nome": "Autocontrole e Regulação", "campo": "pont_autocontrole", "cor": "#E74C3C",
        "itens": [
            (1,  "Usa estratégias de autorregulação (respiração, afastamento) com suporte"),
            (2,  "Frequência de comportamentos autolesivos é baixa ou ausente"),
            (3,  "Frequência de crises de agressão é baixa ou ausente"),
            (4,  "Reage de forma proporcional a frustrações"),
            (5,  "Retoma estado regulado após episódio de desregulação em tempo razoável"),
        ],
    },
]

COMPORTAMENTO_OPCOES = [
    {"valor": 0, "label": "Nunca"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Frequentemente / Com consistência"},
]
