# AI 小红书爆款生成器

基于多 Agent 协作的 AI 小红书笔记文案自动生成平台。输入内容方向，AI 自动完成选题策划 → 文案创作 → 爆款优化 → 合规检测，一键生成爆款笔记。

## 功能亮点

- **选题策划** — TopicAgent 分析热门趋势，生成爆款选题方向
- **AI 创作** — ContentAgent 根据选题创作完整小红书文案
- **爆款优化** — OptimizeAgent 优化标题吸引力与正文互动率
- **合规检测** — RiskAgent 自动检测敏感内容并标注风险等级（低/中/高）
- **每日限额** — 可配置免费使用次数，防止滥用

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| AI 引擎 | LangChain Agent + DeepSeek API |
| 数据库 | SQLAlchemy + SQLite |
| 前端 | Jinja2 模板 + TailwindCSS (CDN) |
| 样式 | 暗色编辑风格，纯 CSS 动画 |

## 项目结构

```
├── main.py                     # FastAPI 入口，路由定义
├── config.py                   # 环境变量配置
├── database.py                 # 数据库连接与会话管理
├── requirements.txt            # Python 依赖清单
│
├── agents/                     # LangChain Agent 层
│   ├── base.py                 # Agent 基类（LLM 初始化、构建、运行）
│   ├── topic_agent.py          # 选题策划 Agent
│   ├── content_agent.py        # 文案生成 Agent
│   ├── optimize_agent.py       # 爆款优化 Agent
│   └── risk_agent.py           # 风险检测 Agent
│
├── prompts/                    # Agent 系统提示词
│   ├── topic.txt               # 选题策划师提示词
│   ├── content.txt             # 文案写手提示词
│   ├── optimize.txt            # 优化专家提示词
│   └── risk.txt                # 审核专家提示词
│
├── services/                   # 业务服务层
│   └── content_service.py      # 生成流程编排、结果解析、限额检查
│
├── models/                     # 数据模型
│   └── post.py                 # Post SQLAlchemy 模型
│
├── templates/                  # Jinja2 前端模板
│   ├── layout.html             # 基础布局（暗色编辑风格）
│   ├── index.html              # 首页（输入、快速标签、功能卡片）
│   └── result.html             # 结果页（杂志式阅读布局）
│
├── static/                     # 静态资源（预留）
│   ├── css/style.css
│   └── js/main.js
│
├── .env.example                # 环境变量模板
└── .gitignore                  # Git 忽略规则
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：

```env
LLM_API_KEY=sk-your-api-key-here
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-pro
LLM_TEMPERATURE=0.7
DATABASE_URL=sqlite:///./xhs.db
FREE_DAILY_LIMIT=3
```

> `.env` 已加入 `.gitignore`，不会被提交到版本控制。

### 3. 启动服务

```bash
python main.py
```

访问 `http://localhost:8000` 即可使用。

## 配置说明

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `LLM_API_KEY` | DeepSeek API 密钥 | - |
| `LLM_BASE_URL` | API 地址 | `https://api.deepseek.com` |
| `LLM_MODEL` | 模型名称 | `deepseek-v4-pro` |
| `LLM_TEMPERATURE` | 生成温度 (0-1) | `0.7` |
| `DATABASE_URL` | 数据库连接 | `sqlite:///./xhs.db` |
| `FREE_DAILY_LIMIT` | 每日免费次数 | `3` |

> 如使用其他 OpenAI 兼容 API（如通义千问、智谱 GLM），修改 `LLM_BASE_URL` 和 `LLM_MODEL` 即可。

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 首页 |
| `POST` | `/generate` | 生成文案（Body: `{"topic": "内容方向"}`） |
| `GET` | `/result/{post_id}` | 查看生成结果 |

## License

MIT
