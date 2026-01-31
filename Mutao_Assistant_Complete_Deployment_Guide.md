# Mutao Assistant - PS写作功能完整部署指南

## 项目概述
开发一个基于FastAPI和Google Gemini 2.5 Pro的**PS写作模块**后端。这是Mutao Assistant留学文书工具中的独立模块，后续将单独开发PS修改、推荐信（RL）写作、简历（CV）写作等独立模块。

**PS写作模块核心功能**：
1. 分析学生课外经历，识别与申请专业最匹配的3个细分领域
2. 进行深度行业调研，生成结构化分析报告
3. 提供交互式选择机制，用户可选择最匹配的方向
4. 基于用户选择生成完整的5段式个人陈述（Personal Statement）

**模块独立性设计**：
- 独立API路由结构，不与其他文书模块耦合
- 专用数据模型和业务逻辑
- 可复用的AI服务层封装
- 独立的部署和配置管理

## 核心功能模块
### 1. 调研分析模块
- 输入：学校、专业、课程、课外经历
- 输出：3个细分领域调研报告（按匹配度排序）

### 2. 交互选择模块
- 前端展示3个调研选项
- 用户选择最匹配的方向
- 会话状态管理

### 3. 个人陈述生成模块
- 基于用户选择生成5段式个人陈述
- 纯文本输出，无任何Markdown符号
- 结构化段落：动机、学习经历、课外经历、选校理由、职业规划

## 技术栈
- **后端框架**: FastAPI (Python 3.9+)
- **AI模型**: Google Gemini 2.5 Pro
- **代理**: HTTP_PROXY=http://127.0.0.1:7897 (本地调试)
- **部署**: Render
- **数据格式**: JSON
- **会话存储**: 内存缓存（生产环境建议Redis）

## 项目结构
```
backend/
├── app/
│   ├── main.py                    # FastAPI入口
│   ├── api/
│   │   ├── __init__.py
│   │   └── ps_write.py            # 核心API端点
│   ├── core/
│   │   ├── config.py              # 配置管理
│   │   └── security.py
│   ├── models/
│   │   └── schemas.py             # Pydantic数据模型
│   └── services/
│       ├── gemini.py              # Gemini服务封装
│       └── selection.py           # 选择服务管理
├── requirements.txt
├── .env.example
├── render.yaml
└── README.md
```

## 环境配置
### 1. 本地开发环境
```bash
# 创建项目目录
mkdir backend && cd backend

# 创建虚拟环境（Windows）
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install fastapi uvicorn google-generativeai pydantic python-dotenv pydantic-settings

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 2. 环境变量配置 (.env)
```env
# API配置
GEMINI_API_KEY=your_gemini_api_key_here

# 代理配置（本地开发需要）
HTTP_PROXY=http://127.0.0.1:7897
HTTPS_PROXY=http://127.0.0.1:7897

# 应用配置
DEBUG=true
SESSION_TTL_MINUTES=30
MAX_RETRY_ATTEMPTS=3
```

## 核心API端点
### 1. 健康检查
```
GET /api/health
```
响应：应用状态检查

### 2. 生成调研选项（供用户选择）
```
POST /api/ps-write/generate-with-selection
```
请求体：
```json
{
  "school": "目标学校",
  "major": "申请专业",
  "courses": "相关课程描述",
  "extracurricular": "课外经历描述",
  "api_key": "用户提供的Gemini API密钥"
}
```
响应：
```json
{
  "session_id": "唯一会话ID",
  "research_options": [
    {
      "title": "细分领域名称",
      "match_score": 85,
      "summary": "一句话总结",
      "reasoning": ["详细理由1", "详细理由2"],
      "references": ["参考文献1", "参考文献2"]
    },
    // ... 共3个选项
  ]
}
```

### 3. 生成个人陈述
```
POST /api/ps-write/generate-ps
```
请求体：
```json
{
  "selection": {
    "selection_index": 0,
    "research_options": [...]  // 完整的调研选项列表
  },
  "school": "目标学校",
  "major": "申请专业",
  "courses": "相关课程描述",
  "extracurricular": "课外经历描述",
  "api_key": "用户提供的Gemini API密钥"
}
```
响应：
```json
{
  "paragraphs": [
    "第一段：申请动机内容...",
    "第二段：学习经历内容...",
    "第三段：课外经历内容...",
    "第四段：选校理由内容...",
    "第五段：职业规划内容..."
  ],
  "selected_domain": "选择的细分领域",
  "generated_at": "生成时间戳"
}
```

## 核心代码实现

### 1. 数据模型 (models/schemas.py)
```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ResearchOption(BaseModel):
    """调研选项数据模型"""
    title: str
    match_score: int  # 70-100
    summary: str      # 一句话总结
    reasoning: List[str]  # 详细理由列表
    references: List[str] # 参考文献列表

