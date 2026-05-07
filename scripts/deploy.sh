#!/usr/bin/env bash
# ============================================
# AI 小红书爆款生成器 — 生产部署脚本
# ============================================
set -e

PROJECT_DIR="/opt/xhs-auto-workflow"

log()  { echo "[$(date '+%H:%M:%S')] $1"; }
err()  { echo "[ERR] $1"; exit 1; }

log "开始部署..."

cd "$PROJECT_DIR" || err "项目目录不存在: $PROJECT_DIR"

log "拉取最新代码..."
git pull origin master

log "构建镜像..."
docker compose build --pull

log "重启服务..."
docker compose up -d

log "清理旧镜像..."
docker image prune -f

log "检查服务状态..."
sleep 3
docker compose ps

log "部署完成"
