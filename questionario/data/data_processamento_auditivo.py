# Triagem de Processamento Auditivo Central — Fonoaudiologia / Audiologia
# Referências: FAPC-BR — Questionário de Avaliação do Processamento Auditivo Central (versão BR),
#              Fisher's Auditory Problems Checklist (Fisher, 1976),
#              Checklist do Processamento Auditivo (Pereira, 1997)
# Escala: 0 = Nunca | 1 = Às vezes | 2 = Frequentemente | 3 = Sempre
# Todos os itens têm polaridade positiva (maior pontuação = melhor desempenho)

AUDITIVO_DOMINIOS = [
    {
        "key": "atencao",
        "nome": "Atenção e Discriminação Auditiva",
        "campo": "pont_atencao",
        "cor": "#3E73D1",
        "itens": [
            (1,  "Responde ao próprio nome quando chamado em volume habitual de voz", False),
            (2,  "Mantém atenção a instruções verbais até o final sem se distrair com facilidade", False),
            (3,  "Distingue sons semelhantes na fala (ex.: p/b, d/t, f/v) de forma adequada para a idade", False),
            (4,  "Segue instruções auditivas em ambientes silenciosos sem necessidade de repetição", False),
            (5,  "Identifica corretamente sons familiares do ambiente (telefone, sino, buzina)", False),
            (6,  "Ouve e compreende adequadamente em contextos de baixo ruído ambiental", False),
        ],
    },
    {
        "key": "compreensao",
        "nome": "Compreensão Auditiva",
        "campo": "pont_compreensao",
        "cor": "#27AE60",
        "itens": [
            (1,  "Compreende e executa instruções orais de uma etapa sem apoio visual", False),
            (2,  "Compreende e executa sequências de 2 a 3 instruções orais encadeadas", False),
            (3,  "Compreende histórias contadas oralmente de forma adequada para a idade", False),
            (4,  "Entende explicações verbais sem necessitar de suporte visual ou demonstração", False),
            (5,  "Retém informações verbais suficientes para responder perguntas sobre o que ouviu", False),
            (6,  "Compreende a linguagem oral nos contextos esperados para sua faixa etária", False),
        ],
    },
    {
        "key": "memoria",
        "nome": "Memória Auditiva",
        "campo": "pont_memoria",
        "cor": "#9B59B6",
        "itens": [
            (1,  "Lembra sequências verbais aprendidas oralmente (dias da semana, meses, sequências numéricas)", False),
            (2,  "Recorda instruções dadas verbalmente para executá-las posteriormente", False),
            (3,  "Mantém informações verbais na memória até a conclusão de uma tarefa", False),
            (4,  "Recorda o conteúdo de histórias contadas oralmente pouco tempo após ouvir", False),
            (5,  "Recupera informações dadas verbalmente no início do dia ou da aula", False),
        ],
    },
    {
        "key": "figura_fundo",
        "nome": "Figura-Fundo e Localização",
        "campo": "pont_figura_fundo",
        "cor": "#E67E22",
        "itens": [
            (1,  "Compreende a fala em ambientes com ruído de fundo (sala de aula, refeitório, rua)", False),
            (2,  "Identifica corretamente a direção e a fonte de sons no ambiente", False),
            (3,  "Acompanha conversas em grupo sem perder o fio da comunicação", False),
            (4,  "Consegue focar em uma voz específica em meio a outras vozes ou sons", False),
            (5,  "Direciona atenção ao estímulo auditivo relevante ignorando os distratores sonoros", False),
        ],
    },
    {
        "key": "impacto",
        "nome": "Impacto Escolar e Social",
        "campo": "pont_impacto",
        "cor": "#E74C3C",
        "itens": [
            (1,  "Desempenha-se adequadamente em atividades orais na escola (leitura em voz alta, rodas de conversa)", False),
            (2,  "Não necessita que instruções sejam repetidas para compreender e executar tarefas", False),
            (3,  "Acompanha o conteúdo apresentado oralmente em sala de aula sem dificuldades perceptíveis", False),
            (4,  "Participa de atividades em grupo com componente oral sem dificuldade de compreensão", False),
            (5,  "Não apresenta dificuldades escolares ou sociais atribuídas à compreensão auditiva", False),
        ],
    },
]

AUDITIVO_OPCOES = [
    {"valor": 0, "label": "Nunca"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Frequentemente"},
    {"valor": 3, "label": "Sempre"},
]

AUDITIVO_CLASSIFICACAO = {
    "atencao":      [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "compreensao":  [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "memoria":      [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "figura_fundo": [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "impacto":      [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
    "total":        [("Atenção Clínica", 0, 49), ("Em Desenvolvimento", 50, 74), ("Adequado", 75, 100)],
}
