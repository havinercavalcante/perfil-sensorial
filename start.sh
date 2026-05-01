#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "==> Gerando migrações..."
.venv/bin/python manage.py makemigrations

echo "==> Aplicando migrações..."
.venv/bin/python manage.py migrate

echo "==> Iniciando servidor de desenvolvimento..."
.venv/bin/python manage.py runserver
