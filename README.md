# AI 小红书爆款生成器

基于多 Agent 协作的 AI 小红书笔记文案自动生成平台。输入内容方向与偏好，AI 自动完成选题策划 → 文案创作 → 爆款优化 → 合规检测，一键生成爆款笔记。支持精细控制笔记类型、文案长度、语言风格等维度。

## 功能亮点

- **选题策划** — TopicAgent 分析热门趋势，生成爆款选题方向
- **AI 创作** — ContentAgent 根据选题创作完整小红书文案
- **爆款优化** — OptimizeAgent 优化标题吸引力与正文互动率
- **合规检测** — RiskAgent 自动检测敏感内容并标注风险等级（低/中/高）
- **精细控制** — 可选指定笔记类型、文案长度、语言风格，以及自由描述内容方向，产出更精准
- **每日限额** — 可配置免费使用次数，防止滥用

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| AI 引擎 | LangChain Agent + DeepSeek API |
| 数据库 | SQLAlchemy + SQLite（开发）/ PostgreSQL（生产） |
| 缓存 | Redis（生产） |
| 前端 | Jinja2 模板 + TailwindCSS (CDN) |
| 部署 | Docker Compose + Nginx |
| 样式 | 暗色编辑风格，纯 CSS 动画 |

## 项目结构

```
├── app/                         # 应用代码
│   ├── main.py                  # FastAPI 入口，路由定义
│   ├── config.py                # 环境变量配置
│   ├── database.py              # 数据库连接与会话管理
│   ├── agents/                  # LangChain Agent 层
│   │   ├── base.py              # Agent 基类
│   │   ├── topic_agent.py       # 选题策划 Agent
│   │   ├── content_agent.py     # 文案生成 Agent
│   │   ├── optimize_agent.py    # 爆款优化 Agent
│   │   └── risk_agent.py        # 风险检测 Agent
│   ├── services/                # 业务服务层
│   │   └── content_service.py   # 生成流程编排
│   ├── models/                  # 数据模型
│   │   └── post.py
│   ├── prompts/                 # Agent 系统提示词
│   ├── templates/               # Jinja2 前端模板
│   └── static/                  # 静态资源
│
├── nginx/
│   └── default.conf             # Nginx 反向代理配置
│
├── scripts/
│   ├── deploy.sh                # 生产部署脚本
│   ├── backup.sh                # 数据库备份脚本
│   └── migrate.sh               # 数据库迁移脚本
│
├── logs/                        # 日志目录
├── uploads/                     # 用户上传目录
├── docker-compose.yml           # Docker 服务编排
├── Dockerfile                   # 应用容器镜像
├── .dockerignore
├── .env.example
├── requirements.txt
└── README.md
```

## 快速开始（本地开发）

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

```bash
cp .env.example .env
```

编辑 `.env`：

```env
DOMAIN=your-domain.com          # 生产域名（本地开发可忽略）
LLM_API_KEY=sk-your-api-key-here
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-pro
LLM_TEMPERATURE=0.7
DATABASE_URL=sqlite:///./xhs.db
FREE_DAILY_LIMIT=3
```

### 3. 启动

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问 `http://localhost:8000`。

## 生产部署（Docker Compose）

### 前置条件

- Ubuntu 22.04 LTS + Docker & Docker Compose
- 域名已解析到服务器 IP + ICP 备案

### 部署步骤

```bash
# 1. 克隆到规范路径
cd /srv/apps
git clone https://github.com/snowfeeling3/xhs-auto-workflow.git
cd xhs-auto-workflow

# 2. 配置（域名 + API Key + PostgreSQL）
cp .env.example .env
nano .env
# 必填：DOMAIN、LLM_API_KEY
# 生产启用：DATABASE_URL（PostgreSQL）、REDIS_URL

# 3. 启动（nginx 自动从模板读取 DOMAIN 生成配置）
docker compose up -d

# 4. 查看状态
docker compose ps
```

### 申请 SSL 证书

```bash
# HTTP 服务跑起来后，用 certbot 申请证书
docker compose exec nginx certbot certonly --webroot \
  -w /var/www/certbot \
  -d $(grep DOMAIN .env | cut -d= -f2) \
  --email admin@你的邮箱.com --agree-tos

# 取消注释 nginx/default.conf.template 中 HTTPS server 块
# 然后重启
docker compose restart nginx
```

### 运维命令

```bash
docker compose ps                  # 查看服务状态
docker compose logs -f app         # 实时日志
docker compose restart app         # 重启应用
bash scripts/backup.sh             # 备份数据库
bash scripts/deploy.sh             # 一键重新部署
```

## 配置说明

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `DOMAIN` | 部署域名 | - |
| `LLM_API_KEY` | DeepSeek API 密钥 | - |
| `LLM_BASE_URL` | API 地址 | `https://api.deepseek.com` |
| `LLM_MODEL` | 模型名称 | `deepseek-v4-pro` |
| `LLM_TEMPERATURE` | 生成温度 | `0.7` |
| `DATABASE_URL` | 数据库连接 | `sqlite:///./xhs.db` |
| `REDIS_URL` | Redis 地址（生产） | - |
| `FREE_DAILY_LIMIT` | 每日免费次数 | `3` |

> 兼容 OpenAI 格式的 API（如通义千问、智谱 GLM），修改 `LLM_BASE_URL` 和 `LLM_MODEL` 即可。

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 首页 |
| `POST` | `/generate` | 生成文案（见下方请求格式） |
| `GET` | `/result/{post_id}` | 查看生成结果 |

### POST /generate 请求格式

```json
{
    "topic": "护肤",
    "description": "我想写敏感肌平价面霜推荐，主打积雪草成分",
    "style": "好物测评",
    "length": "中篇（~500-800字）",
    "tone": "口语化/年轻化"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `topic` | string | 是 | 内容方向关键词 |
| `description` | string | 否 | 方向描述，越具体产出越精准 |
| `style` | string | 否 | 笔记类型：干货教程 / 经验分享 / 好物测评 / 情感共鸣 / Vlog脚本 / 避坑指南 |
| `length` | string | 否 | 文案长度：短篇 ~300字 / 中篇 500-800字 / 长篇 1000+字 |
| `tone` | string | 否 | 语言风格：口语化/年轻化 / 正式/专业 / 治愈/温暖 / 犀利/敢说 |

## License

MIT
