# AI SaaS 基础设施标准规范

版本：1.0

目的：
本规范用于统一所有 AI SaaS 项目的：

- 开发架构
- 部署方式
- 服务器结构
- Docker 标准
- 运维规范
- AI Agent 行为规则

AI Agent 在以下行为中必须严格遵守本规范：

- 生成代码
- 创建项目
- 修改项目
- Docker 部署
- 配置服务器
- 配置 Nginx
- 配置数据库
- 自动运维
- 多项目管理

目标：

- 标准化
- 可扩展
- 可复制
- 易维护
- AI Agent 友好
- 长期 SaaS 化运营

---

# 一、全局基础设施规范

## 1.1 操作系统

所有生产服务器必须使用：

- Ubuntu 22.04 LTS 或更高版本

禁止使用：

- Windows Server
- CentOS
- 非主流 Linux 发行版

---

## 1.2 项目根目录规范

所有项目统一存放于：

/srv/apps/

每个项目必须独立：

/srv/apps/<project-name>/

示例：

/srv/apps/xiaohongshu-ai/
/srv/apps/ai-blog/
/srv/apps/agent-platform/

---

# 二、项目结构规范

每个项目必须严格遵循以下结构：

project/
│
├── app/
│   ├── agents/
│   ├── services/
│   ├── models/
│   ├── routes/
│   ├── templates/
│   ├── static/
│   ├── prompts/
│   ├── main.py
│   ├── config.py
│   └── database.py
│
├── nginx/
│   └── default.conf
│
├── scripts/
│   ├── deploy.sh
│   ├── backup.sh
│   └── migrate.sh
│
├── logs/
│
├── uploads/
│
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
├── .env
├── .env.example
├── requirements.txt
├── README.md
└── AI_SAAS_INFRASTRUCTURE_CN.md

---

# 三、后端开发规范

## 3.1 后端框架

推荐技术栈：

- FastAPI
- Uvicorn
- SQLAlchemy

避免：

- Flask
- Django 大型单体架构

---

## 3.2 Python 版本

必须使用：

- Python 3.11+

---

## 3.3 环境变量规范

禁止：

- API Key 写死在代码中

必须使用：

.env

示例：

OPENAI_API_KEY=
DATABASE_URL=
REDIS_URL=

Python 必须使用：

python-dotenv

读取环境变量。

---

# 四、数据库规范

## 4.1 开发环境

允许：

- SQLite

---

## 4.2 生产环境

必须使用：

- PostgreSQL

禁止生产环境长期使用 SQLite。

---

# 五、Redis 规范

Redis 用于：

- 缓存
- 限流
- Session
- AI 任务状态
- 队列管理

---

# 六、Docker 标准

## 6.1 Docker 要求

所有项目必须支持 Docker 部署。

必须包含：

- Dockerfile
- docker-compose.yml

---

## 6.2 Dockerfile 规范

必须使用官方轻量镜像。

推荐：

python:3.11-slim

避免：

- 超大镜像
- 无用依赖

---

## 6.3 Docker Compose 规范

所有服务统一由 docker compose 管理。

必须包含：

- app
- nginx
- postgres
- redis

可选：

- celery
- worker
- monitoring

---

# 七、Nginx 规范

Nginx 必须作为：

- 反向代理
- HTTPS 入口
- 静态资源网关

---

## 7.1 配置位置

/etc/nginx/sites-available/

/etc/nginx/sites-enabled/

每个项目独立配置文件。

---

# 八、HTTPS 规范

生产环境必须启用 HTTPS。

推荐：

- certbot
- Let's Encrypt

允许：

- Cloudflare CDN

---

# 九、进程管理规范

禁止：

- nohup
- screen

推荐：

- Docker Compose

备用：

- systemd

---

# 十、日志规范

每个项目必须包含：

logs/

日志包括：

- app 日志
- error 日志
- deployment 日志

禁止日志写入根目录。

---

# 十一、部署规范

## 11.1 推荐部署流程

推荐工作流：

GitHub
↓
git pull
↓
docker compose build
↓
docker compose up -d

---

## 11.2 deploy.sh

每个项目必须包含：

scripts/deploy.sh

职责：

- 拉取最新代码
- 重建容器
- 重启服务
- 清理旧镜像

---

# 十二、AI Agent 运维规范

AI Agent 必须：

- 危险操作前先说明
- 不修改无关项目
- 不删除未知文件
- 不修改全局系统配置（除非明确授权）

---

## 12.1 禁止行为

AI Agent 严禁：

- rm -rf /
- 覆盖其他 nginx 配置
- 泄露 secrets
- 关闭防火墙
- 写死密码/API Key

---

# 十三、域名规范

每个项目推荐：

子域名结构：

ai.domain.com
blog.domain.com
admin.domain.com

---

# 十四、安全规范

生产环境必须：

- 启用防火墙
- 禁止 SSH 密码登录
- 使用 SSH Key
- 禁止公开 .env
- 强制 HTTPS

---

# 十五、Git 规范

必须包含：

- .gitignore

禁止提交：

- .env
- logs
- 数据库文件
- secrets

---

# 十六、监控规范

推荐：

- uptime 监控
- 自动重启
- nginx access logs
- 健康检查接口

---

# 十七、AI SaaS 标准架构

推荐生产架构：

Cloudflare
↓
Nginx
↓
Docker Compose
↓
FastAPI
↓
PostgreSQL
↓
Redis
↓
AI Workers

---

# 十八、AI 开发哲学

系统必须优先考虑：

- 可维护性
- 可扩展性
- 可复制部署
- AI Agent 兼容性
- 模块化
- 低复杂度

避免：

- 过早微服务化
- 过度工程化
- 无意义复杂框架

---

# 十九、Claude Code / AI Agent 行为规则

AI Agent 必须：

- 严格遵守本规范
- 保持统一目录结构
- 优先生成生产级代码
- 优先简单稳定方案
- 避免无意义依赖

---

# 二十、最终目标

最终目标是构建：

- 可长期运营的 AI SaaS 系统
- 多项目统一基础设施
- AI Agent 可操作的生产环境
- 可扩展的自动化部署体系

所有未来项目必须遵循本规范。
