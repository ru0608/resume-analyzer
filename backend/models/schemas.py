"""数据模型 - Pydantic schemas

定义请求和响应的数据结构。
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List


class ResumeUploadResponse(BaseModel):
    """简历上传与解析结果"""
    resume_id: str = Field(..., description="简历唯一标识")
    filename: str = Field(..., description="原始文件名")
    raw_text: str = Field(..., description="提取的原始文本")
    cleaned_text: str = Field(..., description="清洗后的文本")
    pages: int = Field(0, description="PDF 页数")


class BasicInfo(BaseModel):
    """基本信息"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class JobIntention(BaseModel):
    """求职信息（加分项）"""
    job_intention: Optional[str] = None
    expected_salary: Optional[str] = None


class BackgroundInfo(BaseModel):
    """背景信息（加分项）"""
    work_years: Optional[str] = None
    education: Optional[str] = None
    project_experience: Optional[list[str]] = None


class ExtractedInfo(BaseModel):
    """AI 提取的关键信息"""
    basic_info: BasicInfo = Field(default_factory=BasicInfo)
    job_intention: Optional[JobIntention] = None
    background_info: Optional[BackgroundInfo] = None


class MatchRequest(BaseModel):
    """岗位匹配请求"""
    resume_id: str = Field(..., description="简历 ID")
    job_description: str = Field(..., description="岗位需求描述", min_length=1)


class MatchDimension(BaseModel):
    """匹配维度评分"""
    skill_match: float = Field(..., ge=0, le=100, description="技能匹配率")
    experience_relevance: float = Field(..., ge=0, le=100, description="经验相关性")
    keyword_match: float = Field(..., ge=0, le=100, description="关键词匹配率")
    ai_score: Optional[float] = Field(None, ge=0, le=100, description="AI 综合评分")


class MatchResponse(BaseModel):
    """岗位匹配结果"""
    resume_id: str
    job_description_summary: str = ""
    extracted_info: ExtractedInfo
    dimensions: MatchDimension
    overall_score: float = Field(..., ge=0, le=100, description="综合评分")
    analysis_summary: str = ""


class ResumeParseResponse(BaseModel):
    """完整简历解析与匹配结果"""
    parse_result: ResumeUploadResponse
    extracted_info: ExtractedInfo
    match_result: Optional[MatchResponse] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    error_code: str
    message: str
    detail: Optional[str] = None
