#!/bin/bash
# Backup do banco de dados SQLite
# Instalar cron: bash deploy/backup.sh --install-cron
set -e

PROJECT_DIR=/root/perfil_sensorial
BACKUP_DIR=/root/backups
DB_FILE=$PROJECT_DIR/db.sqlite3
RETENTION_DAYS=30

if [ "$1" = "--install-cron" ]; then
    mkdir -p $BACKUP_DIR
    SCRIPT_PATH=$PROJECT_DIR/deploy/backup.sh
    CRON_LINE="0 2 * * * bash $SCRIPT_PATH >> /var/log/backup_db.log 2>&1"
    (crontab -l 2>/dev/null | grep -v "backup.sh"; echo "$CRON_LINE") | crontab -
    echo "Cron configurado: backup diario as 2h da manha"
    echo "Logs em: /var/log/backup_db.log"
    exit 0
fi

mkdir -p $BACKUP_DIR

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEST=$BACKUP_DIR/db_$TIMESTAMP.sqlite3

cp $DB_FILE $DEST
echo "$(date '+%Y-%m-%d %H:%M:%S') Backup criado: $DEST"

find $BACKUP_DIR -name "db_*.sqlite3" -mtime +$RETENTION_DAYS -delete
echo "$(date '+%Y-%m-%d %H:%M:%S') Backups antigos removidos (retencao: ${RETENTION_DAYS} dias)"
