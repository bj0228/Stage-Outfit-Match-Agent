# Stage Outfit Match Agent

中文名：演出服搭配智能体

这是一个面向舞蹈演出、校园晚会、比赛舞台的 AI 搭配智能体。用户输入舞蹈题目或视频链接，选择想要的风格，系统自动生成五套完整演出服搭配，并提供衣服、鞋子、配饰、价格、参考来源、商品搜索链接和 PDF 搭配报告。

## 功能

一、输入信息

1. 舞蹈题目或视频链接
2. 风格按钮：甜美、帅气、性感、休闲、灵动、韩系、女团风、学院风
3. 预算选择：低预算、中预算、高预算

二、智能体输出

1. 舞蹈风格分析
2. 风格关键词
3. 参考来源，例如某 idol 舞台风格
4. 五套演出服搭配推荐
5. 每套包含上衣、下装、鞋子、配饰
6. 每个单品包含价格和淘宝/京东/拼多多搜索链接
7. 按总价从低到高排序
8. 自动生成 PDF 报告

## 技术栈

前端：

1. Vue 3
2. Vite
3. Element Plus
4. Axios
5. Lucide Icons

后端：

1. FastAPI
2. Python 3.11
3. ReportLab
4. OpenAI API / 通义千问 API / Mock 模式

## 项目结构

```text
stage-outfit-match-agent/
├── backend/
│   ├── app.py
│   ├── agent/
│   │   ├── outfit_agent.py
│   │   ├── product_searcher.py
│   │   └── report_generator.py
│   ├── llm/
│   │   └── llm_client.py
│   ├── reports/
│   ├── requirements.txt
│   ├── runtime.txt
│   └── .env.example
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── api/
│       │   └── agent.js
│       └── styles/
│           └── main.css
├── demo_materials/
│   ├── demo_script.md
│   └── sample_input.md
├── Dockerfile
├── render.yaml
└── README.md
```

## 本地启动

### 一、启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

健康检查：

```text
http://127.0.0.1:8000/api/health
```

### 二、启动前端

```bash
cd frontend
npm install
npm run dev
```

访问：

```text
http://127.0.0.1:5173
```

## API Key 配置

默认使用 mock 模式，不需要 API Key，适合演示和部署测试。

使用通义千问：

```env
LLM_PROVIDER=qwen
DASHSCOPE_API_KEY=你的 DashScope API Key
QWEN_MODEL=qwen-plus
```

使用 OpenAI：

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=你的 OpenAI API Key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

注意：不要把真实 API Key 提交到 GitHub。

## Mock 模式说明

`.env` 中设置：

```env
LLM_PROVIDER=mock
```

系统会返回一组稳定的演出服搭配结果，包含五套搭配、搜索链接和 PDF 报告，方便录制视频和提交作业。

## 部署方案：Render + GitHub Pages

### 一、后端部署到 Render

1. 把项目上传到 GitHub。
2. 打开 Render，新建 Web Service。
3. 选择该 GitHub 仓库。
4. Root Directory 留空。
5. 选择 Docker 部署，Render 会读取根目录的 `Dockerfile`。
6. 环境变量设置：

```env
LLM_PROVIDER=mock
ALLOWED_ORIGINS=*
```

如果使用千问：

```env
LLM_PROVIDER=qwen
DASHSCOPE_API_KEY=你的 DashScope API Key
QWEN_MODEL=qwen-plus
ALLOWED_ORIGINS=*
```

7. 部署完成后访问：

```text
https://你的-render域名/api/health
```

看到 `{"status":"ok"}` 表示后端成功。

### 二、前端部署到 GitHub Pages

最简单方式是使用 Vercel。也可以用 GitHub Pages，但需要配置构建工作流。

前端构建环境变量：

```env
VITE_API_BASE_URL=https://你的-render域名
```

如果用 Vercel：

1. New Project
2. 选择 GitHub 仓库
3. Root Directory 选择 `frontend`
4. Build Command：`npm run build`
5. Output Directory：`dist`
6. 添加环境变量 `VITE_API_BASE_URL`
7. Deploy

## 示例输入

```text
我想跳 NewJeans《Super Shy》，想要适合学校舞台的女团风演出服。
```

风格选择：

```text
甜美
```

预算：

```text
中预算
```

## 预期输出

1. 舞蹈风格分析
2. NewJeans / IVE / BLACKPINK 等舞台参考来源
3. 五套搭配推荐
4. 每套包含上衣、下装、鞋子、配饰
5. 每个单品有价格与淘宝/京东/拼多多搜索链接
6. 搭配总价从低到高
7. 可下载 PDF 搭配报告

## MP4 演示建议

录制 3 到 5 分钟：

1. 展示公开访问链接
2. 输入舞蹈题目或链接
3. 点击风格按钮
4. 点击生成五套搭配
5. 展示运行日志
6. 展示五套搭配卡片
7. 点击商品搜索链接
8. 下载 PDF 报告
9. 打开 PDF 报告
10. 总结系统满足公开访问、AI Agent、PDF 输出和视频演示要求

## 提交材料清单

1. GitHub 仓库链接
2. 前端公开访问链接
3. 后端健康检查链接
4. MP4 演示视频
5. 下载生成的 PDF 报告

## 注意事项

当前版本为了稳定演示，商品链接采用“电商搜索链接”方案，不声称某个具体商品一定存在。这样比直接编造商品详情更可靠，也更符合演示场景。后续如果要做商业版本，可以接淘宝联盟、京东联盟、SerpAPI 或 Google Shopping API。
