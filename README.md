# 🏠 HomeService - 家政智能预约系统

> **可端到端演示的家政智能预约系统，多 Agent 路由 + RAG + MCP 模拟接口 + 完整订单流程 + 自动化测试覆盖**

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Tests](https://img.shields.io/badge/Tests-Pytest-9cf)

---

## 📋 目录

- [核心特性](#-核心特性)
- [快速开始](#-快速开始)
- [系统架构](#-系统架构)
- [功能模块](#-功能模块)
- [API 文档](#-api-文档)
- [测试覆盖](#-测试覆盖)
- [部署方式](#-部署方式)
- [技术栈](#-技术栈)

---

## 🌟 核心特性

| 特性 | 说明 |
|------|------|
| **📊 智能多 Agent 路由** | 基于 LangGraph 的预约 Agent、咨询 Agent、复购推荐 Agent，实现智能请求分发 |
| **📚 RAG 知识检索** | 支持知识文档上传、向量化检索，为智能问答提供语义搜索能力 |
| **🔧 MCP 模拟接口** | 日历、地图、通知等 Mock 接口，便于快速开发与演示 |
| **🛒 完整订单流程** | 从报价、预约、派单到订单管理，覆盖家政服务全生命周期 |
| **🧪 自动化测试** | 20+ 单元测试与集成测试，覆盖核心业务逻辑 |
| **🐳 Docker 支持** | 提供/docker-compose.yml，一键启动 PostgreSQL + Redis + 应用 |

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目（或解压后进入目录）
cd HomeService

# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境配置

```bash
# 生成 .env 文件
bash gen-env.sh

# 或手动复制模板
cp .env.example .env
# 编辑 .env 填写 API Key
```

### 3. 启动服务

```bash
# 方式一：直接启动（开发模式）
uvicorn HomeService.app:app --reload --host 0.0.0.0 --port 8000

# 方式二：Docker 启动
docker-compose up -d
```

### 4. 访问应用

- **Web 页面**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/healthz

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     客户端层 (Client Layer)                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐       │
│  │  Web    │ │  App    │ │  Mini   │ │  Third-party│       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway Layer                         │
│  Auth │ Rate Limit │ Logging │ CORS                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                Agent Router (LangGraph)                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐    │
│  │ Appointment  │ │  Consult   │ │ Recommendation   │    │
│  │   Agent      │ │   Agent    │ │     Agent        │    │
│  └──────────────┘ └──────────────┘ └──────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐ ┌───────────────┐ ┌──────────────────┐
│   Pricing     │ │ Scheduling    │ │    RAG Retrieval │
│   Service     │ │   Service     │ │    Service       │
└───────┬───────┘ └───────┬───────┘ └────────┬─────────┘
        │                 │                  │
        ▼                 ▼                  ▼
┌───────────────┐ ┌───────────────┐ ┌──────────────────┐
│   Order       │ │   User        │ │     MCP Access   │
│   Service     │ │   Service     │ │   (Mock)         │
└───────┬───────┘ └───────┬───────┘ └──────────────────┘
        │                 │
        ▼                 ▼
┌──────────────────────────────────────────┐
│          Data Persistence Layer          │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐  │
│  │PostgreSQL│ │ SQLite  │ │  Redis   │  │
│  └──────────┘ └─────────┘ └──────────┘  │
└──────────────────────────────────────────┘
```

---

## ✨ 功能模块

### 1. 智能预约与报价

- ✅ 根据服务类型和面积自动计算价格
- ✅ 支持附加服务（如深度清洁、擦窗等）
- ✅ 实时查询师傅可用时段
- ✅ 智能派单与冲突检测

### 2. 用户管理

- ✅ 用户注册与信息管理
- ✅ 多地址管理
- ✅ 订单历史查询
- ✅ 个性化服务推荐

### 3. 知识库与智能问答

- ✅ 文档上传（支持文本、策略、服务说明）
- ✅ 向量化存储与检索
- ✅ 语义搜索答案

### 4. 订单全生命周期

- ✅ 创建订单 → 确认报价
- ✅ 查看订单状态
- ✅ 改约时间
- ✅ 取消订单

### 5. 管理后台（需要 Auth）

- ✅ 服务项目管理
- ✅ 分类管理
- ✅ 套餐管理
- ✅ 师傅排班管理

---

## 🔌 API 文档

### 快速测试

#### 1. 获取管理员 Token
```bash
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'
```

#### 2. 创建用户
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"张三","phone":"13800138000"}'
```

#### 3. 查询报价
```bash
curl -X POST http://localhost:8000/api/appointments/quote \
  -H "Content-Type: application/json" \
  -d '{"service_type":"daily_cleaning","area":80,"extras":{}}'
```

#### 4. 创建预约
```bash
curl -X POST http://localhost:8000/api/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":1,
    "address_id":1,
    "service_item_id":1,
    "scheduled_start":"2024-06-15 10:00:00",
    "scheduled_end":"2024-06-15 13:00:00",
    "estimated_price":300,
    "final_price":300
  }'
```

#### 5. 知识库搜索
```bash
curl "http://localhost:8000/api/knowledge/search?q=家政"
```

更多 API 示例请查看 [API 文档](http://localhost:8000/docs)（启动服务后）。

---

## 🧪 测试覆盖

### 测试命令

```bash
pytest tests/ -v --tb=short
```

### 测试结果

```
20 passed, 2 warnings in 0.24s
```

### 测试模块

| 测试文件 | 覆盖内容 |
|----------|----------|
| `test_api.py` | 用户管理、地址管理 API |
| `test_appointments.py` | 报价、预约、订单流程 |
| `test_rag.py` | 知识库上传、搜索、检索 |
| `test_services.py` | 报价服务、定价模型 |

---

## 🐳 部署方式

### Docker 部署

```bash
# 构建镜像
docker build -t homeservice:latest .

# 启动服务
docker run -p 8000:8000 homeservice:latest
```

### Docker Compose 部署

```bash
docker-compose up -d
```

Docker Compose 包含：
- `homeservice`：主应用服务（端口 8000）
- `db`：PostgreSQL 数据库
- `cache`：Redis 缓存

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | 数据库连接 | `sqlite:///./homeservice.db` |
| `API_SECRET_KEY` | API 密钥 | 自动生成 32 字符 |
| `ADMIN_USERNAME` | 管理员用户名 | `admin` |
| `ADMIN_PASSWORD` | 管理员密码 | `password123` |
| `LLM_PROVIDER` | LLM 提供商 | `claude` |
| `LLM_API_KEY` | LLM API Key | - |
| `LLM_MODEL_NAME` | 模型名称 | `claude-3-5-sonnet` |
| `DEBUG` | 调试模式 | `false` |

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **Web 框架** | FastAPI |
| **数据库** | SQLAlchemy + SQLite/PostgreSQL |
| **缓存** | Redis |
| **AI 框架** | LangChain / LangGraph |
| **测试框架** | Pytest |
| **容器化** | Docker |

---

## 📁 项目结构

```
HomeService/
├── HomeService/              # 核心代码包
│   ├── api/                  # API 路由
│   ├── agents/               # AI Agent 路由
│   ├── services/             # 业务服务层
│   ├── db/                   # 数据库模型
│   ├── models/               # LLM 模型接口
│   ├── utils/                # 工具函数
│   └── static/               # 静态文件
├── tests/                    # 测试文件
├── .env.example             # 环境变量示例
├── docker-compose.yml       # Docker 编排
├── Dockerfile               # Docker 镜像定义
├── gen-env.sh               # 环境变量生成脚本
├── requirements.txt         # 依赖列表
└── README.md               # 项目说明
```

---

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

---

## 🤝 贡献指南

欢迎提交 Issue 和 PR！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📚 相关文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [LangChain 文档](https://python.langchain.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)

---

## 📧 联系方式

如有问题或建议，欢迎通过 GitHub Issues 联系。

---

<div align="center">

**如果这个项目对你有帮助，欢迎点赞支持！⭐**

</div>
