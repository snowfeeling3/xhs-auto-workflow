#!/usr/bin/env bash
# ============================================
# AI 小红书爆款生成器 — 生产部署脚本
# ============================================
set -e

PROJECT_DIR="/opt/xhs-auto-workflow"

log()  { echo "[$(date '+%H:%M:%S')] $1"; }

log "开始部署..."

cd "$PROJECT_DIR" || { log "项目目录不存在: $PROJECT_DIR"; exit 1; }

# 检查 .env 是否存在
if [ ! -f .env ]; then
    log "请先创建 .env 文件: cp .env.example .env"
    exit 1
fi

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

echo ""
echo "=============================================="
echo "  部署完成"
echo "  访问地址: https://${DOMAIN:-your-domain.com}"
echo "=============================================="
