#!/usr/bin/env bash
# ============================================
# AI 小红书爆款生成器 — 数据库迁移脚本
# ============================================
set -e

log() { echo "[$(date '+%H:%M:%S')] $1"; }

log "运行数据库迁移（表结构同步）..."
# SQLAlchemy 在启动时自动 create_all，无需单独迁移
# 未来如有 Alembic 迁移，在此处执行: docker exec xhs-app alembic upgrade head
docker compose restart app

log "迁移完成"
