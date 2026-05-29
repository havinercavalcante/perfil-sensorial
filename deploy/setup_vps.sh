#!/bin/bash
# Execute na VPS: bash setup_vps.sh
set -e

PROJECT_DIR=/root/perfil_sensorial
REPO_URL=https://github.com/havinercavalcante/perfil-sensorial.git

echo "==> Atualizando sistema..."
apt update && apt upgrade -y

echo "==> Instalando dependencias..."
apt install -y python3-pip python3-venv git nginx certbot python3-certbot-nginx

echo "==> Clonando repositório..."
git clone $REPO_URL $PROJECT_DIR
cd $PROJECT_DIR

echo "==> Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

echo "==> Instalando pacotes Python..."
pip install -r requirements.txt gunicorn

echo "==> Configurando .env..."
cp deploy/.env.example .env
echo ""
echo "*** EDITE o arquivo .env agora: nano $PROJECT_DIR/.env ***"
echo "Pressione ENTER quando terminar..."
read

echo "==> Rodando migrate e collectstatic..."
python manage.py migrate
python manage.py collectstatic --noinput

echo "==> Importando documentos da biblioteca..."
python documentos/analisar_docs.py

echo "==> Configurando Gunicorn como servico..."
cp deploy/gunicorn.service /etc/systemd/system/gunicorn.service
systemctl daemon-reload
systemctl enable gunicorn
systemctl start gunicorn

echo "==> Configurando Nginx..."
cp deploy/nginx.conf /etc/nginx/sites-available/integramente.pro
ln -sf /etc/nginx/sites-available/integramente.pro /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo "==> Configurando HTTPS com Certbot..."
certbot --nginx -d integramente.pro -d www.integramente.pro

echo "==> Configurando backup automatico do banco de dados..."
chmod +x deploy/backup.sh
bash deploy/backup.sh --install-cron

echo ""
echo "Deploy concluido! Acesse: https://integramente.pro"
