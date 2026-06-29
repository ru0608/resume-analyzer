"""简历上传与解析路由

提供简历 PDF 上传、解析和关键信息提取接口。
"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import ResumeUploadResponse, ExtractedInfo
from services.parser import parse_pdf
from services.extractor import extract_info
from services.cache import cache_service
from utils.text_cleaner import clean_text
from config import settings

router = APIRouter(prefix="/api/resume", tags=["简历管理"])


@router.post("/upload", response_model=dict)
async def upload_resume(file: UploadFile = File(...)):
    """上传简历 PDF 文件并解析

    - 接收 PDF 文件上传
    - 解析 PDF 提取文本内容
    - 清洗和结构化文本
    - 使用 AI 提取关键信息

    Args:
        file: PDF 格式的简历文件

    Returns:
        包含解析结果和提取信息的 JSON
    """
    # 验证文件类型
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="仅支持 PDF 格式文件",
        )

    # 验证文件大小
    content = await file.read()
    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制（最大 {settings.max_file_size // 1024 // 1024}MB）",
        )

    # 生成唯一 ID
    resume_id = str(uuid.uuid4())

    # 保存文件
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, f"{resume_id}.pdf")
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {e}")

    # 解析 PDF
    try:
        raw_text, pages = await parse_pdf(file_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 清洗文本
    cleaned = clean_text(raw_text)

    # AI 提取信息
    extracted_info = await extract_info(cleaned)

    # 构建解析结果
    parse_result = ResumeUploadResponse(
        resume_id=resume_id,
        filename=file.filename,
        raw_text=raw_text,
        cleaned_text=cleaned,
        pages=pages,
    )

    # 写入缓存
    await cache_service.set("parse", resume_id, parse_result.model_dump())
    await cache_service.set("extract", resume_id, extracted_info.model_dump())

    # 清理上传的临时文件
    try:
        os.remove(file_path)
    except OSError:
        pass

    return {
        "resume_id": resume_id,
        "filename": file.filename,
        "pages": pages,
        "extracted_info": extracted_info.model_dump(exclude_none=True),
    }


@router.get("/{resume_id}", response_model=dict)
async def get_resume_info(resume_id: str):
    """获取已解析的简历信息

    Args:
        resume_id: 简历 ID

    Returns:
        简历解析结果和提取信息
    """
    # 尝试从缓存获取
    cached_parse = await cache_service.get("parse", resume_id)
    cached_extract = await cache_service.get("extract", resume_id)

    if not cached_parse:
        raise HTTPException(status_code=404, detail="简历不存在或已过期")

    return {
        "parse_result": cached_parse,
        "extracted_info": cached_extract,
    }
