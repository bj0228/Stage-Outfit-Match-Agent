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


当前版本为了稳定演示，商品链接采用“电商搜索链接”方案，不声称某个具体商品一定存在。这样比直接编造商品详情更可靠，也更符合演示场景。后续如果要做商业版本，可以接淘宝联盟、京东联盟、SerpAPI 或 Google Shopping API。
