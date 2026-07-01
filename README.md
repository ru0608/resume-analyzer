# 📄 AI 赋能的智能简历分析系统

> 后端服务 + 前端交互页面，支持简历 PDF 上传解析、AI 关键信息提取与岗位匹配评分。

## 项目简介

在招聘流程中，快速筛选和分析大量简历是一项耗时的工作。本系统能够自动解析上传的 PDF 简历，提取关键信息，并利用 AI 模型（阿里云通义千问）对简历进行评分和关键词匹配，帮助招聘者快速筛选候选人。

### 功能模块

| 模块 | 功能 | 状态 |
|------|------|------|
| 简历上传与解析 | PDF 上传、文本提取、清洗结构化 
| 关键信息提取 | AI 提取姓名/电话/邮箱/地址/求职意向等 
| 简历评分与匹配 | 岗位需求匹配度计算、AI 精准评分 
| 结果返回与缓存 | JSON 结构化返回、Redis/内存缓存 
|  前端页面 | React + Vite 交互页面，部署到 GitHub Pages 

## 技术架构

```
┌──────────────┐     ┌──────────────┐     ┌────────────┐
│  前端 React   │────▶│  后端 FastAPI │────▶│  DashScope │
│  (Vite + SPA) │◀────│  (Python)    │◀────│  (通义千问) │
│              │     │              │     │            │
│ GitHub Pages │     │  阿里云 FC    │     │  AI 模型   │
└──────────────┘     └──────┬───────┘     └────────────┘
                            │
                     ┌──────▼───────┐
                     │   Redis 缓存  │
                     │  (可选/内存)  │
                     └──────────────┘
```

### 技术栈

- **后端**: Python 3.14+, FastAPI, PyMuPDF, DashScope SDK
- **前端**: React 19, Vite, Fetch API
- **AI**: 阿里云通义千问 Qwen-Plus (DashScope API)
- **缓存**: Redis (可选，默认降级为内存缓存)
- **部署**: 阿里云函数计算 FC (后端) + GitHub Pages (前端)

## 项目结构

```
demo_for_interview/
├── backend/
│   ├── app.py                  # FastAPI 主入口
│   ├── config.py               # 配置管理
│   ├── requirements.txt        # Python 依赖
│   ├── .env.example            # 环境变量示例
│   ├── routers/
│   │   ├── resume.py           # 简历上传与解析 API
│   │   └── match.py            # 简历匹配评分 API
│   ├── services/
│   │   ├── parser.py           # PDF 解析服务
│   │   ├── extractor.py        # AI 信息提取服务
│   │   ├── scorer.py           # AI 评分与匹配服务
│   │   └── cache.py            # Redis/内存缓存服务
│   ├── models/
│   │   └── schemas.py          # Pydantic 数据模型
│   └── utils/
│       └── text_cleaner.py     # 文本清洗工具
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # 主页面组件
│   │   ├── App.css             # 页面样式
│   │   ├── api.js              # API 调用封装
│   │   └── main.jsx            # 入口文件
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## 快速开始

### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 DashScope API Key

# 启动服务
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

启动后 API 文档地址：http://localhost:8000/docs

### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端默认地址：http://localhost:5173

### 3. 环境变量配置

在 `backend/.env` 中配置：

| 变量 | 说明 | 必填 |
|------|------|------|
| DASHSCOPE_API_KEY | 阿里云通义千问 API Key | 是 |
| DASHSCOPE_MODEL | 模型名称 (qwen-plus/qwen-turbo) | 否 |
| REDIS_HOST | Redis 地址 | 否 (不配置则用内存缓存) |
| REDIS_PORT | Redis 端口 | 否 |

> 获取 DashScope API Key: https://dashscope.aliyun.com/

## API 文档

### 常见 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/resume/upload` | 上传简历 PDF，返回解析结果和提取信息 |
| GET | `/api/resume/{resume_id}` | 获取已解析的简历信息 |
| POST | `/api/match/score` | 简历与岗位需求匹配评分 |
| GET | `/health` | 健康检查 |

## 部署

### 完整部署指南

查看 [DEPLOY.md](./DEPLOY.md) 获取详细的部署步骤。

快速概览：

1. 注册 [Render.com](https://dashboard.render.com/register)（用 GitHub 登录）
2. 一键部署后端 Web Service
3. 告知我 Render 后端地址，我更新前端构建
4. 面试官访问 GitHub Pages 演示地址即可验收

## 评分方案

### 评分维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 技能匹配度 | 40% | 技术栈、专业技能匹配程度 |
| 经验相关性 | 30% | 行业经验、岗位职责匹配度 |
| 学历背景 | 15% | 学历层次评估 |
| 关键词匹配 | 15% | 岗位需求关键词命中率 |

AI 评分模式下，以上维度由通义千问模型综合评估，提供更精准的匹配度分析。

## 开源协议

MIT
