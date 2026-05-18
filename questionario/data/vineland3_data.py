# EHFA — Escala de Habilidades Funcionais e Adaptativas
# Formulário de Pais/Cuidadores — Níveis de Domínio
# Estrutura: 4 domínios adaptativos + Problemas de Comportamento (Seções A, B, C)
# Escala: 0 = Não faz, 1 = Faz algumas vezes ou com ajuda, 2 = Faz normalmente / na maioria das vezes

VINELAND3_SECOES = [
    {
        "nome": "Comunicação",
        "sigla": "COM",
        "cor": "#1D6FA4",
        "itens": list(range(1, 41)),
        "dominio": "com",
    },
    {
        "nome": "Atividade de Vida Diária",
        "sigla": "AVD",
        "cor": "#27AE60",
        "itens": list(range(41, 81)),
        "dominio": "avd",
    },
    {
        "nome": "Habilidades Sociais e Relacionamentos",
        "sigla": "SOC",
        "cor": "#8E44AD",
        "itens": list(range(81, 121)),
        "dominio": "soc",
    },
    {
        "nome": "Atividade Física / Habilidades Motoras",
        "sigla": "HMOT",
        "cor": "#E67E22",
        "itens": list(range(121, 146)),
        "dominio": "hmot",
    },
    {
        "nome": "Problemas de Comportamento — Seção A",
        "sigla": "PC-A",
        "cor": "#C0392B",
        "itens": list(range(146, 159)),
        "dominio": "pc_a",
    },
    {
        "nome": "Problemas de Comportamento — Seções B e C",
        "sigla": "PC-BC",
        "cor": "#922B21",
        "itens": list(range(159, 181)),
        "dominio": "pc_bc",
    },
]

VINELAND3_OPCOES = [
    (0, "Não faz", "0"),
    (1, "Faz algumas vezes ou com ajuda", "1"),
    (2, "Faz normalmente / na maioria das vezes", "2"),
]

