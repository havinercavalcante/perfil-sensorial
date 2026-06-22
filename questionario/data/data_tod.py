TOD_OPCOES = [
    {"valor": 0, "label": "Nada"},
    {"valor": 1, "label": "Pouco"},
    {"valor": 2, "label": "Muito"},
    {"valor": 3, "label": "Demais"},
]

TOD_ITENS = [
    (1,  "Frequentemente interrompe ou se intromete nas atividades dos outros (conversas ou atividades lúdicas e jogos)"),
    (2,  "Tem fugido de sua casa ou escola pelo menos 2 vezes (ou uma vez sem retornar por um longo período)"),
    (3,  "Frequentemente argumenta desnecessariamente com adultos"),
    (4,  "Frequentemente mente para obter vantagens ou favores ou evitar obrigações"),
    (5,  "Frequentemente inicia luta corporal ou brigas com seus parentes de casa"),
    (6,  "Tem sido fisicamente cruel com as pessoas"),
    (7,  "Fala excessivamente"),
    (8,  "Tem roubado itens ou coisas"),
    (9,  "Distrai-se fácil por estímulos"),
    (10, "Frequentemente se engaja em atividades físicas perigosas sem considerar os riscos e sem noção de perigo"),
    (11, "Frequentemente mata aulas (antes dos 13 anos)"),
    (12, "Inquietude excessiva com as mãos e os pés e durante postura sentada"),
    (13, "É rancorosamente vingativo"),
    (14, "Frequentemente usa linguagem obscena"),
    (15, "Frequente responsabiliza os outros pelos seus erros ou comportamentos inadequados"),
    (16, "Tem deliberadamente destruído as propriedades dos outros"),
    (17, "Frequentemente desafia ou se recusa concordar com opiniões ou regras de adultos"),
    (18, "Parece frequentemente não atender quando se fala diretamente com ele(a)"),
    (19, "Frequentemente responde precocemente antes das perguntas serem completadas"),
    (20, "Frequentemente inicia lutas físicas e brigas com pessoas que não conhece ou que vivem na sua escola ou vizinhança"),
    (21, "Frequentemente pula de uma atividade para outra"),
    (22, "Tem frequentemente dificuldade de participar uma atividade em silêncio"),
    (23, "Frequentemente falha em cumprir atividades que exigem observação de detalhes e comete erros na escola, em casa e/ou com os trabalhos"),
    (24, "Frequentemente emburra e aborrece por pouca coisa"),
    (25, "Frequentemente levanta ou anda em momentos em que se espera que fique sentado e tranquilo"),
    (26, "Frequentemente é sensível e facilmente se aborrece com os outros"),
    (27, "Frequentemente não segue instruções e fracassa em tarefas escolares (mas não por comportamento opositivo ou porque não entendeu as instruções)"),
    (28, "Temperamento explosivo facilmente"),
    (29, "Tem frequente dificuldade em sustentar a atenção em tarefas ou atividades lúdicas"),
    (30, "Tem dificuldade em esperar sua vez"),
    (31, "Forçou ou força alguém a manter relações sexuais"),
    (32, "Aplica bullying, intimida ou ameaça as pessoas"),
    (33, "Frequentemente quer sempre chegar logo na frente e faz as coisas correndo"),
    (34, "Frequentemente perde coisas, objetos necessários para tarefas e atividades (brinquedos, materiais escolares, lápis, livros)"),
    (35, "Frequentemente se agita e corre excessivamente em situações nas quais não se recomenda ou não se é esperado"),
    (36, "Aplica atos cruéis com animais"),
    (37, "Frequentemente evita, não gosta ou fica relutante para se engajar em atividades"),
    (38, "Fica fora de casa com frequência mesmo com a proibição dos pais, começando antes dos 13 anos"),
    (39, "Deliberadamente aborrece as pessoas"),
    (40, "Tem roubado de forma a confrontar com a vítima (assalto, extorsão, roubo à mão armada)"),
    (41, "Estraga deliberadamente patrimônios, causando sérios danos"),
    (42, "Tem evidente dificuldade em organizar tarefas e atividades sequenciais"),
    (43, "Tem quebrado e desfastado muito coisas da casa, do carro ou da escola"),
    (44, "Frequentemente é esquecido para atividades rotineiras de vida diária"),
    (45, "Tem usado instrumentos ou armas que tem causado sérios danos físicos às pessoas ou instituições"),
]

# Itens da nota de corte (TOD)
TOD_ITENS_CORTE = {3, 13, 15, 17, 24, 26, 28, 39}

# Nota de corte: se 4 ou mais itens_corte tiverem valor >= 2 -> positivo para TOD
TOD_LIMIAR_CORTE = 4
TOD_VALOR_CORTE = 2
