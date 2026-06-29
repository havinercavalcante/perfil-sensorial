#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "==> Atualizando dependências..."
.venv/bin/pip install -r requirements.txt -q

echo "==> Gerando migrações..."
.venv/bin/python manage.py makemigrations

echo "==> Aplicando migrações..."
.venv/bin/python manage.py migrate

echo "==> Importando documentos da biblioteca..."
.venv/bin/python documentos/analisar_docs.py

echo "==> Iniciando Mailpit (captura de e-mails em desenvolvimento)..."
if command -v mailpit &>/dev/null || [ -f ".venv/bin/mailpit" ]; then
    .venv/bin/mailpit --smtp "[::]:1025" --listen "[::]:8025" --log-file logs/mailpit.log &
else
    echo "    Mailpit não encontrado no PATH, pulando..."
fi

echo "==> Iniciando worker Celery em background..."
.venv/bin/celery -A perfil_sensorial worker -l info --concurrency=2 --logfile=logs/celery.log --detach

echo "==> Iniciando Celery Beat em background..."
.venv/bin/celery -A perfil_sensorial beat -l info --logfile=logs/celery_beat.log --detach

echo "==> Iniciando servidor de desenvolvimento..."
echo "    Emails disponíveis em: http://localhost:8025"
.venv/bin/python manage.py runserver
