# Mutao Assistant 后端API

基于FastAPI的Mutao Assistant后端服务，处理Gemini API调用和流式响应。

## 功能特性

- PS写作分析生成（流式/非流式）
- 强制使用gemini-2.5-pro模型
- 完整的Markdown清理功能
- CORS支持前端跨域调用
- 模块化设计，支持后续扩展其他工具

## API端点

### 通用端点
- `POST /api/gemini/generate` - 普通文本生成
- `POST /api/gemini/stream` - 流式文本生成

### PS写作专用端点
- `POST /api/gemini/ps-write/generate` - PS写作分析（非流式）
- `POST /api/gemini/ps-write/stream` - PS写作分析（流式）

### 系统端点
- `GET /` - API状态
- `GET /health` - 健康检查
- `GET /api/gemini/modules` - 可用模块列表

## 请求参数

### PS写作请求
```json
{
  "school": "目标学校名称",
  "major": "申请专业",
  "courses": "相关课程信息",
  "extracurricular": "课外经历",
  "api_key": "Google Gemini API Key",
  "model_name": "gemini-2.5-pro", // 强制使用此模型
  "temperature": 0.7,
  "max_output_tokens": 4000
}
```

## 本地开发

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行开发服务器：
```bash
python run.py
# 或
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. API将运行在：http://localhost:8000

4. 访问API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 部署到Render

1. 将backend目录推送到GitHub仓库

2. 在Render.com创建新的Web Service

3. 配置：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. 环境变量：
   - `PYTHON_VERSION`: 3.11.0

## 前端配置

前端需要设置环境变量：
```
VITE_API_BASE_URL=https://your-render-app.onrender.com
```

开发环境可创建`.env.local`文件：
```
VITE_API_BASE_URL=http://localhost:8000
```

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI主应用
│   ├── api/
│   │   ├── __init__.py      # API路由注册
│   │   └── gemini.py        # Gemini API处理
├── requirements.txt         # Python依赖
├── run.py                  # 启动脚本
├── render.yaml             # Render部署配置
└── README.md              # 本文档
```

## 后续扩展

### 添加新模块
1. 在`gemini.py`中添加新的提示词构建函数
2. 添加对应的请求模型和端点
3. 更新模块列表

### 支持的模块
- ✅ PS写作 (ps-write)
- ⬜ PS修改 (ps-review)
- ⬜ CV写作 (cv-write)
- ⬜ RL写作 (rl-write)

## 注意事项

1. API Key由前端提供，后端不存储任何密钥
2. 强制使用gemini-2.5-pro模型确保一致性
3. 流式响应使用Server-Sent Events (SSE)
4. 生产环境应配置CORS白名单而非允许所有来源