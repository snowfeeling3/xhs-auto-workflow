# AI 小红书爆款生成器

基于多 Agent 协作的 AI 小红书笔记文案自动生成平台。输入内容方向与偏好，AI 自动完成选题策划 → 文案创作 → 爆款优化 → 合规检测，一键生成爆款笔记。支持精细控制笔记类型、文案长度、语言风格等维度。

## 功能亮点

- **选题策划** — TopicAgent 分析热门趋势，生成爆款选题方向
- **AI 创作** — ContentAgent 根据选题创作完整小红书文案
- **爆款优化** — OptimizeAgent 优化标题吸引力与正文互动率
- **合规检测** — RiskAgent 自动检测敏感内容并标注风险等级（低/中/高）
- **精细控制** — 可选指定笔记类型、文案长度、语言风格，支持自定义输入
- **配图建议** — AI 在正文中自动标注 [插入图片：描述] 位置，结果页渲染为配图建议卡片
- **热搜榜单** — 每日 8:00 自动生成小红书社区热搜话题，首页表格展示
- **历史记录** — 查看过往生成记录，支持一键复制和同主题再生成
- **扫码付款** — 微信/支付宝扫码支付，￥1.00 = 3 次生成，支持自动/手动验证
- **积分系统** — Session 级别积分追踪，新用户可配置试用次数

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| AI 引擎 | LangChain Agent + DeepSeek API |
| 数据库 | SQLAlchemy + SQLite（开发）/ PostgreSQL（生产） |
| 缓存 | Redis（生产） |
| 前端 | Jinja2 模板 + TailwindCSS (CDN) |
| 部署 | Docker Compose + 宿主机 Nginx |
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
│   │   └── content_service.py   # 生成流程编排 + XSS 过滤
│   ├── models/                  # 数据模型
│   │   ├── post.py              # 生成记录
│   │   ├── trending.py          # 热搜话题
│   │   ├── credit.py            # 积分账户
│   │   └── payment.py           # 付款记录
│   ├── prompts/                 # Agent 系统提示词
│   ├── templates/               # Jinja2 前端模板
│   │   ├── index.html           # 首页（含热搜榜单 + 积分提示）
│   │   ├── result.html          # 结果页（含配图卡片）
│   │   ├── history.html         # 历史记录页
│   │   └── payment.html         # 充值付款页
│   └── static/                  # 静态资源（含收款二维码）
│
├── nginx/
│   └── xhs.conf                 # 宿主机 Nginx 配置
│
├── scripts/
│   ├── deploy.sh                # 生产部署脚本
│   ├── backup.sh                # 数据库备份脚本
│   ├── migrate.sh               # 数据库迁移脚本
│   └── fetch_trending.py        # 每日热搜话题抓取
│
├── logs/                        # 日志目录
├── uploads/                     # 用户上传目录
├── docker-compose.yml           # Docker 服务编排（app + postgres + redis）
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
LLM_API_KEY=sk-your-api-key-here
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-pro
LLM_TEMPERATURE=0.7
DATABASE_URL=sqlite:///./xhs.db

# 积分与付款
NEW_USER_CREDITS=1
PAYMENT_QR_URL=/static/qr_payment.png
PAYMENT_AUTO_VERIFY=true
ADMIN_KEY=admin123
```

### 3. 启动

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问 `http://localhost:8000`。

## 生产部署（Docker Compose + 宿主机 Nginx）

### 架构

```
用户 → 宿主机 Nginx (80/443) → localhost:8011 → Docker xhs-app
```

各项目共享一个宿主机 Nginx，按域名分发到不同端口（8011、8012...）。Docker 内不运行 Nginx。

### 部署步骤

```bash
# 1. 克隆
cd /srv/apps
git clone https://github.com/snowfeeling3/xhs-auto-workflow.git
cd xhs-auto-workflow

# 2. 配置
cp .env.example .env
nano .env
# 必填：LLM_API_KEY
# 生产：DATABASE_URL=postgresql://xhs:<密码>@postgres:5432/xhs_app
#        REDIS_URL=redis://redis:6379/0
#        DB_PASSWORD=<密码>

# 3. 把收款二维码放到 app/static/qr_payment.jpg（覆盖占位图）

# 4. 配置宿主机 Nginx
sudo cp nginx/xhs.conf /etc/nginx/conf.d/xhs.conf
# 编辑域名：sed -i 's/xhs.sn0wpear.com/你的域名/g' /etc/nginx/conf.d/xhs.conf
sudo nginx -t && sudo systemctl reload nginx

# 5. 启动
docker compose up -d --build

# 6. HTTPS（可选）
sudo certbot --nginx -d 你的域名
```

### 运维命令

```bash
docker compose ps                  # 查看服务状态
docker compose logs -f app         # 实时日志
docker compose restart app         # 重启应用
docker compose up -d --build       # 更新代码后重建
bash scripts/backup.sh             # 备份数据库
python scripts/fetch_trending.py   # 手动抓取今日热搜

# 每日 8:00 自动抓取热搜
(crontab -l 2>/dev/null; echo "0 8 * * * cd /srv/apps/xhs-auto-workflow && python scripts/fetch_trending.py >> logs/trending.log 2>&1") | crontab -
```

## 配置说明

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `LLM_API_KEY` | DeepSeek API 密钥 | - |
| `LLM_BASE_URL` | API 地址 | `https://api.deepseek.com` |
| `LLM_MODEL` | 模型名称 | `deepseek-v4-pro` |
| `LLM_TEMPERATURE` | 生成温度 | `0.7` |
| `DATABASE_URL` | 数据库连接 | `sqlite:///./xhs.db` |
| `REDIS_URL` | Redis 地址（生产） | - |
| `NEW_USER_CREDITS` | 新用户初始积分 | `1` |
| `PAYMENT_QR_URL` | 收款二维码路径 | - |
| `PAYMENT_AUTO_VERIFY` | 付款后自动到账 | `false` |
| `ADMIN_KEY` | 管理后台密钥 | `admin123` |

> 兼容 OpenAI 格式的 API（如通义千问、智谱 GLM），修改 `LLM_BASE_URL` 和 `LLM_MODEL` 即可。

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 首页（含热搜榜单） |
| `POST` | `/generate` | 生成文案 |
| `GET` | `/result/{post_id}` | 查看生成结果 |
| `GET` | `/history` | 历史生成记录 |
| `GET` | `/api/trending` | 今日热搜话题 JSON |
| `GET` | `/api/credits` | 查询当前积分 |
| `GET` | `/payment` | 充值付款页 |
| `POST` | `/api/payment/submit` | 提交付款验证 |
| `GET` | `/admin/login` | 管理后台登录 |
| `GET` | `/admin/payments` | 管理付款记录 |
| `GET` | `/admin/verify/{id}` | 审核付款（通过/拒绝） |

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

### 付款流程

1. 用户积分用完后，首页自动提示充值
2. 跳转 `/payment` 扫码支付（￥1.00 = 3 次）
3. 填写交易单号提交
4. `PAYMENT_AUTO_VERIFY=true` 自动到账，否则管理员在 `/admin/login` 登录后审核

## License

MIT
