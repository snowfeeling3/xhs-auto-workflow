#!/usr/bin/env bash
# ============================================
# AI 小红书爆款生成器 — 数据库备份脚本
# ============================================
set -e

BACKUP_DIR="/opt/backups/xhs"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

log "备份 PostgreSQL 数据库..."
docker exec xhs-postgres pg_dump -U xhs xhs_app | gzip > "$BACKUP_DIR/xhs_${TIMESTAMP}.sql.gz"

log "清理 ${RETENTION_DAYS} 天前的旧备份..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

log "备份完成: $BACKUP_DIR/xhs_${TIMESTAMP}.sql.gz"
