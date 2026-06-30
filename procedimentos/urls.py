from django.urls import path
from . import views

urlpatterns = [
    # Anamnese preenchida diretamente pelo profissional (cria o paciente ao salvar)
    path("anamnese/nova/", views.nova_anamnese, name="nova_anamnese"),

    # Atalhos legados (redireciona para lista)
    path("pacientes/<uuid:paciente_id>/anamnese/",             views.anamnese,             name="anamnese"),
    path("pacientes/<uuid:paciente_id>/ficha-triagem/",        views.ficha_triagem,        name="ficha_triagem"),
    path("pacientes/<uuid:paciente_id>/carta-encaminhamento/", views.carta_encaminhamento, name="carta_encaminhamento"),
    path("pacientes/<uuid:paciente_id>/atestado/",             views.atestado,             name="atestado"),
    path("pacientes/<uuid:paciente_id>/relatorio/",            views.relatorio,            name="relatorio"),

    # Novo fluxo genérico
    path("pacientes/<uuid:paciente_id>/procedimentos/<str:tipo>/",
         views.lista_procedimentos, name="lista_procedimentos"),

    path("pacientes/<uuid:paciente_id>/procedimentos/<str:tipo>/novo/",
         views.novo_procedimento, name="novo_procedimento"),

    path("pacientes/<uuid:paciente_id>/procedimentos/<str:tipo>/criar/",
         views.criar_procedimento, name="criar_procedimento"),

    path("pacientes/<uuid:paciente_id>/procedimentos/<str:tipo>/<uuid:doc_id>/",
         views.abrir_procedimento, name="abrir_procedimento"),

    path("pacientes/<uuid:paciente_id>/procedimentos/<str:tipo>/<uuid:doc_id>/salvar/",
         views.salvar_procedimento, name="salvar_procedimento"),

    path("pacientes/<uuid:paciente_id>/procedimentos/<str:tipo>/<uuid:doc_id>/excluir/",
         views.excluir_procedimento, name="excluir_procedimento"),

    # Anamnese pública (sem login) — preenchida pelo responsável via link
    path("anamnese/publico/<uuid:token>/",
         views.anamnese_publica_form, name="anamnese_publica_form"),
    path("anamnese/publico/<uuid:token>/salvar/",
         views.anamnese_publica_salvar, name="anamnese_publica_salvar"),
]
