# 🚀 部署指南 - Render.com

## 为什么选 Render？

- 🆓 **免费额度**：每月 750 小时，足够演示用
- 🔗 **直接连接 GitHub**：推送代码自动部署
- 🌐 **自动 HTTPS/SSL**：无需额外配置
- ⚡ **部署只需 2 步**

---

## 第一步：注册 Render 并连接 GitHub

> 你需要先注册一个 Render 账号

1. 打开 https://dashboard.render.com/register
2. 点击 **"Sign up with GitHub"**
3. 授权 Render 访问你的仓库（选择 `ru0608/resume-analyzer`）
4. 完成注册

> 注册只需要 GitHub 账号，不需要绑信用卡也能用免费额度

---

## 第二步：部署后端（Web Service）

注册登录后：

1. 点击 **"New +"** → **"Web Service"**
2. 连接 GitHub → 选择 **`ru0608/resume-analyzer`**
3. 配置（逐项填）：

| 配置项 | 值 |
|--------|-----|
| **Name** | `resume-analyzer` |
| **Region** | `Singapore`（东南亚，国内访问最快） |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}` |
| **Instance Type** | **Free** ✅ |

4. 展开 **"Advanced"** → 点击 **"Add Environment Variable"**
   - `DASHSCOPE_API_KEY` = 你的通义千问 API Key
   - `DASHSCOPE_MODEL` = `qwen-plus`

5. 点击 **"Create Web Service"**
6. 等待 3-5 分钟部署完成 🎉

---

## 第三步：获取后端地址

部署成功后，页面顶部会显示：

```
https://resume-analyzer.onrender.com  ← 这就是你的后端地址
```

验证一下：

```bash
curl https://resume-analyzer.onrender.com/health
# 应该返回: {"status": "healthy"}
```

---

## 第四步：更新前端

拿到后端地址后，**把地址发给我**，我帮你完成：

```bash
# 1. 用 Render 地址重新构建前端
cd frontend
VITE_API_BASE=https://resume-analyzer.onrender.com npm run build

# 2. 推送到 gh-pages 分支（GitHub Pages 自动更新）
```

然后面试官访问以下地址就能完整使用：

```
🌐 演示地址：https://ru0608.github.io/resume-analyzer/
```

---

## 最终架构

```
面试官 ──▶ https://ru0608.github.io/resume-analyzer/  (前端, GitHub Pages)
                │
                ▼ (API 请求)
         https://resume-analyzer.onrender.com          (后端, Render)
                │
                ▼
         通义千问 DashScope API                         (AI 模型)
```

---

## 常见问题

**Q: Free 计划会休眠吗？**
A: Render 的免费服务 15 分钟无访问会休眠，再次访问会冷启动（等 10-30 秒）。这个不影响面试官验收。

**Q: Free 计划够用吗？**
A: 每月 750 小时 ≈ 每天 25 小时，完全够面试演示用。

**Q: 部署失败怎么办？**
A: 把部署日志发给我，我帮你排查。
