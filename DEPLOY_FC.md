# 🚀 部署指南 - 阿里云函数计算 FC

## 方案选择

| 方案 | 难度 | 说明 |
|------|------|------|
| **⭐ 自定义容器（推荐）** | ⭐⭐ | 无需改代码，功能完整，推荐 |
| Python Runtime (ZIP 上传) | ⭐⭐⭐ | 需要适配代码，功能受限 |
| 本地演示 (localhost) | ⭐ | 仅本地可用，面试官无法访问 |

---

## 方案一：自定义容器部署（推荐）

### 前置条件

- [阿里云账号](https://aliyun.com/) 并完成实名认证
- 本地安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- 配置好 `backend/.env` 中的 `DASHSCOPE_API_KEY`

### 步骤 1：构建 Docker 镜像

```bash
cd demo_for_interview/backend

# 构建镜像
docker build -t resume-analyzer:latest .
```

### 步骤 2：推送到阿里云容器镜像服务（CR）

```bash
# 登录阿里云 Docker Registry
# 替换 cn-beijing 为你的地域，xxx 为你的阿里云账号 ID
docker login --username=xxx@aliyun.com registry.cn-beijing.aliyuncs.com

# 打标签
docker tag resume-analyzer:latest registry.cn-beijing.aliyuncs.com/<你的命名空间>/resume-analyzer:latest

# 推送
docker push registry.cn-beijing.aliyuncs.com/<你的命名空间>/resume-analyzer:latest
```

> 阿里云容器镜像服务地址：https://cr.console.aliyun.com/
> 首次使用需要创建命名空间，设置密码

### 步骤 3：创建 FC 函数

1. 打开 https://fc.console.aliyun.com/
2. 点击 **创建函数** → **使用容器镜像**
3. 配置：
   - **函数名称**：`resume-analyzer`
   - **镜像地址**：选择上一步推送的镜像
   - **启动命令**：`uvicorn app:app --host 0.0.0.0 --port 9000`
   - **监听端口**：`9000`
   - **环境变量**：添加 `DASHSCOPE_API_KEY` = 你的 API Key
   - **内存**：512MB（推荐）
   - **超时时间**：120 秒
4. 点击 **创建**
5. 创建 **HTTP 触发器**：
   - 认证方式：**无需认证**（方便面试官访问）
   - 请求方法：GET、POST

### 步骤 4：获取公网 URL

创建完成后，在函数详情页的 **触发器** 标签页中，会看到一个公网访问地址，类似：

```
https://resume-analyzer-xxxxx.cn-beijing.fc.aliyuncs.com
```

验证是否可用：

```bash
curl https://你的FC域名/health
# 预期输出: {"status":"healthy"}
```

### 步骤 5：更新前端指向后端

拿到 FC URL 后，执行以下命令构建并部署前端：

```bash
cd demo_for_interview/frontend

# 方式 A：构建时指定后端地址（推荐）
VITE_API_BASE=https://你的FC域名 npm run build

# 方式 B：或使用脚本（见下方说明）
```

---

## 方案二：Python Runtime ZIP 部署（备选）

如果 Docker 不方便，可以用 ZIP 方式部署到 FC Python 3.10 Runtime。

### 准备部署包

> 此方案功能受限，如需完整 API 功能建议用方案一

按照 FC 控制台的上传代码方式，将 `backend/` 目录打包为 ZIP（不含 `.env`），设置：
- **运行环境**：Python 3.10
- **函数入口**：`app.handler`
- **HTTP 触发器**：无需认证

---

## 更新前端（得到 FC URL 后联系我 👋）

拿到 FC URL 后，可以让我帮你一键完成：

```bash
# 1. 构建前端，API 指向你的 FC 域名
cd frontend
VITE_API_BASE=https://你的FC域名 npm run build

# 2. 将构建结果推送到 gh-pages 分支
```

或者你手动执行，然后将当前页面的 URL 发给面试官：

```
演示地址：https://ru0608.github.io/resume-analyzer/
```

---

## 架构总览

```
用户浏览器 ──▶ GitHub Pages (前端) ──▶ 阿里云 FC (后端) ──▶ DashScope API
                                          │
                                     DASHSCOPE_API_KEY
```

部署完成后，面试官只需要访问 GitHub Pages 地址，就能完整使用全部功能（上传 PDF → AI 提取 → 匹配评分）。
