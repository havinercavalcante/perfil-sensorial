# Questionário de Dependência Emocional
# 23 itens, escala 1–6 (Nunca / Raramente / Poucas vezes / Muitas vezes / Frequentemente / Sempre)
# 6 subescalas: ansiedade_separacao, expressao_afetiva, modificacao_planos,
#               miedo_soledad, expresion_limite, busqueda_atencion
# Pontuação: soma bruta por subescala; maior pontuação = maior dependência

DEP_EMOCIONAL_ITENS = [
    {"numero":  1, "texto": "Me sinto desamparado(a) quando estou sozinho(a)",               "subescala": "ansiedade_separacao"},
    {"numero":  2, "texto": "Me preocupa muito a ideia de ser abandonado(a) pela pessoa que amo", "subescala": "ansiedade_separacao"},
    {"numero":  3, "texto": "Para mim seria aterrorizante que a pessoa que amo não gostasse mais de mim", "subescala": "ansiedade_separacao"},
    {"numero":  4, "texto": "Seria muito difícil para mim continuar com minha vida sem o(a) meu(minha) parceiro(a)", "subescala": "ansiedade_separacao"},
    {"numero":  5, "texto": "Quando me separo brevemente da pessoa que amo, sinto-me nervoso(a) ou ansioso(a)", "subescala": "ansiedade_separacao"},
    {"numero":  6, "texto": "Necessito fazer muitas coisas para agradar à pessoa que amo",   "subescala": "expressao_afetiva"},
    {"numero":  7, "texto": "Necessito constantemente a atenção do(a) meu(minha) parceiro(a)", "subescala": "expressao_afetiva"},
    {"numero":  8, "texto": "Para atrair o(a) meu(minha) parceiro(a), chego a fazer coisas que me agradam ou que me custam trabalho", "subescala": "expressao_afetiva"},
    {"numero":  9, "texto": "Sou uma pessoa necessitada e dependente",                       "subescala": "expressao_afetiva"},
    {"numero": 10, "texto": "Tenho tentado ser a melhor pessoa possível para o(a) meu(minha) parceiro(a)", "subescala": "expressao_afetiva"},
    {"numero": 11, "texto": "Renunciei a alguma atividade importante para mim por passar mais tempo com o(a) meu(minha) parceiro(a)", "subescala": "modificacao_planos"},
    {"numero": 12, "texto": "Tenho me afastado dos meus amigos para estar disponível para o(a) meu(minha) parceiro(a)", "subescala": "modificacao_planos"},
    {"numero": 13, "texto": "Modifico os meus planos quando o(a) meu(minha) parceiro(a) tem algo diferente planejado", "subescala": "modificacao_planos"},
    {"numero": 14, "texto": "Venho descuidando de alguns aspectos da minha vida por estar mais tempo com o(a) meu(minha) parceiro(a)", "subescala": "modificacao_planos"},
    {"numero": 15, "texto": "Prefiro ceder nos meus interesses para agradar o(a) meu(minha) parceiro(a)", "subescala": "modificacao_planos"},
    {"numero": 16, "texto": "Quando discuto com o(a) meu(minha) parceiro(a), fico muito preocupado(a) em não perder o relacionamento", "subescala": "miedo_soledad"},
    {"numero": 17, "texto": "Se o(a) meu(minha) parceiro(a) rompe o relacionamento comigo, sinto que minha vida perdeu o sentido", "subescala": "miedo_soledad"},
    {"numero": 18, "texto": "Me sinto muito mal se o(a) meu(minha) parceiro(a) não está comigo",         "subescala": "miedo_soledad"},
    {"numero": 19, "texto": "Tenho tentado que o(a) meu(minha) parceiro(a) não rompa comigo através de choro, ameaças, ou outras ações", "subescala": "expresion_limite"},
    {"numero": 20, "texto": "Quando o(a) meu(minha) parceiro(a) me trata mal, continuo me apegando mais a ele(ela)", "subescala": "expresion_limite"},
    {"numero": 21, "texto": "Para conseguir a atenção do(a) meu(minha) parceiro(a), chego a fazer coisas como fingir uma doença", "subescala": "busqueda_atencion"},
    {"numero": 22, "texto": "Quero ter toda a atenção do(a) meu(minha) parceiro(a)",                     "subescala": "busqueda_atencion"},
    {"numero": 23, "texto": "Sinto que preciso da presença do(a) meu(minha) parceiro(a) para me sentir bem", "subescala": "busqueda_atencion"},
]

for item in DEP_EMOCIONAL_ITENS:
    item["reverso"] = False

DEP_EMOCIONAL_SUBESCALAS = {
    "ansiedade_separacao": {"nome": "Ansiedade de Separação",     "itens": [1, 2, 3, 4, 5],      "cor": "#E74C3C", "campo": "pont_ansiedade_separacao"},
    "expressao_afetiva":   {"nome": "Expressão Afetiva",          "itens": [6, 7, 8, 9, 10],     "cor": "#3498DB", "campo": "pont_expressao_afetiva"},
    "modificacao_planos":  {"nome": "Modificação de Planos",      "itens": [11, 12, 13, 14, 15], "cor": "#27AE60", "campo": "pont_modificacao_planos"},
    "miedo_soledad":       {"nome": "Medo da Solidão",            "itens": [16, 17, 18],         "cor": "#9B59B6", "campo": "pont_miedo_soledad"},
    "expresion_limite":    {"nome": "Expressão Limite",           "itens": [19, 20],             "cor": "#E67E22", "campo": "pont_expresion_limite"},
    "busqueda_atencion":   {"nome": "Busca de Atenção",           "itens": [21, 22, 23],         "cor": "#F39C12", "campo": "pont_busqueda_atencion"},
}

DEP_EMOCIONAL_OPCOES = [
    {"valor": 1, "label": "Nunca / Raramente"},
    {"valor": 2, "label": "Poucas vezes"},
    {"valor": 3, "label": "Algumas vezes"},
    {"valor": 4, "label": "Muitas vezes"},
    {"valor": 5, "label": "Frequentemente"},
    {"valor": 6, "label": "Sempre"},
]

DEP_EMOCIONAL_CORTE = {
    "total": [
        ("Baixo",   23,  69),
        ("Médio",   70, 115),
        ("Alto",   116, 138),
    ],
}