VINELAND3_PERGUNTAS = {
    # ── COMUNICAÇÃO (1–40) ────────────────────────────────────────────────────
    1: "Expressa quantidade ao se referir a objetos. Exemplos: \"Dois carros\", \"Mais biscoitos\", \"Essas flores\".",
    2: "Combina ideias com a conjunção e em suas falas. Exemplos: \"Pai e mãe chegaram\", \"Quero suco e bolacha\".",
    3: "Compreende e obedece instruções condicionais do tipo \"se... então\". Exemplos: \"Se estiver com fome, então coma algo\"; \"Se estiver frio, então vista um casaco\".",
    4: "Responde adequadamente a perguntas sobre tempo. Exemplo: ao ser perguntado(a) \"Quando você acorda?\", responde \"De manhã\".",
    5: "Mantém atenção em uma narrativa contada por adulto por no mínimo 15 minutos.",
    6: "Explica causas e motivos quando questionado. Exemplo: ao ser perguntado \"Por que está triste?\", responde com uma razão coerente.",
    7: "Utiliza ao menos três gestos comunicativos com significado claro. Exemplos: acenar para chamar alguém, colocar o dedo na boca para pedir silêncio, abrir as mãos para indicar tamanho, encolher os ombros para dizer \"não sei\".",
    8: "Utiliza palavras descritivas ao falar sobre objetos ou pessoas. Exemplos: \"Carro vermelho\", \"Gato pequenininho\".",
    9: "Informa o próprio nome completo (nome e sobrenome) quando perguntado.",
    10: "Realiza a mesma ação em dois objetos indicados. Exemplos: \"Pega o livro e o caderno\", \"Guarda o casaco e a mochila\".",
    11: "Executa dois comandos diferentes e sem relação entre si. Exemplo: \"Apague a luz e traga meu óculos\".",
    12: "Emprega pronomes pessoais e possessivos corretamente na fala. Exemplos: eu, ele, nós, vocês, meu, nosso, deles.",
    13: "Forma frases compostas usando conectivos como e ou mas. Exemplos: \"Ela pediu e eu ajudei\"; \"Queria sair, mas estava chovendo\".",
    14: "Relata eventos passados com uso correto do tempo verbal. Exemplos: \"Fui ao parque ontem\", \"A professora contou uma história\".",
    15: "Diferencia e nomeia os lados esquerdo e direito do próprio corpo.",
    16: "Reproduz os elementos principais de uma história conhecida: personagens, enredo e desfecho.",
    17: "Cumpre uma sequência de três etapas em ordem. Exemplo: \"Calce o tênis, pegue a mochila e aguarde na porta\".",
    18: "Descreve situações do dia a dia com detalhes quando perguntado. Exemplo: relata o que fez durante uma visita ou passeio.",
    19: "Reproduz o próprio primeiro nome por escrito sem cometer erros.",
    20: "Orienta-se corretamente seguindo comandos de direção. Exemplos: \"Vire à esquerda\", \"Olhe para a direita\".",
    21: "Reformula o que disse quando percebe que o outro não entendeu.",
    22: "Acompanha uma explicação ou aula por 15 minutos seguidos e demonstra compreensão do conteúdo.",
    23: "Produz frases escritas com pelo menos três palavras de forma compreensível.",
    24: "Registra as letras do alfabeto na posição correta, sem invertê-las ou girá-las.",
    25: "Lembra-se de realizar uma tarefa pedida para ser feita em breve. Exemplo: \"Assim que terminar de brincar, guarde os brinquedos\".",
    26: "Escreve de memória ao menos 10 palavras diferentes sem precisar copiá-las. [Pontue 2 para Sim ou 0 para Não]",
    27: "Reconhece quando alguém usa ironia ou sarcasmo no discurso. Exemplo: compreende que \"Que coisa incrível!\" pode significar o oposto.",
    28: "Lê em voz alta frases com no mínimo três palavras de forma fluente.",
    29: "Usa a ordem alfabética de forma prática. Exemplos: busca uma palavra em dicionário ou um nome em lista ordenada.",
    30: "Mantém atenção e compreende o conteúdo de uma palestra ou explicação de 30 minutos.",
    31: "Informa corretamente o próprio endereço completo, incluindo cidade e estado, quando solicitado.",
    32: "Recorda-se de executar uma tarefa pedida para mais tarde no mesmo dia. Exemplo: \"Ao chegar da escola, não esqueça de ligar para a vovó\". [Pontue 2 para Sim ou 0 para Não]",
    33: "Possui nível de leitura equivalente ao 2º ano do ensino fundamental ou acima. [Pontue 2 para Sim ou 0 para Não]",
    34: "Fornece instruções detalhadas com três ou mais etapas de forma clara. Exemplos: \"Ande até o semáforo, vire à esquerda e entre no segundo portão\"; \"Ferva a água, adicione o macarrão, escorra e acrescente o molho\".",
    35: "Registra por escrito ou em desenho um passo a passo para outra pessoa seguir. Exemplos: receita, roteiro de caminho.",
    36: "Consulta fontes de pesquisa (internet ou biblioteca) para reunir informações e concluir uma tarefa escolar ou pessoal.",
    37: "Revisa o próprio texto antes de entregar, corrigindo erros de ortografia ou conteúdo.",
    38: "Preenche fichas ou formulários (físicos ou digitais) de até uma página com as informações solicitadas.",
    39: "Possui nível de leitura equivalente ao 6º ano do ensino fundamental ou acima.",
    40: "Produz textos dissertativos ou relatórios com no mínimo três páginas, com palavras próprias. [Pontue 2 para Sim ou 0 para Não]",

    # ── ATIVIDADE DE VIDA DIÁRIA (41–80) ─────────────────────────────────────
    41: "Utiliza o banheiro de forma independente durante o dia. Pode precisar de auxílio ao ajustar as roupas, mas deve reconhecer sozinho(a) quando precisa ir.",
    42: "Conta objetos individualmente chegando a pelo menos 10 itens.",
    43: "Demonstra entender que dinheiro é necessário para adquirir produtos. Não precisa fazer compras sozinho(a).",
    44: "Limpa o próprio rosto e mãos ao se sujar durante as refeições.",
    45: "Permanece próximo(a) ao acompanhante em locais públicos. Se conduzido(a) em carrinho ou colo, não deve ser considerado. [Pontue 2 se realizou isso quando mais novo(a)]",
    46: "Veste roupas que passam pela cabeça sem ajuda. Exemplos: camiseta, blusa, vestido.",
    47: "Demonstra cautela diante de fontes de calor. Exemplos: fogão aceso, forno quente, vela.",
    48: "Veste as roupas no sentido correto, com a frente para a frente e o avesso para dentro.",
    49: "Respeita normas de segurança como passageiro em veículos. Exemplos: mantém o cinto afivelado, não interfere na condução.",
    50: "Usa o banheiro de forma totalmente autônoma, dia e noite. Deve se higienizar, dar descarga e lavar as mãos.",
    51: "Realiza a escovação dos dentes de forma independente. Deve aplicar pasta, escovar adequadamente e enxaguar.",
    52: "Encaixa botões grandes nas respectivas casas. Exemplo: botões de sobretudo ou jaqueta.",
    53: "Abre e regula a torneira, ajustando a temperatura conforme necessário.",
    54: "Manuseia com cuidado objetos com bordas cortantes. Exemplos: faca de mesa, tesoura.",
    55: "Verifica os dois lados da via antes de atravessar ruas ou estradas.",
    56: "Limpa o local quando provoca um derramamento.",
    57: "Distingue alimentos nutritivos de opções não saudáveis.",
    58: "Conhece as atitudes corretas diante de situações de risco. Exemplos: saber quando pedir socorro, como acionar emergência, como se afastar de um perigo.",
    59: "Prepara um lanche ou refeição simples por conta própria. Exemplos: pão com manteiga, alimentos de microondas.",
    60: "Entra em contato com outras pessoas por meio de telefone, tablet ou computador.",
    61: "Encontra uma data específica no calendário quando solicitado. Exemplos: a data de hoje, um feriado ou aniversário.",
    62: "Age com segurança durante atividades físicas ou manuais. Exemplos: usa equipamentos de proteção, manuseia ferramentas com cuidado.",
    63: "Guarda as próprias roupas limpas nos locais adequados. Exemplos: dobra e coloca em gaveta, pendura em cabide.",
    64: "Opera pelo menos dois aparelhos domésticos simples. Exemplos: micro-ondas, torradeira, liquidificador.",
    65: "Lava frutas e legumes antes de consumi-los ou cozinhá-los.",
    66: "Pratica atividade física por iniciativa própria, visando saúde ou lazer.",
    67: "Adapta a vestimenta conforme as condições climáticas. Exemplo: percebe quando levar guarda-chuva ou casaco adicional.",
    68: "Utiliza recursos tecnológicos para ao menos dois fins diferentes. Exemplos: redigir textos, enviar mensagens, pesquisar informações, organizar arquivos.",
    69: "Cuida dos pertences pessoais fora de casa. Exemplos: guarda dinheiro, celular e carteira com atenção ao sair de compras ou viajar.",
    70: "Utiliza produtos de limpeza doméstica de forma adequada. Exemplos: detergente para louça, limpador para vidro, sabão em pó.",
    71: "Lava louça de forma satisfatória, seja à mão ou em máquina.",
    72: "Adota medidas de segurança ao sair de casa. Exemplos: tranca portas, fecha janelas, aciona alarme se houver.",
    73: "Corta alimentos de maior resistência com faca adequada. Exemplos: carnes, legumes crus, pão.",
    74: "Avalia qualidade e custo antes de decidir o que comprar.",
    75: "Compreende o direito de reclamar quando um produto ou serviço não corresponde ao esperado.",
    76: "Define uma meta de médio ou longo prazo e a persegue. Exemplos: poupa dinheiro para uma compra, adota uma rotina de exercícios.",
    77: "Cozinha ou assa alimentos usando fogão ou forno, ligando e desligando sozinho(a).",
    78: "Realiza a limpeza do banheiro, incluindo vaso sanitário, pia e chuveiro.",
    79: "Verifica a própria temperatura corporal quando necessário.",
    80: "Já realizou algum trabalho remunerado fora de casa. Exemplos: cuidado de animais ou jardim para vizinhos, emprego formal. [Pontue 2 para Sim ou 0 para Não]",

    # ── HABILIDADES SOCIAIS E RELACIONAMENTOS (81–120) ───────────────────────
    81: "Explica como os integrantes da família se relacionam com ele(a). Exemplos: \"Essa é minha avó\", \"Ele é meu primo\".",
    82: "Percebe as emoções dos outros ao observar expressões e comportamentos.",
    83: "Verbaliza as próprias emoções. Exemplos: \"Estou animado(a)\", \"Fiquei com medo\", \"Aquilo me incomoda\".",
    84: "Tem um amigo próximo ou um pequeno grupo de amigos estáveis. [Pontue 2 para Sim e 0 para Não]",
    85: "Demonstra empatia através de ações ou palavras. Exemplos: abraça quando o outro está triste, pergunta \"Você está bem?\", comemora uma boa notícia junto.",
    86: "Brinca com outra criança por pelo menos 30 minutos com supervisão de um adulto. [Pontue 2 se já era capaz disso e hoje dispensa supervisão]",
    87: "Compartilha brinquedos ou objetos quando solicitado.",
    88: "Adapta-se com facilidade ao encerramento de uma atividade para iniciar outra. Exemplos: termina de brincar e vai para o banho sem resistência excessiva.",
    89: "Mantém contato visual adequado ao interagir com outras pessoas.",
    90: "Prefere brincar junto com outras crianças a ficar apenas observando ou brincando sozinho(a).",
    91: "Participa de brincadeiras de faz de conta com outras crianças. Exemplos: brincar de médico, super-heróis, casinha. [Pontue 2 se fez isso quando mais jovem e hoje não tem mais esse perfil de brincadeira]",
    92: "Toma iniciativa para fazer amizades. Exemplos: convida para brincar, sugere sair junto.",
    93: "Pede desculpas de forma genuína após ofender ou machucar alguém.",
    94: "Ajusta o volume de voz, ritmo de fala e nível de animação conforme o contexto da conversa.",
    95: "Imita espontaneamente o que uma criança próxima está fazendo, mesmo sem interagir diretamente. Exemplo: vê outra criança desenhando e começa a desenhar também. [Pontue 2 se fez isso quando mais novo(a)]",
    96: "Aguarda sua vez ao participar de jogos ou esportes.",
    97: "Expressa frustração com palavras ou gestos em vez de gritar, bater ou arremessar objetos.",
    98: "Demonstra flexibilidade e disposição para ceder em situações de convivência.",
    99: "Realiza gestos espontâneos de cuidado com os outros. Exemplos: faz um desenho de presente, oferece ajuda sem ser pedido.",
    100: "Muda de assunto na conversa conforme necessário, sem se prender excessivamente a um único tema.",
    101: "Demonstra espírito esportivo ao participar de jogos: respeita regras, aceita derrotas, cumprimenta adversários.",
    102: "Respeita os limites de tempo definidos pelos responsáveis. Exemplos: tempo de tela, horário de retorno. [Pontue 2 se cumpria isso quando mais novo(a)]",
    103: "É cauteloso(a) quando um desconhecido tenta convencê-lo(a) a fazer algo arriscado, seja pessoalmente ou pela internet. [Se não souber, estime]",
    104: "Participa de encontros sociais na casa de colegas com dois ou mais indivíduos da mesma faixa etária.",
    105: "Conversa com os outros demonstrando interesse pelos assuntos que eles trazem, mesmo que não sejam do seu interesse.",
    106: "Percebe quando precisa fornecer mais contexto para que o outro acompanhe o que está dizendo.",
    107: "Reconhece sinais não verbais de rejeição e se afasta sem precisar de explicação. Exemplo: percebe que não é bem-vindo(a) quando o grupo o(a) ignora.",
    108: "Participa de jogos de tabuleiro, cartas ou eletrônicos que exigem estratégia e tomada de decisão. Exemplos: xadrez, damas, jogos cooperativos.",
    109: "Mantém o controle emocional quando os planos mudam por razões alheias à sua vontade. Exemplos: não se desorganiza quando um passeio é cancelado por chuva.",
    110: "Respeita o tempo e o espaço dos outros. Exemplos: não atrasa compromissos, não interrompe conversas alheias sem necessidade.",
    111: "Posiciona-se para evitar ser manipulado(a) ou prejudicado(a) por outros.",
    112: "Acompanha as preferências dos amigos em atividades, mesmo que prefira fazer algo diferente. [Se não souber, estime]",
    113: "Pondera as possíveis consequências antes de agir.",
    114: "Reconhece que uma pessoa pode agir de forma amigável com intenção de se aproveitar.",
    115: "Comunica aos responsáveis onde estará e quando voltará ao sair. Exemplo: avisa ou deixa recado antes de sair.",
    116: "Compreende que propagandas e anúncios podem conter informações parciais ou imprecisas.",
    117: "Capta mensagens implícitas nas interações. Exemplos: percebe que bocejo pode indicar tédio; que desvio de assunto pode ser esquiva; que olhar para o relógio sinaliza pressa.",
    118: "Planeja e organiza atividades sociais com colegas de forma independente. Exemplos: marca encontros, organiza saídas.",
    119: "Busca por conta própria informações sobre eventos e programações. Exemplos: consulta aplicativos, redes sociais ou telefona para o local.",
    120: "Frequenta locais com colegas da mesma faixa etária sem supervisão de adultos durante o dia. Exemplos: praça, shopping, espaço cultural.",

    # ── ATIVIDADE FÍSICA / HABILIDADES MOTORAS (121–145) ─────────────────────
    121: "Remove a embalagem de pequenos itens sozinho(a). Exemplos: bala, chiclete, biscoito embrulhado.",
    122: "Desce escadas colocando um pé em cada degrau. Pode usar o corrimão como apoio.",
    123: "Sobe um lance de pelo menos oito degraus em ritmo regular. Pode apoiar no corrimão.",
    124: "Corre com agilidade, alterando velocidade e direção conforme necessário. Exemplos: brincadeiras de perseguição, esportes.",
    125: "Salta para frente pelo menos três vezes consecutivas com os dois pés sem perder o equilíbrio.",
    126: "Segura corretamente o lápis, caneta ou giz ao escrever ou desenhar, sem usar preensão palmar.",
    127: "Caminha por duas ou mais quadras sem precisar de ajuda ou parar para descansar.",
    128: "Reproduz um círculo por escrito ao observar um modelo.",
    129: "Pedala um triciclo ou veículo de três rodas por pelo menos 2 metros. [Pontue 2 se dominou essa habilidade quando mais novo(a)]",
    130: "Intercepta uma bola do tamanho de uma bola de praia a 2 metros de distância. Pode usar uma ou as duas mãos.",
    131: "Pula num pé só com facilidade e equilíbrio, sem cair.",
    132: "Pinta figuras simples ou animais mantendo a cor predominantemente dentro dos contornos. [Pontue 2 se fez isso quando mais novo(a)]",
    133: "Pedala uma bicicleta com rodinhas ou de equilíbrio por pelo menos 3 metros. [Pontue 2 se já superou essa fase]",
    134: "Desenha espontaneamente mais de uma forma reconhecível. Exemplos: figura humana, casa, árvore.",
    135: "Transfere líquido de um recipiente para outro com mínimo derramamento. Exemplo: serve água ou suco em um copo.",
    136: "Pega uma bola menor (como bola de tênis) lançada a 0,5–1 metro. Deve pegar fora do corpo, não agarrar junto ao tronco.",
    137: "Recorta formas geométricas simples com tesoura. Exemplos: círculo, quadrado, retângulo.",
    138: "Realiza construções elaboradas com peças de montar, materiais de artes ou afins.",
    139: "Traça uma linha reta com o auxílio de uma régua.",
    140: "Pega uma bola menor lançada a 3 metros de distância, deslocando-se para alcançá-la se necessário.",
    141: "Dá um nó simples.",
    142: "Recorta formas mais complexas com precisão. Exemplos: estrela, letras, contorno de animais.",
    143: "Manuseia objetos muito pequenos com destreza. Exemplos: passa linha em agulha, monta peças minúsculas, cola botão.",
    144: "Pedala bicicleta sem rodinhas com equilíbrio e sem cair.",
    145: "Faz laço duplo com firmeza. Exemplos: cadarço de tênis, fita de embrulho.",

    # ── PROBLEMAS DE COMPORTAMENTO — SEÇÃO A (146–158) ───────────────────────
    # Escala invertida: 2 = mais problemas
    146: "Apresenta dependência excessiva de outras pessoas. Exemplos: pede ajuda mesmo quando não precisa, demonstra apego intenso a familiares ou cuidadores.",
    147: "Apresenta comportamentos alimentares atípicos. Exemplos: come compulsivamente, recusa a maioria dos alimentos, aceita apenas dois ou três itens, esconde comida.",
    148: "Apresenta dificuldades recorrentes com o sono. Exemplos: sonambulismo, pesadelos frequentes e prolongados, padrão de sono muito diferente do esperado para a idade.",
    149: "Recusa-se a ir à escola ou ao trabalho, ou precisa retornar antes do horário por causa de preocupações, tristeza ou nervosismo.",
    150: "Demonstra ansiedade ou tensão excessiva em situações do cotidiano.",
    151: "Chora ou fica aparentemente triste sem motivo identificável.",
    152: "Isola-se socialmente ou evita participar de atividades. Exemplos: se afasta do grupo, prefere ficar sozinho(a), recusa interações.",
    153: "Perdeu o interesse por atividades das quais antes gostava.",
    154: "Apresenta medo desproporcional de objetos ou situações cotidianas. Exemplos: alturas, animais comuns, elevadores.",
    155: "Preocupa-se excessivamente sem razão aparente identificável.",
    156: "Está frequentemente irritável, impaciente ou de mau humor.",
    157: "Demonstra sentimentos de desamparo ou desesperança. Exemplo: expressa que nada vai melhorar.",
    158: "Queixa-se frequentemente de mal-estar físico sem causa médica identificada. Exemplos: dores, cansaço, náuseas.",

    # ── PROBLEMAS DE COMPORTAMENTO — SEÇÃO B (159–169) ───────────────────────
    159: "Tem crises de choro, gritos, chutes ou outros comportamentos disruptivos.",
    160: "Desobedece figuras de autoridade de forma sistemática.",
    161: "Pratica intimidação psicológica ou física com outras pessoas.",
    162: "Mente, engana ou furta.",
    163: "Demonstra agressividade física. Exemplos: bate, morde, chuta outras pessoas.",
    164: "Usa palavras para ofender, humilhar ou magoar intencionalmente.",
    165: "É excessivamente teimoso(a) ou provoca discussões repetidamente.",
    166: "Infringe regras ou normas por pressão de colegas.",
    167: "Apresenta agitação motora acima do esperado para a faixa etária. Exemplos: não para quieto(a), não consegue permanecer sentado(a), está em constante movimento.",
    168: "Pega ou usa materiais da escola sem permissão. Exemplos: livros, objetos de colegas.",
    169: "Destrói objetos próprios ou de outros intencionalmente.",

    # ── PROBLEMAS DE COMPORTAMENTO — SEÇÃO C (170–180) ───────────────────────
    170: "Foca de forma intensa e persistente em um único objeto ou parte dele. Exemplos: gira rodinhas de carrinho, alinha objetos em fileira, observa ventiladores girando.",
    171: "Relata ouvir vozes ou enxergar coisas que os outros ao redor não percebem.",
    172: "Pratica automutilação. Exemplos: bate a cabeça em superfícies, se morde, se arranha, arranca os próprios cabelos.",
    173: "Apresenta fala estereotipada ou sem sentido aparente. Exemplos: repete a mesma frase repetidamente, faz sons ou palavras sem contexto.",
    174: "Apresenta movimentos corporais repetitivos e estereotipados. Exemplos: balança o corpo, gira em torno de si mesmo, agita as mãos.",
    175: "Ingere substâncias não alimentares. Exemplos: terra, sabão, massa de modelar, areia.",
    176: "Demonstra interesse obsessivo por um tema específico, de forma que incomoda os outros. Exemplos: fala repetidamente sobre um único assunto como trens, mapas ou personagens.",
    177: "Faz referências à morte ou já tentou se machucar gravemente.",
    178: "Afasta-se de grupos ou sai de ambientes sem avisar, sem considerar os riscos.",
    179: "Faz ameaças de agredir ou machucar outras pessoas.",
    180: "É influenciado(a) por terceiros a realizar ações que podem colocá-lo(a) ou a outros em risco.",
}

