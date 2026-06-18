from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variaveis do .env se existir
_env_path = BASE_DIR / '.env'
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith('#') and '=' in _line:
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-perfil-sensorial-2-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'integramente.pro,www.integramente.pro').split(',')
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'https://integramente.pro,https://www.integramente.pro'
).split(',')
INSTALLED_APPS = [
    'questionario',
    'documentos',
    'procedimentos',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
MIDDLEWARE = [
    'questionario.middleware.CustomErrorMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'questionario.middleware.TrialExpiradoMiddleware',
    'questionario.middleware.PageVisitMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'perfil_sensorial.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [], 'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'perfil_sensorial.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Fortaleza'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Permite que usuários com is_active=False façam login
# (o middleware redireciona para /planos/ após o login)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.AllowAllUsersModelBackend',
]

# ── Segurança HTTPS (ativas em produção, desligadas com DEBUG=True) ───────────
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ── Session e CSRF cookies ────────────────────────────────────────────────────
SESSION_COOKIE_AGE = 28800           # 8 horas
SESSION_COOKIE_SECURE = not DEBUG    # HTTPS only em produção
SESSION_COOKIE_HTTPONLY = True       # Inacessível via JavaScript
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

# ── Validadores de senha ──────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Configuração de envio de e-mail SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ── Configurações de pagamento manual (PIX) ────────────────────────────────────
PIX_KEY          = os.environ.get('PIX_KEY', '06164397332')
PIX_BENEFICIARIO = os.environ.get('PIX_BENEFICIARIO', 'Haviner Cavalcante Nunes de Souza')
PIX_BANCO        = os.environ.get('PIX_BANCO', 'Nubank')
# E-mail do admin que recebe notificação de nova solicitação de plano
ADMIN_NOTIFY_EMAIL = os.environ.get('ADMIN_NOTIFY_EMAIL', EMAIL_HOST_USER)

# ── Celery ────────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_BEAT_SCHEDULE = {
    "desativar-trials-expirados": {
        "task": "questionario.tasks.desativar_trials_expirados",
        "schedule": 86400,  # a cada 24 horas
    },
    "verificar-planos-expirando": {
        "task": "questionario.tasks.verificar_planos_expirando",
        "schedule": 86400,  # a cada 24 horas
    },
}

# ── Logging de auditoria LGPD ─────────────────────────────────────────────────
_logs_dir = BASE_DIR / 'logs'
_logs_dir.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'auditoria': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'auditoria_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': _logs_dir / 'auditoria.log',
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 10,
            'formatter': 'auditoria',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'auditoria': {
            'handlers': ['auditoria_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
