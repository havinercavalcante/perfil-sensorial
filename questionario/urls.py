from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("registrar/", views.registrar_view, name="registrar"),
    path("meu-perfil/", views.meu_perfil, name="meu_perfil"),
    # App
    path("", views.index, name="index"),
    path("pacientes/", views.lista_pacientes, name="lista_pacientes"),
    path("pacientes/novo/", views.novo_paciente, name="novo_paciente"),
    path("pacientes/<int:paciente_id>/", views.detalhe_paciente, name="detalhe_paciente"),
    path("pacientes/<int:paciente_id>/nova-avaliacao/", views.nova_avaliacao, name="nova_avaliacao"),
    path("avaliacao/<int:avaliacao_id>/pagina/<int:pagina>/", views.questionario_view, name="questionario"),
    path("questionario/publico/<str:token>/<int:pagina>/", views.questionario_publico_view, name="questionario_publico"),
    path("avaliacao/<int:avaliacao_id>/concluir/", views.concluir, name="concluir"),
    path("avaliacao/<int:avaliacao_id>/dashboard/", views.dashboard, name="dashboard"),
    path("avaliacao/<int:avaliacao_id>/deletar/", views.deletar_avaliacao, name="deletar_avaliacao"),
    path("avaliacao/<int:avaliacao_id>/enviar-link/", views.enviar_email_link, name="enviar_email_link"),
]
