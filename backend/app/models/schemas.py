from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ResearchOption(BaseModel):
    """调研选项数据模型"""
    title: str = Field(..., description="细分领域名称")
    match_score: int = Field(..., ge=70, le=100, description="匹配度评分 (70-100)")
    summary: str = Field(..., description="一句话总结")
    reasoning: List[str] = Field(..., description="详细理由列表")
    references: List[str] = Field(..., description="参考文献列表")

class UserSelection(BaseModel):
    """用户选择数据模型"""
    selection_index: int = Field(..., ge=0, le=2, description="选择索引 (0, 1, 2)")
    research_options: List[ResearchOption] = Field(..., description="完整的调研选项列表")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")

class PSWriteRequest(BaseModel):
    """PS生成请求"""
    school: str = Field(..., description="目标学校")
    major: str = Field(..., description="申请专业")
    courses: str = Field(..., description="相关课程描述")
    extracurricular: str = Field(..., description="课外经历描述")
    api_key: str = Field(..., description="用户提供的Gemini API密钥")
    model_name: Optional[str] = Field(None, description="模型名称")
    temperature: Optional[float] = Field(None, description="温度参数")
    max_output_tokens: Optional[int] = Field(None, description="最大输出token数")

class PSGenerationRequest(BaseModel):
    """个人陈述生成请求"""
    selection: UserSelection = Field(..., description="用户选择")
    school: str = Field(..., description="目标学校")
    major: str = Field(..., description="申请专业")
    courses: str = Field(..., description="相关课程描述")
    extracurricular: str = Field(..., description="课外经历描述")
    api_key: str = Field(..., description="用户提供的Gemini API密钥")

class PersonalStatement(BaseModel):
    """个人陈述响应"""
    paragraphs: List[str] = Field(..., description="5个段落")
    selected_domain: str = Field(..., description="选择的细分领域")
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="生成时间戳")

class ResearchOptionsResponse(BaseModel):
    """调研选项响应"""
    session_id: str = Field(..., description="唯一会话ID")
    research_options: List[ResearchOption] = Field(..., description="调研选项列表")
    message: str = Field(default="请从以上3个选项中选择一个作为文书写作方向", description="提示消息")

class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str = Field(..., description="错误详情")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")