# VINELAND-3 — Formulário de Pais/Cuidadores dos Níveis de Domínio
# Estrutura: 4 domínios adaptativos + Problemas de Comportamento (Seções A, B, C)
# Escala: 0 = Nunca, 1 = Às vezes, 2 = Usualmente ou Frequentemente

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
    (0, "Nunca", "0"),
    (1, "Às vezes", "1"),
    (2, "Usualmente ou Frequentemente", "2"),
]

VINELAND3_PERGUNTAS = {
    # ── COMUNICAÇÃO (1–40) ────────────────────────────────────────────────────
    1: "Sabe como dizer mais de um de alguma coisa. Exemplos: \"Dois gatos\", \"Mais bolachas\", \"Aquelas flores\".",
    2: "Usa e em frases. Exemplos: \"Mamãe e papai estão aqui\", \"Eu quero sorvete e bolo\".",
    3: "Segue as instruções \"se – então\". Exemplos: \"Se você está com sede, então pegue uma bebida\"; \"Se você está com frio, então pegue um moletom.\"",
    4: "Responde a perguntas que usam quando. Exemplo: você pergunta \"Quando você toma café da manhã?\" Diz \"De manhã\".",
    5: "Presta atenção a uma história por pelo menos 15 minutos.",
    6: "Responde a perguntas que usam o porquê. Exemplo: você pergunta \"Por que você está chorando?\" Ele diz \"Meu brinquedo quebrou\".",
    7: "Faz pelo menos três gestos mais avançados, como estes: (1) vir aqui com a mão, (2) colocar um dedo sobre os lábios para dizer silêncio, (3) separar as mãos para mostrar o desse tamanho, (4) balançar os ombros para dizer que não sei.",
    8: "Usa adjetivos para descrever as coisas. Exemplos: \"Retrato bonito\", \"Cachorrinho grande\".",
    9: "Diz seu nome e sobrenome quando você pergunta.",
    10: "Segue instruções para fazer a mesma ação com dois objetos diferentes. Exemplos: \"Traga-me o lápis e a bola\", \"Coloque sua camisa e seus sapatos\".",
    11: "Segue as instruções para fazer duas coisas que não estão relacionadas. Exemplo: \"Desligue a TV e pegue minhas chaves\".",
    12: "Usa todos os pronomes (palavras que se referem a si e aos outros) corretamente. Exemplos: eu, ela, nós, eles, seus, nossos, deles.",
    13: "Usa sentenças de duas partes unidas por e ou mas. Exemplos: \"Ela me perguntou e eu disse não\"; \"Julio queria ir, mas eu não quis.\"",
    14: "Sabe como dizer que algo aconteceu no passado. Exemplos: \"Eu andei até a loja\", \"Maria assou um bolo.\"",
    15: "Identifica a esquerda e a direita em seu corpo.",
    16: "Conta as partes básicas de uma história familiar: os personagens, o que acontece, como termina, etc.",
    17: "Segue instruções de três passos. Exemplo: \"Vista-se, tome o café da manhã e escove os dentes\".",
    18: "Fala sobre seus eventos cotidianos em detalhes. Exemplo: quando você pergunta o que aconteceu na casa de um amigo hoje.",
    19: "Copia o seu primeiro nome sem erros.",
    20: "Segue as direções envolvendo esquerda e direita. Exemplos: \"Vá para a esquerda\", \"Olhe para a direita\".",
    21: "Diz algo de uma maneira diferente se necessário para ajudar alguém a entender o que ele(a) quer dizer.",
    22: "Presta atenção a uma aula informativa de 15 minutos e compreende o que está sendo dito.",
    23: "Escreve frases simples com três ou mais palavras.",
    24: "Escreve letras do alfabeto corretamente, e não de trás para frente ou de cabeça para baixo.",
    25: "Quando solicitado a fazer algo um pouco mais tarde, lembra-se de fazer isso. Exemplo: \"Quando seu programa acabar, coloque seus pratos na pia.\"",
    26: "Escreve pelo menos 10 palavras de cabeça. Exemplos: Chapéu, Bola, etc. [Pontue 2 para Sim ou 0 para Não]",
    27: "Entende o que as pessoas realmente querem dizer quando estão sendo sarcásticas. Exemplo: sabe quando \"Isso é ótimo!\" significa \"Isso é horrível!\"",
    28: "Lê sentenças simples com três ou mais palavras em voz alta.",
    29: "Compreende a ordem alfabética. Exemplos: localiza um nome em um catálogo de endereços ou lista de números de telefone, localiza uma palavra em um dicionário.",
    30: "Presta atenção a uma palestra informativa de 30 minutos e compreende o que está sendo dito.",
    31: "Diz seu endereço completo corretamente quando você pergunta. Deve incluir cidade e estado.",
    32: "Quando solicitado/a a fazer algo muito mais tarde naquele dia, lembra-se de fazê-lo. Exemplo: \"Quando você chegar em casa da escola, deixe o cachorro sair para passear.\" [Pontue 2 para Sim ou 0 para Não]",
    33: "Lê em um nível de segundo ano ou superior. [Pontue 2 para Sim ou 0 para Não]",
    34: "Dá direções complexas com três ou mais etapas. Exemplos: \"Vá até o final desta rua, vire à direita e siga por meio quarteirão até ver o prédio branco de dois andares\"; \"Primeiro, cozinhe o macarrão, despeje-o em uma tigela com o molho, e coloque migalhas de pão por cima e asse por 10 minutos.\"",
    35: "Escreve ou desenha instruções para os outros. Exemplos: como fazer algo, como chegar a algum lugar.",
    36: "Usa a internet ou uma biblioteca para encontrar informações para escrever um trabalho ou concluir uma tarefa.",
    37: "Verifica e corrige seu trabalho escrito antes de entregá-lo. Exemplo: verifica a ortografia usando o computador.",
    38: "Preenche formulários de papel ou eletrônicos de uma página ou menos. Exemplo: formulários para escola ou trabalho.",
    39: "Lê em um nível de sexto ano ou superior.",
    40: "Escreve relatórios com pelo menos três páginas. Deve usar palavras próprias e não copiar. [Pontue 2 para Sim ou 0 para Não]",

    # ── ATIVIDADE DE VIDA DIÁRIA (41–80) ─────────────────────────────────────
    41: "Usa o banheiro durante o dia. Pode precisar de ajuda como abaixar a calça, mas deve identificar quando precisa ir.",
    42: "Conta pelo menos 10 objetos, um por um.",
    43: "Compreende que o dinheiro é usado para comprar coisas. Não precisa usar dinheiro sozinho(a).",
    44: "Limpa o rosto e as mãos quando come algo melequento.",
    45: "Fica perto em locais públicos. Se carregado(a), empurrado(a) em um carrinho, etc., não conta. [Marque 2 se ele(a) fez isso quando era mais novo(a)]",
    46: "Coloca roupas de vestir pela cabeça. Exemplos: camiseta, camisa, vestido.",
    47: "Tem cuidado com coisas que poderiam queimá-lo(a). Exemplos: fogão, forno, fogo.",
    48: "Coloca a roupa com o lado correto para a frente e o lado correto para trás.",
    49: "Compreende as regras de segurança dos passageiros e segue-as. Exemplos: mantém o cinto de segurança afivelado, não distrai o motorista.",
    50: "Usa o banheiro durante o dia e à noite sem ajuda. Deve se limpar, dar descarga e lavar as mãos sozinho(a).",
    51: "Escova seus dentes. Deve colocar pasta de dente na escova, escovar bem e enxaguar.",
    52: "Coloca botões grandes nos buracos corretos. Exemplo: botões de casaco.",
    53: "Liga as torneiras e ajusta a temperatura da água.",
    54: "Tem cuidado ao usar objetos pontiagudos. Exemplos: facas, tesouras.",
    55: "Olha para os dois lados ao atravessar ruas ou estradas.",
    56: "Limpa quando derrama algo.",
    57: "Sabe quais são os alimentos saudáveis e não saudáveis.",
    58: "Sabe o que fazer em situações perigosas. Exemplos: quando obter ajuda, quando ligar para o 190, como fugir do perigo.",
    59: "Faz seu próprio lanche ou refeição simples. Exemplos: sanduíche, queijo e bolachas, alimentos de microondas.",
    60: "Liga para outras pessoas usando um telefone, computador ou outro dispositivo eletrônico.",
    61: "Localiza uma data em um calendário quando você pergunta. Exemplos: data de hoje, o dia de seu aniversário.",
    62: "Age com segurança ao trabalhar e/ou se divertir. Exemplos: usa equipamento de segurança, é cuidadoso ao operar ferramentas e maquinaria.",
    63: "Coloca suas roupas limpas onde elas pertencem. Exemplos: em gavetas ou armário, em cabides.",
    64: "Utiliza pelo menos dois utensílios de cozinha simples. Exemplos: torradeira, microondas, abridor de latas elétrico.",
    65: "Lava frutas e verduras antes de comê-las ou cozinhá-las.",
    66: "Escolhe se exercitar por saúde ou prazer.",
    67: "Muda de roupa conforme o clima, identifica quando usar um guarda-chuva ou casaco por exemplo.",
    68: "Opera tecnologia para executar pelo menos dois tipos de tarefas. Exemplos: escrever documentos escolares ou de trabalho, enviar e-mails para a escola ou o trabalho, organizar informações, encontrar informações na internet.",
    69: "Mantém em segurança, quando fora de casa, dinheiro, carteira, telefone, etc. Exemplos: ao fazer compras, comer fora ou durante uma viagem.",
    70: "Usa produtos domésticos corretamente. Exemplos: sabão em pó para roupas, polidor de móveis, limpador de vidro.",
    71: "Lava a louça. Pode lavar manualmente ou usar a máquina de lavar louça.",
    72: "Mantém a casa segura quando sai. Exemplos: tranca as portas, fecha as janelas, liga o alarme.",
    73: "Corta alimentos mais difíceis de cortar com uma faca afiada. Exemplos: carne, vegetais crus.",
    74: "Considera qualidade e preço ao decidir o que comprar.",
    75: "Entende o direito de relatar um problema com um produto, um serviço, com sua moradia, etc.",
    76: "Estabelece um objetivo que pode ser feito em seis meses ou mais e o alcança. Exemplos: trabalha e economiza dinheiro para comprar algo caro, fica em melhor forma física.",
    77: "Usa o fogão ou forno para cozinhar ou assar. Deve ligar e desligar sozinho(a).",
    78: "Limpa o banheiro: vaso sanitário, pia, banheira ou chuveiro, etc.",
    79: "Mede a própria temperatura, quando necessário.",
    80: "Trabalhou fora de casa para ganhar dinheiro. Exemplos: trabalho de babá ou trabalho no quintal para um vizinho, ter um emprego. [Pontue 2 para Sim ou 0 para Não]",

    # ── HABILIDADES SOCIAIS E RELACIONAMENTOS (81–120) ───────────────────────
    81: "Diz como os membros da família estão relacionados a ele(a). Exemplos: \"Essa é minha mãe\", \"Ele é meu irmão\".",
    82: "Percebe quando outros estão felizes, tristes, com medo, chateados, etc.",
    83: "Usa palavras para expressar suas emoções. Exemplos: \"Eu estou feliz\", \"Eu estou com medo\", \"Eu não gosto dele\".",
    84: "Tem um melhor amigo ou alguns bons amigos. [Pontue 2 para Sim e 0 para Não]",
    85: "Usa ações ou palavras para mostrar aos outros que ele(a) se sente feliz por eles, triste por eles, ou preocupado com eles. Exemplos: dá abraços, dá a mão, pergunta \"Você está bem?\".",
    86: "Brinca com uma ou mais crianças por pelo menos 30 minutos, com alguém mais velho supervisionando. [Pontue 2 se ele(a) fez isso quando mais jovem, e agora não precisa de supervisão]",
    87: "Divide seus brinquedos ou outras coisas quando alguém pede para ele(a) fazê-lo.",
    88: "Muda facilmente de uma atividade para outra. Exemplos: muda da hora de brincar para o banho sem ficar muito chateado.",
    89: "Faz bom contato visual quando interage com as pessoas.",
    90: "Prefere brincar com outras crianças ao invés de só observá-las ou brincar sozinha(o).",
    91: "Brinca de brincadeiras simples, de faz de conta, com outras crianças. Exemplos: brinca de se fantasiar, finge ser super-herói. [Pontue 2 se ele(a) fez isso quando mais jovem, e agora não brinca mais de faz de conta]",
    92: "Tenta fazer amizade com outros de sua idade. Exemplos: convida para um jogo, pede para ir em algum lugar com outra criança.",
    93: "Desculpa-se depois de ferir os sentimentos de alguém, e de forma genuína.",
    94: "Conversa com o volume, velocidade e nível de empolgação corretos para uma conversa.",
    95: "Imita uma criança brincando por perto, mesmo que não estejam brincando juntas. Exemplo: vê outra criança empilhando blocos e então começa a empilhar blocos. [Pontue 2 se ele(a) fez isso quando mais jovem, não brinca mais de empilhar]",
    96: "Aceita revezar quando brinca de jogos ou pratica esportes.",
    97: "Usa palavras ou gestos quando está chateado em vez de gritar, bater, jogar algo, etc.",
    98: "Está disposto a fazer concessões para se dar bem com outras pessoas da sua idade.",
    99: "Faz coisas para tentar agradar os outros. Exemplos: faz um cartão ou presente para alguém, oferece ajuda sem ser solicitado.",
    100: "Muda facilmente de um assunto para outro em uma conversa quando necessário. Não fica \"preso\" em um só assunto.",
    101: "Demonstra bom senso esportivo em jogos ou esportes: joga de maneira justa, não é excessivamente agressivo, parabeniza jogadores vencedores, não age mal quando perde, etc.",
    102: "Segue os limites de tempo fornecidos pelos pais, avô, etc. Exemplos: por quanto tempo pode assistir TV, jogar, usar a internet, brincar fora de casa, etc. [Pontue 2 se ele(a) fez isso quando mais jovem]",
    103: "É cauteloso(a) quando alguém que ele(a) não conhece bem tenta fazer com que ele(a) faça algo arriscado. Pode ser pessoalmente ou pela internet. [Se você não sabe, estime uma pontuação]",
    104: "Junta-se com dois ou mais indivíduos de sua idade na casa de outra pessoa.",
    105: "Conversa com os outros sobre coisas nas quais eles estão interessados, mesmo que ele(a) não esteja.",
    106: "Percebe quando alguém precisa de alguma explicação para acompanhar o que ele(a) está dizendo.",
    107: "Fica de fora de um grupo quando deixam transparecer, sem palavras, que ele(a) não é bem vindo(a). Exemplo: ignorando-o/a.",
    108: "Engaja em jogos de tabuleiro, cartas ou jogos eletrônicos que requerem decisões e habilidades. Exemplos: Banco Imobiliário, pôquer, damas, videogames interativos.",
    109: "Controla a sua raiva ou mágoa quando os planos mudam por razões que não podem ser controladas. Exemplos: não chora nem fica bravo/a quando um evento é cancelado devido ao mau tempo ou quando uma viagem é adiada devido a problemas no carro.",
    110: "Respeita o tempo das outras pessoas. Exemplos: não deixa os outros esperando, não interrompe os outros quando estão ocupados.",
    111: "Impede que os outros o/a controlem ou tirem vantagem dele(a).",
    112: "Faz coisas que seus amigos querem fazer, mesmo quando preferiria fazer outra coisa. [Se você não souber, estime uma pontuação]",
    113: "Pensa nas consequências de seus atos antes de fazer alguma coisa.",
    114: "Entende que uma pessoa agindo amigavelmente pode estar querendo tirar vantagem dele(a).",
    115: "Deixa que você saiba sobre os seus planos quando vai sair. Exemplo: informa ou deixa uma mensagem sobre onde está indo e quando estará em casa.",
    116: "Entende que algumas coisas veiculadas a publicidade podem não ser verdadeiras.",
    117: "Pega dicas implícitas durante a conversa. Exemplos: sabe que alguém que boceja pode estar entediado; que as pessoas podem mudar o assunto para evitar falar sobre algo; que olhar para o relógio pode significar que a pessoa precisa terminar a conversa.",
    118: "Planeja ou toma a iniciativa de fazer coisas com outros da mesma idade sozinho(a). Exemplos: planeja um jantar com um amigo, planeja ir ao cinema com amigos(as) no final de semana.",
    119: "Obtém informações de programação para filmes, eventos esportivos, shows, etc. Exemplos: olha no jornal ou na internet, telefona a um estabelecimento para obter informações.",
    120: "Vai a lugares com outros indivíduos de sua idade durante o dia sem alguém supervisionando. Exemplos: shopping, parque, centro comunitário.",

    # ── ATIVIDADE FÍSICA / HABILIDADES MOTORAS (121–145) ─────────────────────
    121: "Desembrulha pequenos objetos. Exemplos: pedaço de doce ou chiclete.",
    122: "Desce escadas, colocando um pé em cada degrau. Pode usar corrimão.",
    123: "Sobe um conjunto de oito ou mais degraus em um ritmo normal. Pode usar corrimão.",
    124: "Corre sem dificuldade, mudando sua velocidade e direção. Exemplos: brincar de pegapega ou praticar esportes, perseguir um animal de estimação.",
    125: "Salta para a frente pelo menos três vezes com os dois pés sem cair.",
    126: "Segura um giz de cera, caneta ou lápis corretamente para escrever ou desenhar. Não segura com preensão palmar.",
    127: "Anda duas quadras ou mais sem precisar de ajuda ou descansar.",
    128: "Desenha um círculo à mão enquanto olha um modelo.",
    129: "Pedala um triciclo ou outro veículo com três rodas por pelo menos 2 metros. [Pontue 2 se ele(a) fez isso quando mais jovem, e já adquiriu a habilidade]",
    130: "Pega uma bola do tamanho de uma bola de praia a uma distância de 2 metros. Pode usar uma ou duas mãos.",
    131: "Pula com um pé só com facilidade, sem cair.",
    132: "Pinta formas simples ou animais. Deve pintar mais dentro do que fora da linha. [Pontue 2 se ele(a) fez isso quando mais jovem, e agora não pinta mais]",
    133: "Pedala uma bicicleta com rodinha ou bicicleta de equilíbrio por pelo menos 3 metros. [Pontue 2 se ele(a) fez isso quando mais jovem, e agora já adquiriu a habilidade]",
    134: "Desenha mais de uma forma que você consegue reconhecer. Exemplos: pessoa, casa, árvore.",
    135: "Transfere líquido de um recipiente para outro com pouco ou nenhum derramamento. Exemplo: coloca leite ou suco em um copo.",
    136: "Pega uma bola do tamanho de uma bola de tênis ou beisebol a uma distância de 0,5 a 1 metro. Pode usar uma ou ambas as mãos, mas deve pegar longe do corpo em vez de agarrar a bola junto ao corpo.",
    137: "Recorta formas simples. Exemplos: círculos, quadrados, retângulos.",
    138: "Faz construções complexas usando brinquedos de montar, materiais de arte e artesanato, etc.",
    139: "Desenha uma linha reta com uma régua.",
    140: "Pega uma bola do tamanho de uma bola de tênis ou beisebol a uma distância de 3 metros, movendo-se para pegá-la se necessário. Pode usar uma ou ambas as mãos.",
    141: "Amarra um nó.",
    142: "Recorta formas complexas. Exemplos: estrelas, animais, letras do alfabeto.",
    143: "Trabalha com objetos bem pequenos. Exemplos: ajusta um relógio com as mãos, coloca a linha em uma agulha, cola pequenas peças.",
    144: "Pedala uma bicicleta regular, sem rodinhas, sem cair.",
    145: "Faz um laço apertado. Exemplos: cadarço de sapato, embalagem de presente.",

    # ── PROBLEMAS DE COMPORTAMENTO — SEÇÃO A (146–158) ───────────────────────
    # Escala invertida: 2 = mais problemas
    146: "É excessivamente carente ou dependente. Exemplos: insiste em ajudar, mesmo quando não é necessário; é excessivamente apegado aos membros da família, cuidador ou professor.",
    147: "Tem problemas alimentares. Exemplos: come em excesso, se recusa a comer, come apenas uma ou duas coisas, acumula comida.",
    148: "Tem problemas de sono. Exemplos: anda enquanto dorme, tem longos pesadelos, dorme mais ou menos que as crianças de sua idade.",
    149: "Recusa-se a ir à escola ou ao trabalho ou precisa voltar para casa por causa de preocupações, tristeza, nervosismo, etc.",
    150: "É extremamente ansioso(a) ou nervoso(a).",
    151: "Chora ou fica triste por motivos não aparentes.",
    152: "Evita interagir com os outros (se retira do ambiente, prefere ficar sozinha(o), etc.).",
    153: "Falta interesse para fazer as coisas que ele(a) gosta ou costumava gostar.",
    154: "Tem medo excessivo de um ou mais objetos ou situações comuns. Exemplos: altura, cobras, elevador.",
    155: "Preocupa-se demasiadamente por nenhuma razão clara.",
    156: "É muito irritável ou mal-humorado(a).",
    157: "Sente-se desamparado(a) ou sem esperança. Exemplo: diz que as coisas estão ruins e nunca melhoram.",
    158: "Reclama de estar se sentindo doente, exausto ou com dor, mesmo que não haja motivo médico.",

    # ── PROBLEMAS DE COMPORTAMENTO — SEÇÃO B (159–169) ───────────────────────
    159: "Faz birras: grita, chora, chuta, etc.",
    160: "Desobedece a figura de autoridade.",
    161: "Faz bullying, com outros psicologicamente ou fisicamente.",
    162: "Mente, trapaceia ou rouba.",
    163: "É fisicamente agressivo(a). Exemplos: bate, chuta, morde.",
    164: "É abusivo verbalmente. Exemplos: machuca outros de propósito com insultos, humilhações, etc.",
    165: "É teimoso(a) ou discute excessivamente.",
    166: "Quebra regras ou leis por pressão dos colegas.",
    167: "É muito ativo ou inquieto do que outros da sua idade. Exemplos: se movimenta o tempo todo, não consegue ficar sentado, está sempre inquieto.",
    168: "Pega ou usa pertences escolares quando não é permitido. Exemplos: livros, materiais de escritório.",
    169: "Destrói itens pessoais ou de outras pessoas de propósito.",

    # ── PROBLEMAS DE COMPORTAMENTO — SEÇÃO C (170–180) ───────────────────────
    170: "Fixa-se em um único objeto ou parte deles. Exemplos: foca as rodinhas girando ou as pás do ventilador; alinha objetos.",
    171: "Fala sobre ouvir vozes que outros não ouvem ou sobre ver coisas que outros não veem.",
    172: "Se machuca. Exemplos: bate a cabeça, se bate ou se morde, se corta, se arranha, arranca o cabelo.",
    173: "Apresenta fala estranha ou repetitiva. Exemplos: fala coisas que não fazem sentido, repete a mesma coisa várias vezes seguidas.",
    174: "Apresenta movimentos físicos repetitivos. Exemplos: balançar para frente e para trás, girar em torno do próprio eixo, abanar as mãos.",
    175: "Come itens que não são comidas, como sujeira, pasta ou sabão.",
    176: "Fica tão fixado(a) em um único assunto que chega a irritar os outros. Exemplos: trens, mapas, sistema de metrô.",
    177: "Fala sobre se matar ou tentou se matar.",
    178: "Perambula longe de um grupo da escola ou sai da escola sem se preocupar com sua segurança.",
    179: "Ameaça machucar ou matar outra pessoa.",
    180: "É influenciado/a por outros a fazer algo que poderia prejudicar seriamente a si mesmo ou a outra pessoa.",
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
