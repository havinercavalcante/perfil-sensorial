#!/bin/bash
# Execute na VPS: bash setup_vps.sh
set -e

PROJECT_DIR=/home/ubuntu/perfil_sensorial
REPO_URL=https://github.com/havinercavalcante/perfil-sensorial.git

echo "==> Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

echo "==> Instalando dependencias..."
sudo apt install -y python3-pip python3-venv git nginx certbot python3-certbot-nginx

echo "==> Clonando repositório..."
git clone $REPO_URL $PROJECT_DIR
cd $PROJECT_DIR

echo "==> Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

echo "==> Instalando pacotes Python..."
pip install -r requirements.txt gunicorn

echo "==> Configurando .env (edite o arquivo antes de continuar)..."
cp deploy/.env.example .env
echo ""
echo "*** EDITE o arquivo .env agora: nano $PROJECT_DIR/.env ***"
echo "Pressione ENTER quando terminar..."
read

echo "==> Rodando migrate e collectstatic..."
python manage.py migrate
python manage.py collectstatic --noinput

echo "==> Configurando Gunicorn como servico..."
sudo cp deploy/gunicorn.service /etc/systemd/system/gunicorn.service
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

echo "==> Configurando Nginx..."
sudo cp deploy/nginx.conf /etc/nginx/sites-available/cecisys.com
sudo ln -sf /etc/nginx/sites-available/cecisys.com /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

echo "==> Configurando HTTPS com Certbot..."
sudo certbot --nginx -d cecisys.com -d www.cecisys.com

echo ""
echo "✓ Deploy concluido! Acesse: https://cecisys.com"
