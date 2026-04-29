VINELAND_GRUPOS = [
    {
        "nome": "Nível de Idade: 0 meses a 1 ano",
        "itens": [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
    },
    {
        "nome": "Nível de Idade: 1 a 2 anos",
        "itens": [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34],
    },
    {
        "nome": "Nível de Idade: 2 a 3 anos",
        "itens": [35, 36, 37, 38, 39, 40, 41, 42, 43, 44],
    },
    {
        "nome": "Nível de Idade: 3 a 4 anos",
        "itens": [45, 46, 47, 48, 49, 50],
    },
    {
        "nome": "Nível de Idade: 4 a 5 anos",
        "itens": [51, 52, 53, 54, 55, 56],
    },
    {
        "nome": "Nível de Idade: 5 a 6 anos",
        "itens": [57, 58, 59, 60, 61],
    },
    {
        "nome": "Nível de Idade: 6 a 7 anos",
        "itens": [62, 63, 64, 65],
    },
    {
        "nome": "Nível de Idade: 7 a 8 anos",
        "itens": [66, 67, 68, 69, 70],
    },
    {
        "nome": "Nível de Idade: 8 a 9 anos",
        "itens": [71, 72, 73, 74],
    },
    {
        "nome": "Nível de Idade: 9 a 10 anos",
        "itens": [75, 76, 77],
    },
    {
        "nome": "Nível de Idade: 10 a 11 anos",
        "itens": [78, 79, 80, 81],
    },
    {
        "nome": "Nível de Idade: 11 a 12 anos",
        "itens": [82, 83, 84],
    },
    {
        "nome": "Nível de Idade: 12 a 15 anos",
        "itens": [85, 86, 87, 88, 89],
    },
    {
        "nome": "Nível de Idade: 15 a 18 anos",
        "itens": [90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101],
    },
    {
        "nome": "Nível de Idade: 20 a 25 anos",
        "itens": [102, 103, 104, 105],
    },
    {
        "nome": "Nível de Idade: 25 anos ou mais",
        "itens": [106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117],
    },
]

# Legenda: C=Comunicação, L=Locomoção, O=Ocupação, S=Socialização,
#          AG=Autogoverno, AGE=Auto-auxílio geral, AC=Auto-auxílio para comer,
#          AV=Auto-auxílio para vestir
VINELAND_CATEGORIA = {
    # C — Comunicação
    1: "C", 10: "C", 17: "C", 31: "C", 34: "C", 44: "C", 58: "C", 63: "C",
    73: "C", 78: "C", 79: "C", 81: "C", 84: "C", 90: "C", 91: "C",
    # L — Locomoção
    12: "L", 18: "L", 29: "L", 32: "L", 45: "L", 53: "L", 61: "L",
    77: "L", 92: "L", 96: "L",
    # O — Ocupação
    7: "O", 19: "O", 22: "O", 24: "O", 36: "O", 43: "O", 48: "O", 55: "O",
    57: "O", 71: "O", 72: "O", 80: "O", 82: "O", 89: "O", 98: "O",
    106: "O", 107: "O", 108: "O", 111: "O", 113: "O", 114: "O", 116: "O",
    # S — Socialização
    3: "S", 14: "S", 27: "S", 46: "S", 49: "S", 56: "S", 59: "S", 68: "S",
    69: "S", 85: "S", 88: "S", 103: "S", 104: "S", 109: "S", 110: "S",
    115: "S", 117: "S",
    # AG — Autogoverno
    60: "AG", 76: "AG", 83: "AG", 87: "AG", 93: "AG", 94: "AG", 95: "AG",
    97: "AG", 99: "AG", 100: "AG", 101: "AG", 102: "AG", 105: "AG", 112: "AG",
    # AGE — Auto-auxílio geral
    2: "AGE", 5: "AGE", 6: "AGE", 8: "AGE", 9: "AGE", 13: "AGE", 15: "AGE",
    23: "AGE", 26: "AGE", 35: "AGE", 41: "AGE", 51: "AGE", 66: "AGE",
    # AC — Auto-auxílio para comer
    11: "AC", 16: "AC", 20: "AC", 25: "AC", 28: "AC", 30: "AC", 33: "AC",
    38: "AC", 39: "AC", 62: "AC", 67: "AC", 75: "AC",
    # AV — Auto-auxílio para vestir
    21: "AV", 37: "AV", 40: "AV", 42: "AV", 47: "AV", 50: "AV", 52: "AV",
    54: "AV", 64: "AV", 65: "AV", 70: "AV", 74: "AV", 86: "AV",
}

VINELAND_PERGUNTAS = {
    # ── 0 meses a 1 ano ──────────────────────────────────────────────────────
    1: "RESMUNGA, RI. Vocaliza inarticuladamente (além de chorar). Balbucia espontaneamente ou arrulha com animação evidente ou satisfação. Ri espontaneamente ou quando estimulado.",
    2: "EQUILIBRA A CABEÇA. Conserva a cabeça erguida voluntariamente (sem auxílio) com tronco ereto por período indefinido (cerca de um minuto).",
    3: "PROCURA POR PESSOAS FAMILIARES. Pede para ser pego ou mostra desejo de ser carregado pela mãe, pai ou outra pessoa da família; ou de outro modo mostra claramente reconhecimento.",
    5: "VIRA SOBRE SI (ROLA). Deitado de bruços, vira sobre si de costas ou vice-versa, sem auxílio.",
    6: "PROCURA ALCANÇAR OBJETOS PRÓXIMOS. Esforça-se por obter objetos próximos, mas além do alcance.",
    7: "DISTRAI-SE SOZINHO (A). Brinca com chocalhos ou outros objetos simples, ou distrai-se com outras atividades simples, por ¼ de hora ou mais, sem necessidade de atenção.",
    8: "SENTA-SE SEM APÔIO. Senta-se direito sobre superfície dura, plana, sem apoio, por período indefinido (cerca de um minuto). O equilíbrio pode ser inseguro, mas o corpo não cai da postura espinal ereta.",
    9: "ERGUE-SE SOZINHO (A). Chega a uma posição ereta segurando em algum objeto (não em uma pessoa), erguendo-se sozinho.",
    10: "FALA IMITA SONS. Tagarela ou usa conversa inarticulada, que revela aparente tentativa de imitar ou expressar palavras, como algo mais do que mero prazer na vocalização.",
    11: "BEBE EM XÍCARA OU COPO COM AUXÍLIO. Usa xícara ou copo para beber, auxiliado por alguém para segurar ou ajudar a segurar a xícara ou copo, e bebe sem derramar muito.",
    12: "MOVE-SE PELO ASSOALHO (ENGATINHA). Movimenta-se pelo chão por rastejos ou engatinhando, mas pode ser observado enquanto faz isso.",
    13: "AGARRA COM O POLEGAR E O DEDO. Opõe o polegar e o dedo, agarrando ou pegando algo, ao contrário do agarrar com o punho ou a palma inteira.",
    14: "SOLICITA ATENÇÃO PESSOAL. Demonstra desejo de ser abordado ou de ser posto em relação com outra pessoa de qualquer modo, tal como atraindo atenção para si ou para suas próprias atividades, além do mero manuseio ou cuidado das necessidades físicas.",
    15: "FICA DE PÉ SOZINHO (A). Fica em pé sem auxílio numa superfície dura, lisa, não segurando em objeto ou pessoa, por período indefinido (cerca de um minuto). O equilíbrio pode ser inseguro e pode apresentar movimentos dos pés, mas a postura total é mantida ereta.",
    16: "NÃO BABA. Tem o controle da saliva estabilizado, de modo que não requer comunmente que enxugue a boca ou o queixo.",
    17: "OBEDECE INSTRUÇÕES SIMPLES. Vem quando chamado, anda pequenas distâncias até pontos determinados conforme ordens; aponta para objetos especiais em figuras quando solicitado; faz pantomimas de nenê a pedido — em geral, coopera a pedidos verbais em atividades muito simples.",
    # ── 1 a 2 anos ───────────────────────────────────────────────────────────
    18: "ANDA PELO APOSENTO SEM AUXÍLIO. Anda pelo quarto, não meramente como um ato mecânico, mas como evidência de responsabilidade pessoal crescente. Pode exigir observação ou cuidados ocasionais.",
    19: "RABISCA COM LÁPIS PRETO OU DE COR. Distrai-se com crayon ou lápis durante curtos períodos: risca para cima e para baixo, de lado a lado, ou com movimentos circulares sem quebrar a ponta ou rasgar o papel. Faz isto espontaneamente ou a pedido, como meio de se ocupar.",
    20: "MASTIGA OS ALIMENTOS. Mastiga os alimentos sólidos ou semissólidos antes de engolir.",
    21: "TIRA AS MEIAS. Remove meias soquete, meias compridas ou sapatos sem auxílio, se desapertado, como um ato de se despir e não meramente com um significado de brinquedo.",
    22: "MUDA OBJETOS DE LUGAR. Despeja de um recipiente para o outro sem derramar; remove, transfere, muda de lugar objetos de uma maneira um pouco intencional; arranja objetos em um padrão ou ordem.",
    23: "TRANSPÕE OBSTÁCULOS SIMPLES. Abre portas fechadas, sobe cadeiras, usa banco para alcançar algo, usa bastão como instrumento; remove simples impedimentos; usa cesto ou receptáculos para carregar coisas.",
    24: "VAI BUSCAR OU CARREGA OBJETOS FAMILIARES. Desempenha recados a pedido, tais como: levar determinados objetos ou trazê-los de ou para outros lugares próximos, ou levar e trazer mensagens simples de ou para pessoas próximas.",
    25: "BEBE EM XÍCARA OU COPO SEM AUXÍLIO. Usa xícara ou copo, sem auxílio, para beber segurando na asa ou mantendo o copo com uma ou com as duas mãos, sem graves derramamentos.",
    26: "ABANDONA O CARRINHO DE BEBÊ. Não anda mais em carrinho de bebê. Caminha ou usa carrinho de andar quando sai.",
    27: "BRINCA COM OUTRAS CRIANÇAS. Brinca independentemente, sem criar antagonismo, em companhia de outros aproximadamente da mesma idade ou nível social. A atividade é mais individual do que cooperativa, mas ele se adapta com as outras crianças.",
    28: "COME COM COLHER. Usa colher à mesa ou na cadeira alta para comer na tigela, xícara ou prato, e faz isto sem ajuda e sem derramar muito.",
    29: "ANDA PELA CASA OU QUINTAL (OU JARDIM). Anda pela casa ou quintal somente com supervisão ocasional relacionadas aos lugares ou ações, e causa poucos problemas ao fazê-lo.",
    30: "DISTINGUE SUBSTÂNCIAS ALIMENTARES. Evita comer lixo, e facilmente distingue entre substâncias comuns adequadas ou inadequadas para comer, sem necessidade de selecioná-las. Pode morder objetos duros mas não requer vigilância neste sentido.",
    31: "USA NOME DE OBJETOS FAMILIARES. Usa nome de vários objetos familiares (não incluindo pessoas) para fins particulares; não só diz os nomes desses objetos apresentados, mas os pede ou se refere a eles pelo seu nome espontaneamente. Nomes podem ser substituídos por corruptelas de palavras corretas, mas devem ser mais do que sons meramente reconhecíveis.",
    32: "SOBE ESCADAS SEM AUXÍLIO. Sobe escadas sem ajuda; anda mais do que rasteja; pode se apoiar no corrimão ou muro (não em pessoas) e pode subir colocando os dois pés em cada degrau.",
    33: "DESEMBRULHA BALAS. Recebendo balas ou alimentos embrulhados, remove o invólucro, sem sugestão ou ajuda, antes de comer.",
    34: "FALA EM FRASES CURTAS. Usa pequenas sentenças ou frases ou combinações sujeito-objeto, com vocabulário de 25 palavras ou mais. A linguagem é praticamente útil dentro destes limites, e não mero papagaiamento.",
    # ── 2 a 3 anos ───────────────────────────────────────────────────────────
    35: "PEDE PARA IR AO BANHEIRO. Por atos ou palavras expressa a alguém o desejo de ir ao banheiro e raramente tem, durante o dia, 'acidentes'. Pode ser auxiliado no banheiro.",
    36: "INICIA SEUS PRÓPRIOS JOGOS INFANTIS. Ocupa-se com brincadeiras ou atividades semelhantes, de própria iniciativa ou por simples sugestões, tais como desenhar ou pintar com lápis ou crayon, construir com blocos, vestir bonecas, olhar livros ou desenhos. Pode fazê-lo com outros mas não exige supervisão.",
    37: "TIRA O CASACO COM A ROUPA. Tira o próprio casaco, roupa ou sobretudo sem auxílio quando o mesmo está desabotoado.",
    38: "COME COM GARFO. Usa garfo sem derramar muito, para comer alimento sólido que não requer que se corte.",
    39: "BEBE ÁGUA SEM AUXÍLIO. Quando deseja beber é capaz de fazê-lo em circunstâncias comuns em ambientes familiares, sem auxílio, obtendo xícaras ou copo se acessível, abrindo e fechando a torneira sem graves riscos ou desordens.",
    40: "ENXUGA AS PRÓPRIAS MÃOS. Enxuga as próprias mãos aceitavelmente sem auxílio. As mãos podem ser lavadas para ele.",
    41: "EVITA PERIGOS SIMPLES. Abriga-se da chuva, literal ou figuradamente falando. Mostra algumas precauções a respeito de estranhos; é cuidadoso evitando cair de escadas ou lugares altos; evita perigos de objetos tais como fósforos, utensílios afiados, vidros; não sai à rua; é precavido com animais.",
    42: "PÕE O CASACO OU A ROUPA SEM AUXÍLIO. Veste sem ajuda o próprio casaco, roupa ou sobretudo, mas que não precisem ser abotoados.",
    43: "USA TESOURA PARA CORTAR. Usa tesoura sem ponta ao cortar papel ou pano. Assim o faz seguramente e sem perigo, sem fazer estragos, mas pode ser supervisionado.",
    44: "CONTA SUAS EXPERIÊNCIAS. Dá simples relatórios de experiências ou conta histórias (espontaneamente) com sequência, conteúdo coerente e detalhes relevantes. A forma do vocabulário e da linguagem não são tão importantes como a continuidade do relato.",
    # ── 3 a 4 anos ───────────────────────────────────────────────────────────
    45: "DESCE ESCADA COM UM PÉ EM CADA DEGRAU. Desce escada um passo por andar sem ajuda.",
    46: "BRINCA COOPERATIVAMENTE AO NÍVEL DE JARDIM DE INFÂNCIA. Participa de atividades coordenadas de grupo, tais como brincar de roda, brinquedos de imaginação de grupo, chás ou atividades onde é exigida a ação mútua ou recíproca.",
    47: "ABOTOA CASACO OU VESTIDO. Veste seu próprio casaco, roupa ou sobretudo e abotoa os mesmos sem ajuda.",
    48: "AJUDA EM PEQUENOS TRABALHOS CASEIROS. 'Ajuda' em pequenas coisas pela casa, tais como: levar recados, guardar coisas, pôr e tirar a mesa, dar comida aos animais, tirar pó.",
    49: "REPRESENTA PARA OS OUTROS. Faz certas proezas de imaginação ou para entretenimento dos outros tais como: recitar, cantar, dançar, de uma maneira suficientemente meritória para ser mais do que apenas 'engraçadinho'.",
    50: "LAVA AS MÃOS SOZINHO. Lava as próprias mãos aceitavelmente, sem auxílio, e enxuga as mesmas sem sujar a toalha.",
    # ── 4 a 5 anos ───────────────────────────────────────────────────────────
    51: "CUIDA-SE NO BANHEIRO. Vai ao banheiro só, sem ajuda. Tira e põe as próprias roupas (pode requerer ajuda para abotoar os botões das costas) e desempenha outras operações necessárias. Não há acidentes durante o dia.",
    52: "LAVA O ROSTO SOZINHO. Lava seu próprio rosto (exceto orelhas) aceitavelmente e enxuga sem auxílio.",
    53: "ANDA PELA VIZINHANÇA SOZINHO. Anda pela vizinhança imediata sem supervisão. Pode receber restrições quanto a áreas ou limites, e pode ser requerido um conhecimento dos lugares frequentados ou atividades, mas no fundo está sozinho, é livre dentro destes limites.",
    54: "VESTE-SE MAS NÃO AMARRA. Veste-se sozinho exceto os cordões, fitas ou laços. Abotoa de forma comum. As roupas são separadas ou designadas. Recebe ajuda para vestir cachecol, capa ou galochas quando vai sair, e roupas especialmente difíceis tais como sobretudo ou macacão.",
    55: "DESENHA COM LÁPIS OU CRAYON. Desenha com lápis ou crayon e produz formas simples mas reconhecíveis, tais como: homem, casa, árvore, animal, paisagem. Utiliza colorações detalhadas ou diferenciais.",
    56: "BRINCA COM JOGOS COMPETITIVOS. Toma parte em jogo competitivo ativo em pequenos grupos de 3 ou 4 da mesma idade. Ex.: pegador, esconde-esconde, pião, pular corda, estátua.",
    # ── 5 a 6 anos ───────────────────────────────────────────────────────────
    57: "USA PATINS CARRINHOS. Toma conta de si mesmo, sem supervisão, fora do próprio quintal quando usa patins, trenó, carrinho, velocípede, patinete e brinquedos semelhantes que envolvam algum perigo.",
    58: "ESCREVE (LETRA DE FORMA) PALAVRA SIMPLES. Escreve legivelmente seu primeiro nome ou algumas palavras familiares de três ou quatro letras, sem copiar. Assim o faz de própria iniciativa ou por ditado. Não é essencial escrever certo.",
    59: "BRINCA COM JOGOS DE MESA SIMPLES. Joga com os outros, jogos de mesa que requerem rodízio, observando regras, levando em conta as metas e o faz sem discussão (dominó, xadrez, etc.).",
    60: "CONFIAM-LHE DINHEIRO. É responsável por pequenas quantidades de dinheiro quando mandado a fazer pagamentos ou compras especificadas. É cuidadoso com a mesma e a usa como solicitado. Habilidades para fazer trocos não é necessária.",
    61: "VAI À ESCOLA SOZINHO. Sai para a escola ou outro lugar familiar fora da vizinhança imediata sozinho. Pode ir em companhia de amigos, mas ninguém é diretamente responsável por ele.",
    # ── 6 a 7 anos ───────────────────────────────────────────────────────────
    62: "USA FACA PARA ESPALHAR. Usa faca de mesa em circunstâncias comuns para passar manteiga ou geleia no pão.",
    63: "USA LÁPIS PARA ESCREVER. Escreve (não em letra de forma) legivelmente com lápis uma dúzia ou mais de palavras simples, com grafia correta. Assim o faz de própria iniciativa ou por ditado, mas não copiando.",
    64: "TOMA BANHO COM AUXÍLIO. Toma banho supervisionado. Pode ser ajudado ao preparar o banho, ao lavar e secar o cabelo, e nos retoques.",
    65: "VAI PARA CAMA SOZINHO. Desempenha as operações para dormir sem ajuda; vai para o quarto sozinho; despe-se, vai ao banheiro, apaga a luz, etc. de acordo com a rotina familiar. Pode ser acompanhado ou 'pajeado' por questões de sentimentalismo, mas realmente não necessita nenhuma ajuda ou companhia.",
    # ── 7 a 8 anos ───────────────────────────────────────────────────────────
    66: "VÊ AS HORAS DE 15 EM 15 MINUTOS. Lê os relógios comuns com aproximação ao quarto de hora mais próximo e realmente usa relógios com finalidades práticas.",
    67: "USA FACA PARA CORTAR. Usa faca para cortar carne. Pode ser auxiliado ocasionalmente com carne dura ou difícil, tal como carne com ossos ou de galinha.",
    68: "NÃO ACREDITA EM PAPAI-NOEL. Rejeita o conceito antropomórfico, mas pode reter o conceito emocional ou simbólico; também rejeita outros conceitos anímicos como fadas, coelhos de páscoa e personificação de objetos ou acontecimentos.",
    69: "PARTICIPA DE JOGOS PRÉ-ADOLESCENTES. Meninos: participa de jogo cooperativo em grupo que não requer uma habilidade definida e tem apenas regras brandas, tais como futebol, bola ao cesto ou basebol desorganizado. Meninas: participa de representações dramáticas simbolizando situações domésticas ou sociais, tais como: brincar de casinha, escola, médico, enfermeira, loja.",
    70: "PENTEIA-SE E ESCOVA OS CABELOS. Escova ou penteia o cabelo aceitavelmente sem ajuda ou correção quando se veste, sai ou receber conhecidos.",
    # ── 8 a 9 anos ───────────────────────────────────────────────────────────
    71: "USA FERRAMENTAS OU UTENSÍLIOS. Faz algum uso prático de instrumentos ou utensílios simples tais como: martelo, serra, chave de fenda, utensílios domésticos ou de costura, ferramentas para jardim.",
    72: "FAZ TRABALHOS CASEIROS DE ROTINA. Ajuda efetivamente em trabalhos simples em casa que são de rotina e pelos quais assume alguma responsabilidade contínua, tais como: tirar o pó, arrumar, limpar, lavar pratos, pôr ou tirar a mesa, fazer a cama.",
    73: "LÊ POR SUA PRÓPRIA INICIATIVA. Faz uso independente e eficiente do material simples de leitura (mais ou menos no quarto ano), tais como: trechos cômicos, títulos de filmes, histórias simples, notas, instruções simples, novos itens elementares para o próprio entretenimento ou informação.",
    74: "TOMA BANHO SOZINHO. Toma banho aceitavelmente sem ajuda: despe-se, prepara-se para a banheira ou chuveiro. Lava-se e enxuga-se sem necessidade de retoque, não incluindo lavar e enxugar o cabelo.",
    # ── 9 a 10 anos ──────────────────────────────────────────────────────────
    75: "CUIDA-SE À MESA. Cuida-se de suas próprias necessidades à mesa: serve-se de acordo com suas necessidades; em geral sabe lidar com coisas como: batatas assadas, carnes difíceis, ovos cozidos, etc.",
    76: "FAZ PEQUENAS COMPRAS. Compra artigos úteis escolhendo ou selecionando e é responsável pela segurança dos artigos, do dinheiro e do troco correto. O faz independentemente ou pode seguir ordens explícitas.",
    77: "ANDA LIVREMENTE PELA CIDADE. Anda pela cidade sozinho ou com amigos, fora da vizinhança imediata indo a pontos específicos. Pode ser restringido a áreas ou limites, porém estes são mais remotos do que a vizinhança próxima.",
    # ── 10 a 11 anos ─────────────────────────────────────────────────────────
    78: "ESCREVE OCASIONALMENTE CARTAS CURTAS. De vez em quando escreve cartas resumidas a amigos ou parentes, por iniciativa própria ou seguindo algumas sugestões e o faz sem ajuda, com exceção quanto à grafia de palavras não comuns e do fornecimento de endereços desconhecidos. Subscreve envelopes e providencia o seu envio.",
    79: "FAZ CHAMADAS TELEFÔNICAS. Usa telefones locais para fins práticos, procura os números, faz ligações e mantém de modo eficiente conversações úteis, não incluindo chamadas interurbanas.",
    80: "FAZ PEQUENOS TRABALHOS REMUNERADOS. Efetua trabalhos ocasionais ou intermitentes, de própria iniciativa, em casa ou vizinhança, pelos quais são-lhe pagas pequenas somas ou as quais merecem pagamento, tais como: trabalhos avulsos, cuidar da casa, ajudar a cuidar de crianças, costurar, vender revistas, carregar jornais.",
    81: "RESPONDE A ANÚNCIOS; FAZ COMPRAS PELO CORREIO. Responde a revistas, rádio ou outra propaganda enviando cupons, pedindo amostras, solicitando literatura, fazendo compras por catálogos.",
    # ── 11 a 12 anos ─────────────────────────────────────────────────────────
    82: "REALIZA TRABALHOS CRIATIVOS SIMPLES. Faz coisas úteis, consertos simples ou trabalho produtivo: cozinha, assa, ou costura um pouco, faz um pouco de jardinagem, cuida de animais, escreve pequenas histórias ou poemas, faz desenhos ou pinturas simples.",
    83: "É DEIXADO À SÓS PARA CUIDAR DE SI OU DE OUTROS. É às vezes deixado sozinho, ou sua própria responsabilidade, por uma hora ou mais em casa ou no trabalho e é bem sucedido, tratando de suas necessidades imediatas ou das pessoas deixadas ao seu cuidado.",
    84: "GOSTA DE LIVROS, JORNAIS E REVISTAS. Lê para informações práticas ou para seu agrado pessoal, histórias ou notícias nos jornais, revistas de histórias, livros de biblioteca, histórias de aventuras ou romances.",
    # ── 12 a 15 anos ─────────────────────────────────────────────────────────
    85: "ENTREGA-SE A JOGOS DIFÍCEIS. Participa de jogos relativamente complexos e especializados e de esportes como jogos de cartas, beisebol, bola ao cesto, tênis, natação. Compreende as regras e os processos de contagem.",
    86: "CUIDA-SE COMPLETAMENTE QUANTO À ROUPA. Requer raramente auxílio quanto aos cuidados pessoais, incluindo lavagem e secagem de cabelos, cuidados das unhas, barbear-se (se tiver barba), escolha de roupa de acordo com a ocasião e o tempo. Amarra gravata, fitas ou laços.",
    87: "COMPRA OS PRÓPRIOS ACESSÓRIOS DE VESTUÁRIO. Escolhe e compra com o cuidado de ver a utilidade, o preço e o tamanho, pequenos artigos de roupa pessoal tais como: fitas, gravatas, roupas de baixo, sapatos, etc. — não incluindo ternos, vestidos, paletós, chapéus. Autoridade e dinheiro ou crédito pode ser fornecido por pessoas mais velhas.",
    88: "PARTICIPA EM ATIVIDADES DE GRUPOS DE ADOLESCENTES. É membro ativo de um grupo comunitário, time esportivo, clube, organização social ou literária. Planeja e participa de danças, festas, excursões, esportes ao ar livre, etc., em grupos representando um conjunto social de idades e interesses similares, sem liderança de adulto.",
    89: "REALIZA AFAZERES ROTINEIROS DE SUA RESPONSABILIDADE. É responsável para desempenhar trabalhos periódicos e variáveis, tais como as tarefas familiares: servir à mesa, ajudar nos trabalhos caseiros, cuidar do jardim, limpar o carro, lavar janelas.",
    # ── 15 a 18 anos ─────────────────────────────────────────────────────────
    90: "COMUNICA-SE POR CARTA. Escreve cartas comerciais ou sociais que são mais que superficiais e que exigem comunicação de informações sérias, troca de notícias importantes, dando ou conhecendo instruções.",
    91: "ACOMPANHA ACONTECIMENTOS CORRENTES. Discute notícias gerais, esportes, acontecimentos sensacionais, e segue tais coisas com alguma continuidade.",
    92: "VAI SOZINHO A LUGARES PRÓXIMOS (FORA DOS LIMITES DA CIDADE). Sai dos limites da cidade natal e é pessoalmente responsável pelos próprios preparativos ao fazê-lo. É livre, não meramente seguindo direções explícitas ou indo de um ponto conhecido a outro e voltando. A distância percorrida não precisa ser grande, mas as áreas são relativamente não familiares.",
    93: "SAI DESACOMPANHADO DURANTE O DIA. Sai de casa durante o dia sem 'supervisão à distância' e é pessoalmente responsável por seus movimentos sem prestar contas dos mesmos com antecedência. Ao fazê-lo revela comportamento discreto.",
    94: "DISPÕE DE DINHEIRO PRÓPRIO PARA GASTAR. Tem um dinheiro suficiente para gastar (por semana, mesada ou ganho) e usa o mesmo com razoável discrição para necessidades pessoais significativas, mais do que para mero entretenimento imediato.",
    95: "COMPRA TODAS AS SUAS ROUPAS. Usualmente escolhe e compra sua própria roupa, incluindo vestidos, ternos, casacos, chapéus. Pode ser assistido ou aconselhado, mas toma suas decisões finais e faz os pagamentos, mesmo que o dinheiro ou crédito tenha que ser fornecido em vez de ganho.",
    96: "VAI SOZINHO A LUGARES DISTANTES. Vai a cidades ou lugares estranhos ou relativamente remotos, desacompanhado (não aos cuidados de alguém) e para isso faz ele mesmo os preparativos, sem instruções específicas. É cuidadoso com perigos ordinários e enfrenta emergências ordinárias com sucesso ao fazê-lo.",
    97: "CUIDA DA PRÓPRIA SAÚDE. Cuida da própria saúde por vontade própria, observando as regras de higiene comuns, doenças contagiosas ou infecciosas, doenças agudas e acidentes, cuidando de si nas doenças menores e obtendo assistência profissional se preciso.",
    98: "TEM EMPREGO OU CONTINUA A ESTUDAR. Está vantajosamente empregado em ocupações como: trabalhador fabril, empregado, serviços em fazendas, trabalhador comum, barbeiro, auxiliar de artesanato, dona de casa (concessão feita para desemprego devido a circunstâncias especiais). Ou continua estudando depois do ginásio.",
    99: "SAI À NOITE SEM RESTRIÇÕES. É responsável pelas próprias ações depois que escurece, sem avisar com antecedência, e não se vê em problemas. É livre de ir e vir à noite, mas deve avisar de sua ausência antes ou depois, como cortesia ou formalismo. Pode ser solicitado a chegar com hora determinada.",
    100: "CONTROLA SEUS PRINCIPAIS GASTOS. Tem critérios próprios para efetuar gastos maiores de mesadas, ganhos ou rendimentos, apenas com conselhos gerais dos outros de como usar o dinheiro.",
    101: "ASSUME RESPONSABILIDADE PESSOAL. Dirige seus próprios compromissos sociais, mas leva em conta o bem estar dos outros ao fazê-lo. Age de livre arbítrio (julgamento e previsão) nas atividades pessoais.",
    # ── 20 a 25 anos ─────────────────────────────────────────────────────────
    102: "EMPREGA PREVIDENTEMENTE O DINHEIRO. Vive dentro de um rendimento, quita suas obrigações financeiras prontamente, evita desperdício e extravagâncias dentro de um nível de vida prudentemente relacionado com rendimentos, receitas e obrigações. Os gastos são para projetos sérios mais do que para causas frívolas.",
    103: "ASSUME RESPONSABILIDADE ALÉM DO QUE LHE É NECESSÁRIO. Contribui para o sustento de outros, 'é um bom vizinho', participa da responsabilidade de outros.",
    104: "CONTRIBUI PARA O BEM ESTAR SOCIAL. Participa do trabalho social local, ou atividade de natureza altruística e assim faz de iniciativa própria; dá ajuda pessoal ou financeira para grupos sociais como: igreja, escola e organizações de caridade. É membro ativo de clubes ou grupos sociais semi-profissionais como Associação de Pais e Mestres, corporação religiosa, organização ocupacional ou política.",
    105: "É PREVIDENTE QUANTO AO FUTURO. Mantém independência econômica. Prevê futuras necessidades ou vantagens, pondo de lado parte significante do rendimento ou recursos em economias, seguro, investimento, etc. Compra a crédito a própria casa, mobília, faz previsão para o ensino superior dos filhos e outros gastos em investimentos que tenham valor de moeda corrente. Adia satisfações imediatas, por benefícios remotos.",
    # ── 25 anos ou mais ──────────────────────────────────────────────────────
    106: "REALIZA TRABALHOS ESPECIALIZADOS. Está empregado como diarista em ocupações habilidosas (técnicos ou de escritório) ou de supervisão, tais como: escriturário, artesão, enfermeira, sitiante, pequeno comerciante, capataz, empregada doméstica. Ou continua os estudos no nível superior.",
    107: "ENTREGA-SE A RECREAÇÕES BENÉFICAS. Faz uso aproveitável do tempo vago para salvaguardar ou melhorar o bem estar mental e físico com leituras, jogos e esportes, 'hobbies', jardinagem, música, arte, teatro. (Recreações meramente passivas, distrações de baixo nível mental ou ocupações para matar o tempo não devem ser creditadas.)",
    108: "SISTEMATIZA O PRÓPRIO TRABALHO. Trabalha com iniciativa própria com o sistema capaz de promover um uso mais eficiente de habilidades e oportunidades. Faz seu programa de trabalho de maneira que possa ter despesas imprevistas, e o segue tendo em vista aumentar a quantidade, qualidade e a variedade de trabalho. Usa novos engenhos e métodos para aumentar a eficácia do trabalho.",
    109: "INSPIRA CONFIANÇA. É apoio em tempos de aflição ou necessidade, ajuda em tempo de emergência. É consultado em assuntos que requerem liderança ou bom julgamento. Ocupa posição de confiança na sociedade.",
    110: "PROMOVE O PROGRESSO CÍVICO. Toma parte ativa no melhoramento de movimentos cívicos, comerciais, sociais, industriais, educacionais além da rotina ocupacional imediata. É um membro proeminente de grupo operacional, profissional, fraternal, cívico, religioso ou outro grupo que contribua para o bem estar público.",
    111: "SUPERVISIONA ATIVIDADES PROFISSIONAIS. Dirige negócio próprio acima do nível dos pequenos mercados, ou mantém posição de pequena capacidade executiva mais alta do que o lugar de capataz em trabalho de rotina.",
    112: "FAZ COMPRAS PARA OUTROS. Faz ou aprova grandes compras, fora das próprias necessidades ou das necessidades domésticas dos dependentes, como agente para os outros, envolvendo responsabilidade e escolha crítica, com arbítrio maduro quanto à convivência e custo.",
    113: "DIRIGE OU ORIENTA TRABALHOS DE OUTROS. Mantém posição executiva superior ou de supervisão técnica ou emprega vários trabalhadores por sua própria conta. Planeja e organiza o trabalho dos outros de modo mais amplo.",
    114: "REALIZA TRABALHO TÉCNICO OU PROFISSIONAL. Produz trabalhos altamente habilidosos ou executivos acima do nível de diaristas ou consegue carreira profissional, literária ou artística de alto mérito.",
    115: "COMPARTILHA DE RESPONSABILIDADE NA VIDA DA COMUNIDADE. Participa da direção geral de grandes empreendimentos. Ex.: membro do conselho de diretores de importantes organizações de negócios, sociais, educacionais, institucionais ou cívicos. Ocupa posição importante de confiança pública.",
    116: "CRIA AS PRÓPRIAS OPORTUNIDADES. Domina o ambiente e executa seus próprios planos, designa a maneira de fazer certas coisas, contribui com ideias, sai da rotina aceita, tem sucesso ao desenvolver novos descobrimentos, operações melhoradas, direção mais eficiente. Sustenta as atividades criativas ou de organizações durante um período apreciável de anos.",
    117: "CONTRIBUI PARA O BEM ESTAR GERAL. Obteve amplo reconhecimento como alguém que promove progresso público em campos filantrópicos, religiosos, educacionais, culturais, industriais e patrióticos.",
}

VINELAND_OPCOES = [
    ("sim_sempre", "Sim, sempre", "+", 1.0),
    ("sim_as_vezes", "Sim, às vezes", "±", 0.5),
    ("nao_nunca", "Não, nunca", "−", 0.0),
    ("nao_oportunidade", "Não teve oportunidade", "NTO", 0.0),
    ("nao_sei", "Não sei", "NS", 0.0),
]

VINELAND_CATEGORIAS_CONFIG = {
    "C":   {"nome": "Comunicação",           "max": 15},
    "L":   {"nome": "Locomoção",              "max": 10},
    "O":   {"nome": "Ocupação",               "max": 22},
    "S":   {"nome": "Socialização",           "max": 17},
    "AG":  {"nome": "Autogoverno",            "max": 14},
    "AGE": {"nome": "Auto-auxílio geral",     "max": 13},
    "AC":  {"nome": "Auto-auxílio p/ comer",  "max": 12},
    "AV":  {"nome": "Auto-auxílio p/ vestir", "max": 13},
}

QS_CLASSIFICACAO = [
    (130, None,  "Muito Superior"),
    (120, 129,   "Superior"),
    (110, 119,   "Médio Superior"),
    (90,  109,   "Médio"),
    (80,  89,    "Médio Inferior"),
    (70,  79,    "Limítrofe"),
    (0,   69,    "Deficiente Mental"),
]


def calcular_pontuacao_vineland(respostas: dict) -> dict:
    """
    respostas: {numero_item: valor_str}
    Retorna dict com pontuação total e por categoria.
    """
    PONTOS = {"sim_sempre": 1.0, "sim_as_vezes": 0.5}
    total = 0.0
    por_categoria = {k: 0.0 for k in VINELAND_CATEGORIAS_CONFIG}

    for item, valor in respostas.items():
        pts = PONTOS.get(valor, 0.0)
        total += pts
        cat = VINELAND_CATEGORIA.get(item)
        if cat and cat in por_categoria:
            por_categoria[cat] += pts

    return {"total": total, **por_categoria}


def classificar_qs(qs: float) -> str:
    for low, high, label in QS_CLASSIFICACAO:
        if high is None and qs >= low:
            return label
        if high is not None and low <= qs <= high:
            return label
    return "—"