class UserSelection(BaseModel):
    """用户选择数据模型"""
    selection_index: int  # 0, 1, 2
    research_options: List[ResearchOption]
    timestamp: str

class PSWriteRequest(BaseModel):
    """PS生成请求"""
    school: str
    major: str
    courses: str
    extracurricular: str
    api_key: str

class PSGenerationRequest(BaseModel):
    """个人陈述生成请求"""
    selection: UserSelection
    school: str
    major: str
    courses: str
    extracurricular: str
    api_key: str

class PersonalStatement(BaseModel):
    """个人陈述响应"""
    paragraphs: List[str]  # 5个段落
    selected_domain: str
    generated_at: str
```

### 2. Gemini服务封装 (services/gemini.py)
```python
import google.generativeai as genai
import os
import asyncio
from typing import AsyncGenerator

class GeminiService:
    def __init__(self, api_key: str):
        # 配置代理（本地开发）
        os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
        os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'

        # 配置Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    async def generate_enhanced_research(self, prompt: str) -> str:
        """生成增强版调研结果"""
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API调用失败: {str(e)}")

    async def generate_personal_statement(self, prompt: str) -> str:
        """生成个人陈述"""
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"个人陈述生成失败: {str(e)}")
```

### 3. 选择服务管理 (services/selection.py)
```python
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional

class SelectionService:
    def __init__(self, ttl_minutes: int = 30):
        self.user_sessions: Dict[str, dict] = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def create_session(self, research_options: list) -> str:
        """创建用户会话"""
        session_id = str(uuid.uuid4())
        self.user_sessions[session_id] = {
            'research_options': research_options,
            'created_at': datetime.now()
        }
        self._cleanup_expired()
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话数据"""
        if session_id in self.user_sessions:
            session = self.user_sessions[session_id]
            if datetime.now() - session['created_at'] < self.ttl:
                return session
            else:
                del self.user_sessions[session_id]
        return None

    def _cleanup_expired(self):
        """清理过期会话"""
        current_time = datetime.now()
        expired_keys = [
            key for key, session in self.user_sessions.items()
            if current_time - session['created_at'] >= self.ttl
        ]
        for key in expired_keys:
            del self.user_sessions[key]
```

### 4. 核心提示词模板
```python
# 增强版调研提示词
ENHANCED_RESEARCH_PROMPT = """
你是一个留学申请顾问，需要分析申请者的背景信息，提供专业领域的前沿研究方向和深度行业调研。

申请者信息：
- 目标学校：{school}
- 申请专业：{major}
- 相关课程：{courses}
- 课外经历：{extracurricular}

任务要求：
1. 从课外经历中提取最相关的细分领域（申请者可能感兴趣的研究方向）
2. 找出3个最匹配的细分领域，按匹配度从高到低排序
3. 对每个领域进行深度行业调研，包括：
   - 行业趋势分析（2020年后的最新趋势）
   - 前沿理论引用（具体理论名称、提出者、核心观点）
   - 技术发展趋势
   - 市场痛点识别
   - 技能匹配度分析
4. 详细理由部分必须包含：
   - 至少2个真实的前沿理论或技术趋势引用
   - 具体的行业数据或案例支持
   - 与申请者经历的直接关联分析
