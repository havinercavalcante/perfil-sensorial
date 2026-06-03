# BDI — Inventário de Depressão de Beck (21 itens, 0–3 cada)
# Pontos de corte: 0–9 mínimo, 10–16 leve, 17–29 moderado, 30–63 grave

BDI_ITENS = [
    {"numero":  1, "texto": "Tristeza",                  "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não me sinto triste"},
         {"valor": 1, "label": "Eu me sinto triste"},
         {"valor": 2, "label": "Estou sempre triste e não consigo sair disso"},
         {"valor": 3, "label": "Estou tão triste ou infeliz que não consigo suportar"},
     ]},
    {"numero":  2, "texto": "Pessimismo",                "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não estou especialmente desanimado(a) quanto ao futuro"},
         {"valor": 1, "label": "Eu me sinto desanimado(a) quanto ao futuro"},
         {"valor": 2, "label": "Acho que nada tenho a esperar"},
         {"valor": 3, "label": "Acho o futuro sem esperança e tenho a impressão de que as coisas não podem melhorar"},
     ]},
    {"numero":  3, "texto": "Sensação de fracasso",      "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não me sinto um fracasso"},
         {"valor": 1, "label": "Acho que fracassei mais do que uma pessoa comum"},
         {"valor": 2, "label": "Quando olho para trás, na minha vida, tudo que posso ver é um monte de fracassos"},
         {"valor": 3, "label": "Acho que, como pessoa, sou um completo fracasso"},
     ]},
    {"numero":  4, "texto": "Insatisfação",              "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Tenho tanto prazer em tudo como antes"},
         {"valor": 1, "label": "Não me sinto mais tão satisfeito(a) com as coisas como costumava"},
         {"valor": 2, "label": "Não tenho mais prazer real em coisa alguma"},
         {"valor": 3, "label": "Estou insatisfeito(a) ou entediado(a) com tudo"},
     ]},
    {"numero":  5, "texto": "Culpa",                     "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não me sinto especialmente culpado(a)"},
         {"valor": 1, "label": "Eu me sinto culpado(a) grande parte do tempo"},
         {"valor": 2, "label": "Eu me sinto culpado(a) na maior parte do tempo"},
         {"valor": 3, "label": "Eu me sinto sempre culpado(a)"},
     ]},
    {"numero":  6, "texto": "Punição",                   "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não acho que esteja sendo punido(a)"},
         {"valor": 1, "label": "Acho que posso ser punido(a)"},
         {"valor": 2, "label": "Creio que serei punido(a)"},
         {"valor": 3, "label": "Acho que estou sendo punido(a)"},
     ]},
    {"numero":  7, "texto": "Auto-aversão",              "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não me sinto decepcionado(a) comigo mesmo(a)"},
         {"valor": 1, "label": "Estou decepcionado(a) comigo mesmo(a)"},
         {"valor": 2, "label": "Estou enojado(a) de mim mesmo(a)"},
         {"valor": 3, "label": "Eu me odeio"},
     ]},
    {"numero":  8, "texto": "Auto-acusação",             "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não me culpo mais do que o habitual"},
         {"valor": 1, "label": "Sou mais crítico(a) em relação a mim mesmo(a) do que costumava ser"},
         {"valor": 2, "label": "Critico-me por todas as minhas falhas"},
         {"valor": 3, "label": "Culpo-me por tudo de ruim que acontece"},
     ]},
    {"numero":  9, "texto": "Ideias suicidas",           "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não tenho nenhum pensamento de me matar"},
         {"valor": 1, "label": "Tenho pensamentos de me matar, mas não os levaria a cabo"},
         {"valor": 2, "label": "Gostaria de me matar"},
         {"valor": 3, "label": "Eu me mataria se tivesse oportunidade"},
     ]},
    {"numero": 10, "texto": "Choro",                     "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não choro mais do que o habitual"},
         {"valor": 1, "label": "Choro mais do que costumava"},
         {"valor": 2, "label": "Fico chorando o tempo todo agora"},
         {"valor": 3, "label": "Costumava conseguir chorar, mas agora não consigo, mesmo querendo"},
     ]},
    {"numero": 11, "texto": "Irritabilidade",            "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não sou mais irritado(a) agora do que já fui"},
         {"valor": 1, "label": "Fico aborrecido(a) ou irritado(a) mais facilmente do que costumava"},
         {"valor": 2, "label": "Atualmente me sinto irritado(a) o tempo todo"},
         {"valor": 3, "label": "Absolutamente não me irrito com as coisas que costumavam me aborrecer"},
     ]},
    {"numero": 12, "texto": "Afastamento social",        "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não perdi o interesse nas outras pessoas"},
         {"valor": 1, "label": "Estou menos interessado(a) nas outras pessoas do que costumava estar"},
         {"valor": 2, "label": "Perdi a maior parte do meu interesse nas outras pessoas"},
         {"valor": 3, "label": "Perdi todo o interesse nas outras pessoas"},
     ]},
    {"numero": 13, "texto": "Indecisão",                 "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Tomo decisões tão bem quanto antes"},
         {"valor": 1, "label": "Eu adio as tomadas de decisões mais do que costumava"},
         {"valor": 2, "label": "Tenho mais dificuldade de tomar decisões do que antes"},
         {"valor": 3, "label": "Absolutamente não consigo mais tomar decisões"},
     ]},
    {"numero": 14, "texto": "Imagem corporal negativa",  "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não acho que minha aparência seja pior do que costumava ser"},
         {"valor": 1, "label": "Estou preocupado(a) em parecer velho(a) ou sem atrativo"},
         {"valor": 2, "label": "Acho que há mudanças permanentes na minha aparência que me tornam sem atrativo"},
         {"valor": 3, "label": "Acredito que sou feio(a)"},
     ]},
    {"numero": 15, "texto": "Inibição do trabalho",      "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Posso trabalhar tão bem quanto antes"},
         {"valor": 1, "label": "É preciso algum esforço extra para fazer alguma coisa"},
         {"valor": 2, "label": "Tenho que me esforçar muito para fazer alguma coisa"},
         {"valor": 3, "label": "Não consigo mais fazer trabalho algum"},
     ]},
    {"numero": 16, "texto": "Insônia",                   "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Consigo dormir tão bem quanto antes"},
         {"valor": 1, "label": "Não durmo tão bem quanto costumava"},
         {"valor": 2, "label": "Acordo 1-2 horas mais cedo do que habitualmente e tenho dificuldade de voltar a dormir"},
         {"valor": 3, "label": "Acordo várias horas antes do habitual e não volto a dormir"},
     ]},
    {"numero": 17, "texto": "Fatigabilidade",            "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não fico mais cansado(a) do que o habitual"},
         {"valor": 1, "label": "Fico cansado(a) com mais facilidade do que costumava"},
         {"valor": 2, "label": "Fico cansado(a) quando faço quase qualquer coisa"},
         {"valor": 3, "label": "Estou cansado(a) demais para fazer qualquer coisa"},
     ]},
    {"numero": 18, "texto": "Perda de apetite",          "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Meu apetite não é pior do que o habitual"},
         {"valor": 1, "label": "Meu apetite não é tão bom quanto costumava ser"},
         {"valor": 2, "label": "Meu apetite é muito pior agora"},
         {"valor": 3, "label": "Não tenho mais nenhum apetite"},
     ]},
    {"numero": 19, "texto": "Perda de peso",             "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não tenho perdido muito peso, se é que perdi algum"},
         {"valor": 1, "label": "Perdi mais de 2 kg"},
         {"valor": 2, "label": "Perdi mais de 4 kg"},
         {"valor": 3, "label": "Perdi mais de 6 kg (estou tentando perder peso de propósito)"},
     ]},
    {"numero": 20, "texto": "Hipocondria",               "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não estou mais preocupado(a) com minha saúde do que o habitual"},
         {"valor": 1, "label": "Estou preocupado(a) com problemas físicos como dores e perturbações do estômago, ou prisão de ventre"},
         {"valor": 2, "label": "Estou muito preocupado(a) com problemas físicos e é difícil pensar em muitas outras coisas"},
         {"valor": 3, "label": "Estou tão preocupado(a) com meus problemas físicos que não consigo pensar em qualquer outra coisa"},
     ]},
    {"numero": 21, "texto": "Libido",                    "subescala": "total",
     "opcoes": [
         {"valor": 0, "label": "Não notei qualquer mudança recente no meu interesse por sexo"},
         {"valor": 1, "label": "Estou menos interessado(a) por sexo do que costumava"},
         {"valor": 2, "label": "Estou muito menos interessado(a) por sexo atualmente"},
         {"valor": 3, "label": "Perdi completamente o interesse por sexo"},
     ]},
]

BDI_SUBESCALAS = {
    "total": {"nome": "Pontuação Total", "itens": list(range(1, 22)), "cor": "#6C3483", "campo": "pont_total"},
}

BDI_OPCOES = None  # cada item tem suas próprias opções

BDI_CORTE = {
    "total": [
        ("Mínimo",   0,  9),
        ("Leve",    10, 16),
        ("Moderado",17, 29),
        ("Grave",   30, 63),
    ],
}
