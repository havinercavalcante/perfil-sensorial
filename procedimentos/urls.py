from django.urls import path
from . import views

urlpatterns = [
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
]
