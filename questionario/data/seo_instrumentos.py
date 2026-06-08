"""
Conteúdo das páginas públicas de SEO por instrumento (/instrumentos/<slug>/).

Cada entrada gera automaticamente uma página pública otimizada para busca,
explicando o instrumento e convidando o visitante a testar o IntegraMente.
Para publicar um novo instrumento, basta acrescentar uma entrada aqui —
não é necessário criar view, template ou rota nova.
"""

INSTRUMENTOS_SEO = {

    "perfil-sensorial": {
        "nome": "Perfil Sensorial — Criança IntegraMente",
        "nome_curto": "Perfil Sensorial",
        "especialidade": "Terapia Ocupacional",
        "faixa_etaria": "3 a 14 anos e 11 meses",
        "respondido_por": "pais ou responsáveis",
        "meta_description": "Aplique o Perfil Sensorial online com pontuação automática por seção e quadrante (Exploração, Esquiva, Sensibilidade, Observação). Teste grátis por 7 dias no IntegraMente.",
        "o_que_e": "O Perfil Sensorial é um instrumento amplamente utilizado na Terapia Ocupacional para investigar como uma criança processa e responde a estímulos sensoriais do dia a dia — sons, texturas, movimento, posições corporais, entre outros.",
        "o_que_avalia": [
            "Processamento Auditivo, Visual, Tátil e de Movimentos",
            "Posição do Corpo e Sensibilidade Oral",
            "Conduta, Respostas Socioemocionais e de Atenção",
            "Classificação por quadrante: Exploração (EX), Esquiva (EV), Sensibilidade (SN) e Observação (OB)",
        ],
        "para_que_serve": "Ajuda o terapeuta ocupacional a identificar padrões de modulação sensorial que impactam comportamento, aprendizagem e rotina — orientando o plano terapêutico e a comunicação com a família e a escola.",
        "como_no_sistema": "No IntegraMente, você gera um link e envia para o responsável preencher de qualquer dispositivo. O sistema pontua automaticamente cada seção e quadrante, monta o gráfico radar e organiza tudo no histórico do paciente — pronto para análise e geração de laudo.",
    },

    "sdq": {
        "nome": "SDQ — Questionário de Capacidades e Dificuldades",
        "nome_curto": "SDQ",
        "especialidade": "Psicologia",
        "faixa_etaria": "4 a 17 anos",
        "respondido_por": "pais, professores ou o próprio adolescente (autoaplicação)",
        "meta_description": "Aplique o SDQ (Strengths and Difficulties Questionnaire) online com pontuação automática por subescala. Triagem de dificuldades emocionais e comportamentais. Teste grátis por 7 dias.",
        "o_que_e": "O SDQ (Strengths and Difficulties Questionnaire) é um instrumento de triagem breve e amplamente validado para identificar dificuldades emocionais e comportamentais em crianças e adolescentes, além de pontos fortes (comportamento prossocial).",
        "o_que_avalia": [
            "Sintomas Emocionais",
            "Problemas de Conduta",
            "Hiperatividade / Desatenção",
            "Problemas com Colegas",
            "Comportamento Prossocial",
        ],
        "para_que_serve": "É utilizado em triagens clínicas e escolares para identificar crianças que podem se beneficiar de avaliação ou acompanhamento mais aprofundado, e para acompanhar a evolução ao longo do tempo.",
        "como_no_sistema": "Gere o link do SDQ, envie para pais, professores ou para o adolescente, e receba o resultado já pontuado por subescala — sem precisar somar nada manualmente. O histórico fica organizado por paciente, facilitando comparações entre aplicações.",
    },

    "mchat": {
        "nome": "M-CHAT-R — Rastreio de Risco para Autismo",
        "nome_curto": "M-CHAT-R",
        "especialidade": "Psicologia / Pediatria",
        "faixa_etaria": "16 a 30 meses",
        "respondido_por": "pais ou responsáveis",
        "meta_description": "Aplique o M-CHAT-R online — rastreio de risco para Transtorno do Espectro Autista em crianças pequenas, com pontuação automática. Teste grátis por 7 dias no IntegraMente.",
        "o_que_e": "O M-CHAT-R (Modified Checklist for Autism in Toddlers, Revised) é um instrumento de rastreio amplamente utilizado para identificar sinais precoces de risco para o Transtorno do Espectro Autista (TEA) em crianças pequenas.",
        "o_que_avalia": [
            "Comportamentos de atenção compartilhada e comunicação social",
            "Padrões de interesse e resposta a estímulos sociais",
            "Sinais de alerta precoces relacionados ao desenvolvimento socioemocional",
        ],
        "para_que_serve": "Auxilia o profissional a identificar, ainda na primeira infância, crianças que merecem avaliação diagnóstica mais aprofundada — favorecendo a intervenção precoce, que está diretamente associada a melhores desfechos no desenvolvimento.",
        "como_no_sistema": "Envie o link para os responsáveis preencherem em poucos minutos. O IntegraMente calcula automaticamente o nível de risco e organiza o resultado no histórico da criança, junto a outras avaliações já aplicadas.",
    },

    "vineland3": {
        "nome": "Vineland-3 — Escala de Comportamento Adaptativo",
        "nome_curto": "Vineland-3",
        "especialidade": "Psicologia / Terapia Ocupacional / Neuropsicologia",
        "faixa_etaria": "0 a 90 anos (versões por faixa etária)",
        "respondido_por": "pais, cuidadores ou responsáveis",
        "meta_description": "Aplique a Escala Vineland-3 online com pontuação automática por domínio de comportamento adaptativo. Organize resultados e histórico por paciente. Teste grátis por 7 dias.",
        "o_que_e": "A Vineland-3 é uma das escalas mais utilizadas internacionalmente para avaliar o comportamento adaptativo — ou seja, como a pessoa lida com as demandas práticas do dia a dia em diferentes contextos e fases da vida.",
        "o_que_avalia": [
            "Comunicação (receptiva, expressiva e escrita)",
            "Habilidades da Vida Diária (pessoal, doméstica e comunitária)",
            "Socialização (relações interpessoais, lazer e habilidades de enfrentamento)",
            "Habilidades Motoras (em faixas etárias específicas)",
        ],
        "para_que_serve": "É amplamente utilizada em avaliações diagnósticas (incluindo TEA e deficiência intelectual), planejamento de intervenções e acompanhamento de evolução ao longo do tempo.",
        "como_no_sistema": "O IntegraMente organiza a aplicação por página, calcula a pontuação por domínio automaticamente e mantém o histórico de cada paciente — facilitando comparações entre avaliações e a montagem do laudo.",
    },

    "snap_iv": {
        "nome": "SNAP-IV — Avaliação de TDAH e TOD",
        "nome_curto": "SNAP-IV",
        "especialidade": "Psicologia / Pediatria",
        "faixa_etaria": "Crianças e adolescentes em idade escolar",
        "respondido_por": "pais e/ou professores",
        "meta_description": "Aplique o SNAP-IV online — instrumento de triagem para sintomas de TDAH e Transtorno Opositor Desafiador, com pontuação automática por domínio. Teste grátis por 7 dias.",
        "o_que_e": "O SNAP-IV é um instrumento de triagem amplamente utilizado para identificar sintomas relacionados ao Transtorno de Déficit de Atenção e Hiperatividade (TDAH) e ao Transtorno Opositor Desafiador (TOD), a partir do relato de pais e professores.",
        "o_que_avalia": [
            "Desatenção",
            "Hiperatividade / Impulsividade",
            "Sintomas de Oposição / Desafio",
        ],
        "para_que_serve": "Apoia o processo de triagem e acompanhamento de crianças com suspeita de TDAH/TOD, permitindo comparar a percepção de diferentes informantes (pais e professores) sobre o mesmo comportamento.",
        "como_no_sistema": "Envie versões diferentes do link conforme o informante (pais ou professores) e receba os resultados organizados lado a lado no painel do paciente, com pontuação automática por domínio.",
    },

    "dass21": {
        "nome": "DASS-21 — Depressão, Ansiedade e Estresse",
        "nome_curto": "DASS-21",
        "especialidade": "Psicologia",
        "faixa_etaria": "Adolescentes e adultos",
        "respondido_por": "o próprio paciente (autoaplicação)",
        "meta_description": "Aplique o DASS-21 online com pontuação automática das escalas de Depressão, Ansiedade e Estresse. Resultado pronto para análise clínica. Teste grátis por 7 dias.",
        "o_que_e": "O DASS-21 (Depression, Anxiety and Stress Scales) é um instrumento de autoaplicação amplamente utilizado para medir a intensidade de sintomas de depressão, ansiedade e estresse em adolescentes e adultos.",
        "o_que_avalia": [
            "Sintomas de Depressão",
            "Sintomas de Ansiedade",
            "Níveis de Estresse",
        ],
        "para_que_serve": "É útil tanto para triagem inicial quanto para acompanhamento da evolução do paciente ao longo do processo terapêutico, permitindo comparar resultados entre diferentes momentos do acompanhamento.",
        "como_no_sistema": "O paciente responde pelo link em poucos minutos, e o IntegraMente calcula automaticamente a pontuação de cada escala — pronta para ser usada na sessão ou no relatório clínico.",
    },

    "phq9": {
        "nome": "PHQ-9 — Questionário de Saúde do Paciente",
        "nome_curto": "PHQ-9",
        "especialidade": "Psicologia / Psiquiatria",
        "faixa_etaria": "Adolescentes e adultos",
        "respondido_por": "o próprio paciente (autoaplicação)",
        "meta_description": "Aplique o PHQ-9 online — instrumento validado de rastreio e acompanhamento de sintomas depressivos, com pontuação automática. Teste grátis por 7 dias no IntegraMente.",
        "o_que_e": "O PHQ-9 (Patient Health Questionnaire-9) é um dos instrumentos mais utilizados no mundo para rastreio e monitoramento da gravidade de sintomas depressivos.",
        "o_que_avalia": [
            "Frequência e intensidade de sintomas depressivos nas últimas duas semanas",
            "Impacto funcional dos sintomas no dia a dia",
        ],
        "para_que_serve": "Apoia a triagem inicial, o acompanhamento ao longo do tratamento e a comunicação objetiva da evolução do quadro entre profissionais e equipes multidisciplinares.",
        "como_no_sistema": "Aplicações periódicas ficam organizadas no histórico do paciente, com pontuação automática — facilitando visualizar a evolução do quadro ao longo do acompanhamento.",
    },

    "gad7": {
        "nome": "GAD-7 — Transtorno de Ansiedade Generalizada",
        "nome_curto": "GAD-7",
        "especialidade": "Psicologia / Psiquiatria",
        "faixa_etaria": "Adolescentes e adultos",
        "respondido_por": "o próprio paciente (autoaplicação)",
        "meta_description": "Aplique o GAD-7 online com pontuação automática — instrumento validado para rastreio e acompanhamento de sintomas de ansiedade generalizada. Teste grátis por 7 dias.",
        "o_que_e": "O GAD-7 (Generalized Anxiety Disorder-7) é um instrumento breve e validado, amplamente utilizado para rastrear e medir a intensidade de sintomas de ansiedade generalizada.",
        "o_que_avalia": [
            "Frequência de sintomas de ansiedade nas últimas duas semanas",
            "Intensidade do impacto da ansiedade no funcionamento diário",
        ],
        "para_que_serve": "Auxilia na triagem inicial e no acompanhamento longitudinal de pacientes em tratamento, permitindo registrar objetivamente a evolução dos sintomas ao longo das sessões.",
        "como_no_sistema": "O resultado chega pontuado automaticamente ao seu painel, já organizado junto ao histórico clínico do paciente — pronto para apoiar a conduta e o relatório.",
    },

    "beery": {
        "nome": "Beery VMI — Integração Visomotora",
        "nome_curto": "Beery VMI",
        "especialidade": "Terapia Ocupacional / Neuropsicologia",
        "faixa_etaria": "Crianças e adolescentes",
        "respondido_por": "aplicação direta pelo profissional",
        "meta_description": "Organize a aplicação do Beery VMI no IntegraMente — registro de resultados, histórico do paciente e geração de relatório. Teste grátis por 7 dias.",
        "o_que_e": "O Beery VMI (Developmental Test of Visual-Motor Integration) é um instrumento amplamente utilizado para avaliar a integração entre habilidades visuais e motoras — fundamentais para tarefas como escrita, desenho e cópia.",
        "o_que_avalia": [
            "Integração Visomotora",
            "Percepção Visual",
            "Coordenação Motora",
        ],
        "para_que_serve": "Auxilia na identificação de dificuldades que impactam o desempenho escolar e atividades cotidianas, orientando o planejamento de intervenções em Terapia Ocupacional e áreas afins.",
        "como_no_sistema": "Registre os resultados da aplicação diretamente no painel do paciente, acompanhe a evolução ao longo do tempo e gere a documentação clínica associada — tudo em um só lugar.",
    },

    "pedi": {
        "nome": "PEDI — Inventário de Avaliação Pediátrica de Incapacidade",
        "nome_curto": "PEDI",
        "especialidade": "Terapia Ocupacional / Fisioterapia / Pediatria",
        "faixa_etaria": "6 meses a 7 anos e meio (funcionalmente, até além)",
        "respondido_por": "pais, cuidadores ou aplicação direta pelo profissional",
        "meta_description": "Aplique e organize o PEDI no IntegraMente — avaliação funcional infantil com histórico, comparativos e geração de relatório. Teste grátis por 7 dias.",
        "o_que_e": "O PEDI é um instrumento amplamente utilizado para avaliar o desempenho funcional de crianças em atividades do dia a dia, sendo uma referência em contextos de reabilitação e desenvolvimento infantil.",
        "o_que_avalia": [
            "Autocuidado",
            "Mobilidade",
            "Função Social",
            "Nível de assistência do cuidador em cada área",
        ],
        "para_que_serve": "Apoia o diagnóstico funcional, o planejamento terapêutico e o acompanhamento da evolução de crianças em processos de reabilitação ou intervenção precoce.",
        "como_no_sistema": "Centralize os resultados de cada aplicação no histórico do paciente, compare evoluções ao longo do tempo e gere a documentação clínica — sem depender de planilhas paralelas.",
    },

    "scq": {
        "nome": "SCQ — Questionário de Comunicação Social",
        "nome_curto": "SCQ",
        "especialidade": "Psicologia / Pediatria",
        "faixa_etaria": "A partir de 4 anos (idade mental mínima de 2 anos)",
        "respondido_por": "pais ou responsáveis",
        "meta_description": "Aplique o SCQ online — questionário de triagem para sinais relacionados ao espectro autista, com pontuação automática. Teste grátis por 7 dias no IntegraMente.",
        "o_que_e": "O SCQ (Social Communication Questionnaire) é um instrumento de triagem baseado no relato dos pais, utilizado para identificar comportamentos relacionados à comunicação social que podem indicar a necessidade de avaliação mais aprofundada para o espectro autista.",
        "o_que_avalia": [
            "Comunicação verbal e não verbal",
            "Interação social recíproca",
            "Comportamentos restritos e repetitivos",
        ],
        "para_que_serve": "Auxilia profissionais a priorizar encaminhamentos para avaliação diagnóstica mais completa, otimizando o tempo da triagem inicial.",
        "como_no_sistema": "Envie o link para os responsáveis, receba o resultado já pontuado e mantenha tudo organizado junto às demais avaliações do paciente no IntegraMente.",
    },

    "bdi": {
        "nome": "BDI — Inventário de Depressão de Beck",
        "nome_curto": "BDI",
        "especialidade": "Psicologia",
        "faixa_etaria": "Adolescentes e adultos",
        "respondido_por": "o próprio paciente (autoaplicação)",
        "meta_description": "Aplique o Inventário de Depressão de Beck (BDI) online com pontuação automática. Organize resultados e histórico clínico no IntegraMente. Teste grátis por 7 dias.",
        "o_que_e": "O Inventário de Depressão de Beck (BDI) é um dos instrumentos mais conhecidos e utilizados para medir a intensidade de sintomas depressivos em adolescentes e adultos.",
        "o_que_avalia": [
            "Intensidade de sintomas cognitivos, afetivos e somáticos da depressão",
            "Impacto desses sintomas na rotina do paciente",
        ],
        "para_que_serve": "Apoia a triagem, o acompanhamento da evolução clínica e a tomada de decisão sobre encaminhamentos e condutas terapêuticas.",
        "como_no_sistema": "O resultado chega pontuado automaticamente, organizado no histórico do paciente — pronto para ser usado na sessão e na elaboração de relatórios.",
    },
}


def get_instrumento_seo(slug):
    return INSTRUMENTOS_SEO.get(slug)


def listar_instrumentos_seo():
    """Retorna a lista de instrumentos publicados, ordenada por nome curto."""
    itens = [{"slug": slug, **dados} for slug, dados in INSTRUMENTOS_SEO.items()]
    return sorted(itens, key=lambda i: i["nome_curto"])
