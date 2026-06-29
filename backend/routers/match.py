"""简历评分与匹配路由

提供简历与岗位需求的匹配度评分接口。
"""
from fastapi import APIRouter, HTTPException
from models.schemas import MatchRequest, MatchResponse, ExtractedInfo
from services.scorer import calculate_match
from services.cache import cache_service

router = APIRouter(prefix="/api/match", tags=["简历匹配"])


@router.post("/score", response_model=dict)
async def match_resume(request: MatchRequest):
    """将简历与岗位需求进行匹配评分

    - 接收岗位需求描述文本
    - 对岗位需求进行关键词提取和分析
    - 将简历信息与岗位需求进行多维匹配
    - 返回匹配度评分和 AI 分析

    Args:
        request: 包含简历 ID 和岗位需求描述的请求体

    Returns:
        匹配度评分结果
    """
    # 1. 获取缓存的简历信息
    cached_extract = await cache_service.get("extract", request.resume_id)
    if not cached_extract:
        raise HTTPException(
            status_code=404,
            detail="简历不存在或已过期，请重新上传",
        )

    # 2. 检查是否已有缓存匹配结果
    cache_key = f"{request.resume_id}:{hash(request.job_description)}"
    cached_result = await cache_service.get("match", cache_key)
    if cached_result:
        return cached_result

    # 3. 获取简历文本
    cached_parse = await cache_service.get("parse", request.resume_id)
    cleaned_text = cached_parse.get("cleaned_text", "") if cached_parse else ""

    # 4. 构建 ExtractedInfo
    extracted_info = ExtractedInfo.model_validate(cached_extract)

    # 5. 计算匹配度
    dimension, analysis, job_summary = await calculate_match(
        cleaned_text=cleaned_text,
        extracted_info=extracted_info,
        job_description=request.job_description,
    )

    # 6. 计算综合评分
    if dimension.ai_score is not None:
        overall_score = round(
            0.3 * dimension.skill_match
            + 0.2 * dimension.experience_relevance
            + 0.15 * dimension.keyword_match
            + 0.35 * dimension.ai_score,
            1,
        )
    else:
        from config import settings as cfg
        overall_score = round(
            cfg.weight_skill_match * dimension.skill_match
            + cfg.weight_experience * dimension.experience_relevance
            + cfg.weight_education * 60  # 默认学历分
            + cfg.weight_keyword * dimension.keyword_match,
            1,
        )

    # 7. 构建响应
    result = {
        "resume_id": request.resume_id,
        "job_description_summary": job_summary or request.job_description[:200],
        "extracted_info": extracted_info.model_dump(exclude_none=True),
        "dimensions": dimension.model_dump(),
        "overall_score": overall_score,
        "analysis_summary": analysis,
    }

    # 8. 缓存匹配结果
    await cache_service.set("match", cache_key, result)

    return result
