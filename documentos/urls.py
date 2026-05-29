from django.urls import path
from . import views

urlpatterns = [
    path("biblioteca/",                        views.biblioteca,          name="biblioteca"),
    path("biblioteca/<uuid:token>/download/",   views.download_documento,  name="download_documento"),
    path("biblioteca/<uuid:token>/preview/",   views.preview_documento,   name="preview_documento"),
]