5. 参考文献要求真实、权威、前沿：
   - 优先引用：Nature, Science, IEEE, ACM等顶级期刊2020年后的论文
   - 行业报告：Gartner, IDC, McKinsey等权威机构报告
   - 学术会议：最新学术会议论文
   - 专业网站：WHO（世界卫生组织）、UNESCO（联合国教科文组织）、World Bank（世界银行）、IMF（国际货币基金组织）等国际组织官方网站

输出格式（严格遵循，不使用任何Markdown符号）：
【细分领域1: [领域名称]】
匹配度: [XX]%

一句话总结: [我通过硕士学习什么知识来应对什么行业趋势/痛点]

详细理由:
趋势分析: [具体趋势描述，包含前沿理论引用]
痛点识别: [具体痛点分析，包含真实案例]
机会点: [具体机会说明，包含技术发展趋势]
技能匹配: [与申请者经历的相关性分析]

参考文献:
1. [作者] ([年份]). "[标题]", [期刊/机构], DOI/链接
2. [作者] ([年份]). "[标题]", [期刊/机构], DOI/链接

【细分领域2: ...】
（同样格式）

注意：只输出纯文本，不要使用Markdown符号。确保所有参考文献真实存在。
"""

# 个人陈述提示词
PERSONAL_STATEMENT_PROMPT = """
你是一个专业的留学文书顾问，需要基于用户选择的细分领域生成完整的个人陈述。

申请者信息：
- 目标学校：{school}
- 申请专业：{major}
- 相关课程：{courses}
- 课外经历：{extracurricular}
- 选择的细分领域：{selected_domain}

个人陈述要求（严格按照以下5段结构，每段为自然的中文段落，不使用任何列表符号、Markdown格式或分段标题）：

第一段：申请动机
开头一句话精准概括想通过硕士学位探索的细分领域或想解决的行业痛点，展开较为具体的叙述和理由（为什么对这个领域感兴趣），联系期待通过所申请的专业掌握什么技能来应对这样的挑战。

第二段：学习经历
基于提供的课程信息，识别与申请专业最相关的课程，阐述这些课程的教授内容，包括关键概念和方法学，强调课程之间的联系（如XX是XX的基础，或课程间有交集关联），富有逻辑性，避免平铺直叙。

第三段：课外经历
开头与学习经历进行自然衔接，将最相关的课外经历（用户输入的）结合起来。每个经历的撰写逻辑：背景是什么，我负责了什么工作，承担什么职责，我的感悟和体会（课堂外学到的技能、认识到的行业痛点、想解决的问题）。经历之间要有递进关系（时间递进或行业感悟由浅到深），结尾精简总结强调就读硕士想学习的知识技能。

第四段：选校理由
说明目标学校的课程在硕士级别教授的关键概念或方法学，阐述这些课程对申请者有什么帮助，把描述组合成自然的中文段落，强调课程之间的联系，融入前面提到的想法和动机，语气朴素专业，避免夸张。

第五段：职业规划
毕业后的职业规划（毕业硕士应届生可达成的），想去的公司类型，想做的职位，想探索的工作内容，与硕士学习内容的关联性。

