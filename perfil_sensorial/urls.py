from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.views.generic.base import RedirectView
from django.templatetags.static import static

def handler404(request, exception):
    return render(request, 'erros/404.html', status=404)


def handler403(request, exception):
    return render(request, 'erros/403.html', status=403)


def handler500(request):
    return render(request, 'erros/500.html', status=500)

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=static('logotop.png'), permanent=True)),
    path('admin/', admin.site.urls),
    path('', include('questionario.urls')),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        email_template_name='questionario/emails/password_reset_email.txt',
        html_email_template_name='questionario/emails/password_reset_email_html.html',
        subject_template_name='questionario/emails/password_reset_subject.txt',
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
