# Escala de Autoestima de Rosenberg (1965)
# Itens 1,2,4,6,7 positivos: Concordo=3, Concordo parcialmente=2, Discordo parcialmente=1, Discordo=0
# Itens 3,5,8,9,10 negativos: invertidos: Concordo=0...Discordo=3
def _pos(texto):
    return {"texto": texto, "opcoes": [
        {"valor": 3, "label": "Concordo muito"},
        {"valor": 2, "label": "Concordo"},
        {"valor": 1, "label": "Discordo"},
        {"valor": 0, "label": "Discordo muito"},
    ]}
def _neg(texto):
    return {"texto": texto, "opcoes": [
        {"valor": 0, "label": "Concordo muito"},
        {"valor": 1, "label": "Concordo"},
        {"valor": 2, "label": "Discordo"},
        {"valor": 3, "label": "Discordo muito"},
    ]}
ROSENBERG_ITENS = [
    {**_pos("Eu sinto que sou uma pessoa de valor, pelo menos num plano igual às outras pessoas."), "numero": 1},
    {**_pos("Eu acho que tenho várias boas qualidades."), "numero": 2},
    {**_neg("Levando tudo em conta, eu me inclino a achar que sou um(a) fracassado(a)."), "numero": 3},
    {**_pos("Eu sou capaz de fazer coisas tão bem quanto a maioria das pessoas."), "numero": 4},
    {**_neg("Eu acho que não tenho muito do que me orgulhar."), "numero": 5},
    {**_pos("Eu tenho uma atitude positiva com relação a mim mesmo(a)."), "numero": 6},
    {**_pos("No conjunto, estou satisfeito(a) comigo mesmo(a)."), "numero": 7},
    {**_neg("Eu gostaria de ter mais respeito por mim mesmo(a)."), "numero": 8},
    {**_neg("Às vezes eu me sinto inútil."), "numero": 9},
    {**_neg("Às vezes acho que não presto para nada."), "numero": 10},
]
ROSENBERG_CORTE = [
    ("Autoestima muito baixa",  0, 14),
    ("Autoestima baixa",       15, 19),
    ("Autoestima normal",      20, 25),
    ("Autoestima elevada",     26, 30),
]