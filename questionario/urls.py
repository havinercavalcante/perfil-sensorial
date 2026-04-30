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
    path("pacientes/<uuid:paciente_id>/", views.detalhe_paciente, name="detalhe_paciente"),
    path("pacientes/<uuid:paciente_id>/nova-avaliacao/", views.nova_avaliacao, name="nova_avaliacao"),
    path("avaliacao/<int:avaliacao_id>/pagina/<int:pagina>/", views.questionario_view, name="questionario"),
    path("questionario/publico/<str:token>/<int:pagina>/", views.questionario_publico_view, name="questionario_publico"),
    path("avaliacao/<int:avaliacao_id>/concluir/", views.concluir, name="concluir"),
    path("avaliacao/<int:avaliacao_id>/dashboard/", views.dashboard, name="dashboard"),
    path("avaliacao/<int:avaliacao_id>/deletar/", views.deletar_avaliacao, name="deletar_avaliacao"),
    path("avaliacao/<int:avaliacao_id>/enviar-link/", views.enviar_email_link, name="enviar_email_link"),
    # Vineland
    path("pacientes/<uuid:paciente_id>/nova-avaliacao-vineland/", views.nova_avaliacao_vineland, name="nova_avaliacao_vineland"),
    path("vineland/<int:avaliacao_id>/pagina/<int:pagina>/", views.vineland_form, name="vineland_form"),
    path("vineland/<int:avaliacao_id>/concluir/", views.vineland_concluir, name="vineland_concluir"),
    path("vineland/<int:avaliacao_id>/resultado/", views.vineland_resultado, name="vineland_resultado"),
    path("vineland/<int:avaliacao_id>/deletar/", views.vineland_deletar, name="vineland_deletar"),
    path("vineland/publico/<str:token>/<int:pagina>/", views.vineland_publico_view, name="vineland_publico"),
    path("vineland/<int:avaliacao_id>/enviar-link/", views.enviar_email_link_vineland, name="enviar_email_link_vineland"),
]
