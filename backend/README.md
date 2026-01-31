# Mutao Assistant - PS写作模块后端

## 项目概述
PS写作模块后端，基于FastAPI和Google Gemini 2.5 Pro开发。

## 功能特性
- 分析学生课外经历，识别3个最匹配的细分领域
- 深度行业调研，生成结构化分析报告
- 交互式选择机制，用户可选择最匹配方向
- 生成完整的5段式个人陈述（Personal Statement）

## 技术栈
- **后端框架**: FastAPI (Python 3.9+)
- **AI模型**: Google Gemini 2.5 Pro
- **部署**: Render
- **数据格式**: JSON

## 开发环境配置

### 1. 安装Python 3.9+
确保系统中已安装Python 3.9或更高版本。

### 2. 创建虚拟环境（Windows）
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
复制`.env.example`为`.env`并填入实际值：
```bash
cp .env.example .env
# 编辑.env文件，填入Gemini API密钥
```

### 5. 启动开发服务器
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 6. 测试API
```bash
curl http://localhost:8001/api/health
```

## 项目结构
```
backend/
├── app/
│   ├── main.py              # FastAPI入口
│   ├── api/
│   │   ├── __init__.py
│   │   └── ps_write.py      # PS写作API端点
│   ├── core/
│   │   ├── config.py        # 配置管理
│   │   └── security.py      # 安全功能
│   ├── models/
│   │   └── schemas.py       # Pydantic数据模型
│   └── services/
│       └── gemini.py        # Gemini服务封装
├── requirements.txt         # Python依赖
├── .env.example            # 环境变量示例
├── render.yaml             # Render部署配置
└── README.md               # 项目说明
```

## API端点

### 健康检查
```
GET /api/health
```

### PS写作API

#### 1. 生成调研选项
```
POST /api/ps-write/generate-with-selection
```
请求体示例：
```json
{
  "school": "目标学校",
  "major": "申请专业",
  "courses": "相关课程描述",
  "extracurricular": "课外经历描述",
  "api_key": "您的Gemini API密钥"
}
```

#### 2. 生成个人陈述
```
POST /api/ps-write/generate-ps
```
请求体示例：
```json
{
  "selection": {
    "selection_index": 0,
    "research_options": [...]  // 从上一个端点获取的调研选项
  },
  "school": "目标学校",
  "major": "申请专业",
  "courses": "相关课程描述",
  "extracurricular": "课外经历描述",
  "api_key": "您的Gemini API密钥"
}
```

#### 3. 测试端点
```
GET /api/ps-write/test-gemini?api_key=您的API密钥     # 测试Gemini连接
GET /api/ps-write/test-prompt-format                  # 测试提示词格式
GET /api/ps-write/session/{session_id}                # 获取会话信息
GET /api/ps-write/cache-stats                         # 获取缓存统计信息
GET /api/ps-write/clear-cache                         # 清空调研缓存（测试用）
POST /api/ps-write/validate-references                # 测试参考文献验证
```

## 部署到Render

### 1. 推送到GitHub仓库
将代码推送到GitHub仓库。

### 2. 在Render创建Web Service
- 选择"New Web Service"
- 连接GitHub仓库
- 使用`render.yaml`配置自动部署

### 3. 配置环境变量
在Render Dashboard中设置环境变量：
- `GEMINI_API_KEY`: 你的Gemini API密钥
- `DEBUG`: false (生产环境)
- `SESSION_TTL_MINUTES`: 30

## 开发计划

### 阶段1-2：基础框架（已完成）
- 项目结构搭建
- FastAPI核心框架
- 环境配置管理

### 阶段3-4：AI集成与数据模型（已完成）
- ✓ Gemini API集成与服务封装
- ✓ 提示词工程与模板设计
- ✓ Pydantic数据模型设计
- ✓ 代理配置与错误处理
- ✓ 测试端点和验证机制

### 阶段5：调研分析功能实现（已完成）
- ✓ 调研结果解析器完善（文本转结构化数据）
- ✓ 匹配度评分算法实现（基于内容的关键词匹配和结构分析）
- ✓ 参考文献真实性验证（格式检查、权威来源识别、质量评分）
- ✓ 调研结果缓存机制（24小时TTL，LRU淘汰策略）
- ✓ 缓存统计和清理端点

### 阶段6：交互选择与会话管理（待开发）
- 交互选择机制完善
- 会话状态管理优化
- 安全防护机制

### 阶段7-8：完整实现（待开发）
- 个人陈述生成功能完善
- 测试优化与性能调优
- 生产部署与监控

## 注意事项

1. **API密钥安全**: 永远不要将API密钥提交到版本控制
2. **代理配置**: 本地开发可能需要配置HTTP代理
3. **CORS设置**: 生产环境应限制允许的域名
4. **错误处理**: 所有API端点都应包含适当的错误处理

## 故障排除

### 常见问题
1. **导入错误**: 确保虚拟环境已激活且依赖已安装
2. **端口占用**: 更改`--port`参数使用其他端口
3. **API密钥无效**: 检查.env文件中的GEMINI_API_KEY
4. **代理问题**: 检查本地代理服务是否运行

### 日志查看
启动时添加`--log-level debug`查看详细日志：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 --log-level debug
```

## 联系方式
- **项目负责人**: [填写联系方式]
- **技术支持**: [填写联系方式]
- **问题反馈**: [填写GitHub Issues链接]