请直接输出5个段落，段落之间用两个换行符分隔。不要添加任何解释、说明、标题或格式符号。
"""
```

### 5. 主API端点 (app/api/ps_write.py)
```python
from fastapi import APIRouter, HTTPException
from typing import List
import json

from app.models.schemas import (
    PSWriteRequest, PSGenerationRequest,
    PersonalStatement, ResearchOption
)
from app.services.gemini import GeminiService
from app.services.selection import SelectionService

router = APIRouter(prefix="/api/ps-write", tags=["ps-write"])
selection_service = SelectionService()

@router.post("/generate-with-selection")
async def generate_research_options(request: PSWriteRequest):
    """生成调研选项供用户选择"""
    try:
        # 初始化Gemini服务
        gemini = GeminiService(request.api_key)

        # 构建提示词
        prompt = ENHANCED_RESEARCH_PROMPT.format(
            school=request.school,
            major=request.major,
            courses=request.courses,
            extracurricular=request.extracurricular
        )

        # 生成调研结果
        research_text = await gemini.generate_enhanced_research(prompt)

        # 解析调研结果（需要实现解析函数）
        research_options = parse_research_options(research_text)

        # 创建会话
        session_id = selection_service.create_session(research_options)

        return {
            "session_id": session_id,
            "research_options": research_options,
            "message": "请从以上3个选项中选择一个作为文书写作方向"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-ps")
async def generate_personal_statement(request: PSGenerationRequest):
    """基于用户选择生成个人陈述"""
    try:
        # 验证选择索引
        if not (0 <= request.selection.selection_index < 3):
            raise HTTPException(status_code=400, detail="选择索引必须在0-2范围内")

        # 获取选择的选项
        selected_option = request.selection.research_options[request.selection.selection_index]

        # 初始化Gemini服务
        gemini = GeminiService(request.api_key)

        # 构建个人陈述提示词
        prompt = PERSONAL_STATEMENT_PROMPT.format(
            school=request.school,
            major=request.major,
            courses=request.courses,
            extracurricular=request.extracurricular,
            selected_domain=selected_option.title
        )

        # 生成个人陈述
        ps_text = await gemini.generate_personal_statement(prompt)

        # 解析段落（需要实现解析函数）
        paragraphs = parse_personal_statement(ps_text)

        return PersonalStatement(
            paragraphs=paragraphs,
            selected_domain=selected_option.title,
            generated_at=datetime.now().isoformat()
        )

    except IndexError:
        raise HTTPException(status_code=400, detail="选择索引超出范围")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 辅助函数
def parse_research_options(text: str) -> List[ResearchOption]:
    """解析调研文本为结构化数据"""
    # 实现解析逻辑
    pass

def parse_personal_statement(text: str) -> List[str]:
    """解析个人陈述文本为段落列表"""
    # 按两个换行符分割
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return paragraphs[:5]  # 确保只有5个段落
```

## 部署配置

### 1. Render部署配置 (render.yaml)
```yaml
services:
  - type: web
    name: mutao-assistant-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
      - key: GEMINI_API_KEY
        sync: false
      - key: DEBUG
        value: false
      - key: SESSION_TTL_MINUTES
        value: 30
```

### 2. 依赖文件 (requirements.txt)
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
google-generativeai==0.3.2
pydantic==2.5.0
python-dotenv==1.0.0
pydantic-settings==2.1.0
```

### 3. FastAPI主应用 (app/main.py)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api import ps_write

app = FastAPI(
    title="Mutao Assistant API",
    description="PS写作工具后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(ps_write.router)

@app.get("/")
async def root():
    return {"message": "Mutao Assistant API 运行中"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

## 前端对接指南

### 1. 基本交互流程
```javascript
// 1. 生成调研选项
async function generateResearchOptions(data) {
  const response = await fetch('/api/ps-write/generate-with-selection', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  return await response.json();
}

// 2. 用户选择后生成个人陈述
async function generatePersonalStatement(selectionData) {
  const response = await fetch('/api/ps-write/generate-ps', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(selectionData)
  });
  return await response.json();
}
```

### 2. 前端状态管理
```javascript
// 示例状态管理
class PSWriterState {
  constructor() {
    this.sessionId = null;
    this.researchOptions = [];
    this.selectedIndex = null;
    this.personalStatement = null;
  }

  // 处理用户选择
  async selectOption(index) {
    this.selectedIndex = index;

    // 调用API生成个人陈述
    const requestData = {
      selection: {
        selection_index: index,
        research_options: this.researchOptions
      },
      // ... 其他必要数据
    };

    const result = await generatePersonalStatement(requestData);
    this.personalStatement = result.paragraphs;

    // 清空调研结果显示区域
    this.clearResearchDisplay();

    return result;
  }

  clearResearchDisplay() {
    // 清空前端调研结果显示
  }
}
```

## 测试策略

### 1. 单元测试
```python
# test_gemini_service.py
import pytest
from app.services.gemini import GeminiService

def test_gemini_service_initialization():
    """测试Gemini服务初始化"""
    service = GeminiService("test_api_key")
    assert service.model is not None
```

### 2. 集成测试
```python
# test_api_endpoints.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """测试健康检查端点"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### 3. 端到端测试
```python
# test_full_workflow.py
def test_complete_ps_generation_workflow():
    """测试完整的PS生成工作流"""
    # 1. 生成调研选项
    # 2. 模拟用户选择
    # 3. 生成个人陈述
    # 4. 验证输出格式
```

