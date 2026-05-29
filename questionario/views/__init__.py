from .auth import *
from .pacientes import *
from .sensorial import *
from .vineland import *
from .escolar import *
from .bebe import *
from .edm import *
from .mabc2 import *
from .beery import *
from .pedi import *
from .spm import *
from .convite import *
from .vineland3 import *
from .portage import *
from .sdq import *
from .snap_iv import *
from .mchat import *
from .cars import *
from .linguagem import *
from .alimentacao import *
from .habitos_orais import *
from .voz_infantil import *
from .processamento_auditivo import *
from .idv10 import *
from .desenvolvimento import *
from .sono import *
from .habilidades_adaptativas import *
from .comportamento_funcional import *
from .cognitivo import *
from .psicopedagogica import *
# ── Módulos de Psicologia ──────────────────────────────────────────────────
from .bdi import *
from .bai import *
from .dass21 import *
from .had import *
from .bsl23 import *
from .aq10_adulto import *
from .aq10_child import *
from .dep_emocional import *
from .scq import *
# ── Lote 2 Psicologia ─────────────────────────────────────────────────────
from .conners import (
    nova_avaliacao_conners_pais, conners_pais_form, conners_pais_resultado,
    conners_pais_visualizar, conners_pais_deletar, salvar_observacoes_conners_pais,
    enviar_email_conners_pais, conners_pais_publico,
    nova_avaliacao_conners_prof, conners_prof_form, conners_prof_resultado,
    conners_prof_visualizar, conners_prof_deletar, salvar_observacoes_conners_prof,
    enviar_email_conners_prof, conners_prof_publico,
)
from .etdah import (
    nova_avaliacao_etdah_pais, etdah_pais_form, etdah_pais_resultado,
    etdah_pais_visualizar, etdah_pais_deletar, salvar_observacoes_etdah_pais,
    enviar_email_etdah_pais, etdah_pais_publico,
    nova_avaliacao_etdah_prof, etdah_prof_form, etdah_prof_resultado,
    etdah_prof_visualizar, etdah_prof_deletar, salvar_observacoes_etdah_prof,
    enviar_email_etdah_prof, etdah_prof_publico,
)
from .auqei import (
    nova_avaliacao_auqei, auqei_form, auqei_resultado, auqei_visualizar,
    auqei_deletar, salvar_observacoes_auqei, enviar_email_auqei, auqei_publico,
)
from .scared import (
    nova_avaliacao_scared, scared_form, scared_resultado, scared_visualizar,
    scared_deletar, salvar_observacoes_scared, enviar_email_scared, scared_publico,
)
from .masc import (
    nova_avaliacao_masc, masc_form, masc_resultado, masc_visualizar,
    masc_deletar, salvar_observacoes_masc, enviar_email_masc, masc_publico,
)
from .bpq import (
    nova_avaliacao_bpq, bpq_form, bpq_resultado, bpq_visualizar,
    bpq_deletar, salvar_observacoes_bpq, enviar_email_bpq, bpq_publico,
)
from .anamnese_tea_inf import (
    nova_avaliacao_anamnese_tea_inf, anamnese_tea_inf_form,
    anamnese_tea_inf_resultado, anamnese_tea_inf_deletar,
)
from .anamnese_tdah_inf import (
    nova_avaliacao_anamnese_tdah_inf, anamnese_tdah_inf_form,
    anamnese_tdah_inf_resultado, anamnese_tdah_inf_deletar,
)
from .anamnese_adulto import (
    nova_avaliacao_anamnese_adulto, anamnese_adulto_form,
    anamnese_adulto_resultado, anamnese_adulto_deletar,
)
from .anamnese_tdah_adulto import (
    nova_avaliacao_anamnese_tdah_adulto, anamnese_tdah_adulto_form,
    anamnese_tdah_adulto_resultado, anamnese_tdah_adulto_deletar,
)
# ── Lote 3: Denver, QMPI, Dislexia ────────────────────────────────────────────
from .denver import (
    nova_avaliacao_denver, denver_form, denver_resultado,
    denver_visualizar, denver_deletar, salvar_observacoes_denver,
)
from .qmpi import (
    nova_avaliacao_qmpi, qmpi_form, qmpi_resultado, qmpi_visualizar,
    qmpi_deletar, salvar_observacoes_qmpi, enviar_email_qmpi, qmpi_publico,
)
from .quest_dislexia import (
    nova_avaliacao_quest_dislexia, quest_dislexia_form, quest_dislexia_resultado,
    quest_dislexia_visualizar, quest_dislexia_deletar, salvar_observacoes_quest_dislexia,
    enviar_email_quest_dislexia, quest_dislexia_publico,
)
from .checklist_dislexia import (
    nova_avaliacao_checklist_dislexia, checklist_dislexia_form, checklist_dislexia_resultado,
    checklist_dislexia_visualizar, checklist_dislexia_deletar, salvar_observacoes_checklist_dislexia,
    enviar_email_checklist_dislexia, checklist_dislexia_publico,
)
from .prot_dislexia_prof import (
    nova_avaliacao_prot_dislexia_prof, prot_dislexia_prof_form, prot_dislexia_prof_resultado,
    prot_dislexia_prof_visualizar, prot_dislexia_prof_deletar, salvar_observacoes_prot_dislexia_prof,
    enviar_email_prot_dislexia_prof, prot_dislexia_prof_publico,
)
from .inventario_dislexia import (
    nova_avaliacao_inventario_dislexia, inventario_dislexia_form,
    inventario_dislexia_resultado, inventario_dislexia_deletar,
)
# ──────────────────────────────────────────────────────────────────────────
from .laudos import laudo_generico
from .pagamentos import solicitar_plano, painel_pagamentos, aprovar_solicitacao, rejeitar_solicitacao
