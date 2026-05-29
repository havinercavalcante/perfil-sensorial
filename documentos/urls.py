from django.urls import path
from . import views

urlpatterns = [
    path("biblioteca/",                        views.biblioteca,          name="biblioteca"),
    path("biblioteca/<int:pk>/download/",      views.download_documento,  name="download_documento"),
    path("biblioteca/<int:pk>/preview/",       views.preview_documento,   name="preview_documento"),
]