# Mapeamento item → domínio
VINELAND3_DOMINIO = {}
for _sec in VINELAND3_SECOES:
    for _item in _sec["itens"]:
        VINELAND3_DOMINIO[_item] = _sec["dominio"]

# Máximos por domínio
VINELAND3_MAXIMOS = {
    "com": 40 * 2,   # 80
    "avd": 40 * 2,   # 80
    "soc": 40 * 2,   # 80
    "hmot": 25 * 2,  # 50
    "pc_a": 13 * 2,  # 26
    "pc_b": 11 * 2,  # 22
    "pc_c": 11 * 2,  # 22
}

# Seção B = itens 159–169, Seção C = itens 170–180
_SECAO_B_ITENS = list(range(159, 170))
_SECAO_C_ITENS = list(range(170, 181))


def calcular_pontuacao_vineland3(respostas: dict) -> dict:
    """
    respostas: {numero_item: valor_int (0, 1 ou 2)}
    Retorna dict com pontuações brutas por domínio e totais.
    """
    totais = {k: 0 for k in VINELAND3_MAXIMOS}

    for item, valor in respostas.items():
        dominio = VINELAND3_DOMINIO.get(item)
        if dominio in ("pc_bc",):
            if item in _SECAO_B_ITENS:
                totais["pc_b"] += valor
            else:
                totais["pc_c"] += valor
        elif dominio:
            totais[dominio] = totais.get(dominio, 0) + valor

    totais["total_adaptativo"] = totais["com"] + totais["avd"] + totais["soc"] + totais["hmot"]
    totais["total_pc"] = totais["pc_a"] + totais["pc_b"] + totais["pc_c"]
    return totais
