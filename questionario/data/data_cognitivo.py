# Rastreio Cognitivo — Neuropsicologia / Neuropediatria
# Escala: 0 = Comprometido | 1 = Limítrofe / Inconsistente | 2 = Preservado

COGNITIVO_DOMINIOS = [
    {
        "key": "atencao_sustentada", "nome": "Atenção Sustentada", "campo": "pont_atencao_sustentada", "cor": "#3E73D1",
        "itens": [
            (1,  "Mantém foco em tarefa de longa duração (≥ 10 min) sem desvio frequente"),
            (2,  "Realiza leitura ou escuta de texto sem perder o fio"),
            (3,  "Acompanha instruções verbais sequenciais"),
            (4,  "Permanece em jogo ou atividade estruturada por período adequado"),
        ],
    },
    {
        "key": "atencao_seletiva", "nome": "Atenção Seletiva", "campo": "pont_atencao_seletiva", "cor": "#E74C3C",
        "itens": [
            (1,  "Filtra distrações ambientais durante tarefas"),
            (2,  "Detecta estímulo-alvo em tarefa com distrações (ex.: encontrar figura em meio a outras)"),
            (3,  "Mantém foco mesmo em ambiente barulhento ou visualmente poluído"),
            (4,  "Retoma foco rapidamente após interrupção externa"),
        ],
    },
    {
        "key": "memoria_trabalho", "nome": "Memória de Trabalho", "campo": "pont_memoria_trabalho", "cor": "#27AE60",
        "itens": [
            (1,  "Segue instruções de 2 etapas sem precisar de repetição"),
            (2,  "Repete série de dígitos ou palavras em ordem direta e inversa"),
            (3,  "Realiza cálculos mentais simples"),
            (4,  "Mantém informação em mente enquanto executa outra tarefa simultânea"),
        ],
    },
    {
        "key": "memoria_episodica", "nome": "Memória Episódica", "campo": "pont_memoria_episodica", "cor": "#9B59B6",
        "itens": [
            (1,  "Recorda eventos recentes com detalhes adequados"),
            (2,  "Lembra de informações aprendidas na sessão anterior"),
            (3,  "Recorda sequência de eventos de uma história"),
            (4,  "Retém informações novas após período de espera (30 min)"),
        ],
    },
    {
        "key": "funcoes_executivas", "nome": "Funções Executivas", "campo": "pont_funcoes_executivas", "cor": "#E67E22",
        "itens": [
            (1,  "Planeja passos para resolver problema simples"),
            (2,  "Inibe resposta impulsiva quando necessário"),
            (3,  "Alterna entre regras ou categorias com flexibilidade"),
            (4,  "Monitora e corrige erros durante a execução de tarefas"),
            (5,  "Organiza materiais e tempo para completar atividade"),
        ],
    },
    {
        "key": "visoespacial", "nome": "Habilidades Visoespaciais", "campo": "pont_visoespacial", "cor": "#E91E8C",
        "itens": [
            (1,  "Copia figuras geométricas simples com precisão"),
            (2,  "Completa quebra-cabeça com orientação espacial adequada"),
            (3,  "Reconhece e reproduz padrões visuais"),
            (4,  "Navega em espaços conhecidos sem se perder"),
        ],
    },
]

COGNITIVO_OPCOES = [
    {"valor": 0, "label": "Comprometido"},
    {"valor": 1, "label": "Limítrofe / Inconsistente"},
    {"valor": 2, "label": "Preservado"},
]