## 故障排除

### 常见问题及解决方案
1. **Gemini API调用失败**
   - 检查API密钥是否正确
   - 验证代理配置（本地开发）
   - 检查网络连接

2. **会话过期**
   - 默认30分钟过期，重新生成调研选项
   - 延长SESSION_TTL_MINUTES配置

3. **输出格式错误**
   - 检查提示词模板格式
   - 验证解析函数逻辑

4. **性能问题**
   - 添加缓存机制
   - 优化提示词长度
   - 考虑异步处理

## 性能优化建议

### 1. 缓存策略
```python
# 添加Redis缓存（生产环境）
import redis
import json

class RedisCache:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    def cache_research_result(self, key: str, data: dict, ttl: int = 3600):
        """缓存调研结果"""
        self.redis.setex(key, ttl, json.dumps(data))

    def get_cached_result(self, key: str) -> Optional[dict]:
        """获取缓存结果"""
        cached = self.redis.get(key)
        return json.loads(cached) if cached else None
```

### 2. 异步处理
- 使用FastAPI的异步支持
- 避免阻塞操作
- 合理使用背景任务

### 3. 监控和日志
```python
import logging

# 配置结构化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 关键操作添加日志
logger.info("开始生成调研选项", extra={
    "school": request.school,
    "major": request.major
})
```

## 安全注意事项

### 1. API密钥安全
- 用户提供自己的Gemini API密钥
- 不在日志中记录完整API密钥
- 实现密钥验证机制

### 2. 输入验证
- 验证所有用户输入
- 防止注入攻击
- 限制输入长度

### 3. 会话安全
- 使用安全的会话ID生成
- 实现会话过期机制
- 防止会话劫持

## 扩展计划

### 短期扩展（1-2个月）
1. **开发独立文书模块**：基于相似的架构模式，独立开发PS修改、推荐信（RL）写作、简历（CV）写作等独立模块
2. **多语言支持**：添加英文个人陈述生成
3. **模板系统**：支持不同学校/专业的定制模板
4. **历史记录**：用户查询历史管理和导出

### 中期扩展（3-6个月）
1. **多模型支持**：集成Claude、GPT等其他AI模型
2. **文档解析**：自动解析成绩单、CV等PDF文档
3. **智能推荐**：基于历史数据的个性化推荐

### 长期扩展（6个月以上）
1. **协作功能**：多用户协作编辑和评论
2. **评估系统**：AI驱动的文书质量评估
3. **市场集成**：与留学服务平台集成

---

## 快速开始清单

### 第1步：环境准备
- [ ] 安装Python 3.9+
- [ ] 获取Google Gemini API密钥
- [ ] 配置本地代理（如果需要）

### 第2步：项目初始化
```bash
# 克隆或创建项目
mkdir mutao-assistant && cd mutao-assistant

# 创建后端目录
mkdir backend && cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入API密钥
```

### 第3步：本地开发测试
```bash
# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 测试API
curl http://localhost:8001/api/health
```

### 第4步：部署到Render
1. 将代码推送到GitHub仓库
2. 在Render创建新的Web Service
3. 连接GitHub仓库
4. 配置环境变量
5. 部署应用

### 第5步：前端集成
1. 配置前端API请求地址
2. 实现调研结果显示组件
3. 实现用户选择交互
4. 实现个人陈述显示组件
