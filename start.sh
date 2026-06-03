#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "==> Gerando migrações..."
.venv/bin/python manage.py makemigrations

echo "==> Aplicando migrações..."
.venv/bin/python manage.py migrate

echo "==> Importando documentos da biblioteca..."
.venv/bin/python documentos/analisar_docs.py

echo "==> Iniciando servidor de desenvolvimento..."
.venv/bin/python manage.py runserver
