"""AI 评分与匹配服务模块

对简历与岗位需求进行多维度匹配评分，支持 AI 精准评分。
"""
import json
import re
from typing import List, Tuple
from models.schemas import ExtractedInfo, MatchDimension
from config import settings


_SCORER_SYSTEM_PROMPT = "你是一个专业的简历匹配评分助手。请对简历与岗位需求进行多维度匹配度评分，严格按指定 JSON 格式返回评分结果。"


def _build_scoring_prompt(
    cleaned_text: str,
    extracted_info: ExtractedInfo,
    job_description: str,
) -> str:
    """构建评分 prompt"""
    info_json = extracted_info.model_dump_json(indent=2, exclude_none=True)

    return f"""你是一个专业的招聘匹配分析专家。请根据岗位需求对候选人简历进行评分。

岗位需求描述：
{job_description}

候选人简历信息（已结构化提取）：
{info_json}

候选人简历全文：
{cleaned_text}

请从以下维度进行评分（0-100分），并以严格 JSON 格式返回（不要包含 markdown 代码块标记）：

{{
    "skill_match": "技能匹配度评分（考察技术栈、工具、专业技能的匹配程度）",
    "experience_relevance": "工作经验相关性评分（考察行业经验、岗位职责匹配度）",
    "keyword_match": "关键词匹配率评分（岗位需求中的关键词在简历中出现的比例）",
    "ai_score": "AI 综合智能评分（综合考量以上维度以及候选人的项目质量、学历背景等，给出一个全面评估）",
    "analysis_summary": "对匹配结果的文字分析总结（200字以内）",
    "job_summary": "从简历中提炼的岗位相关经历摘要（100字以内）"
}}

评分标准：
- 90-100：完美匹配
- 70-89：良好匹配
- 50-69：部分匹配
- 30-49：较弱匹配
- 0-29：不匹配

返回纯 JSON 对象，不要包含任何额外格式标记。所有分数为整数即可。"""


def _keyword_match_score(
    job_description: str,
    cleaned_text: str,
) -> float:
    """基于关键词的匹配率计算（非 AI 后备方案）

    Args:
        job_description: 岗位需求描述
        cleaned_text: 简历文本

    Returns:
        关键词匹配率 (0-100)
    """
    # 提取关键词（中文分词简单处理：按标点拆分后取长度 > 1 的词）
    stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
                  "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
                  "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "与", "及",
                  "或", "并", "对", "为", "等", "从", "被", "把", "让", "向", "往"}

    # 提取岗位需求中的关键词
    job_words = set()
    for token in re.split(r'[\s,，。；;、:：()（）【】\[\]{}""''\n\t]+', job_description):
        token = token.strip()
        if len(token) >= 2 and token not in stop_words:
            job_words.add(token)

    if not job_words:
        return 50.0  # 无关键词时返回中等分

    # 统计匹配数
    matched = sum(1 for word in job_words if word in cleaned_text)
    return round((matched / len(job_words)) * 100, 1)


async def calculate_match(
    cleaned_text: str,
    extracted_info: ExtractedInfo,
    job_description: str,
) -> Tuple[MatchDimension, str, str]:
    """计算简历与岗位需求的匹配度

    Args:
        cleaned_text: 清洗后的简历文本
        extracted_info: 简历提取信息
        job_description: 岗位需求描述

    Returns:
        (MatchDimension, analysis_summary, job_summary)
    """
    # 1. 计算基础关键词匹配率
    base_keyword_score = _keyword_match_score(job_description, cleaned_text)

    # 2. 计算基础技能匹配率（基于提取的技能信息）
    skill_text = ""
    if extracted_info.background_info and extracted_info.background_info.project_experience:
        skill_text = " ".join(extracted_info.background_info.project_experience)
    base_skill_score = _keyword_match_score(job_description,
                                             cleaned_text + " " + skill_text)

    # 3. 尝试使用 AI 进行精准评分
    if settings.dashscope_api_key:
        try:
            import dashscope
            dashscope.api_key = settings.dashscope_api_key

            messages = [
                {"role": "system", "content": _SCORER_SYSTEM_PROMPT},
                {"role": "user", "content": _build_scoring_prompt(
                    cleaned_text, extracted_info, job_description
                )},
            ]

            response = dashscope.Generation.call(
                model=settings.dashscope_model,
                messages=messages,
                result_format="message",
                temperature=0.2,
            )

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                return _parse_scoring_response(content, base_keyword_score, base_skill_score)

        except Exception as e:
            print(f"[AI 评分异常] {e}，使用规则评分")

    # 4. 后备：基于规则的评分
    # 工作经验相关性：基于工作年限关键词
    exp_score = _estimate_experience_score(cleaned_text, job_description)

    dimension = MatchDimension(
        skill_match=min(base_skill_score * 1.1, 100),
        experience_relevance=exp_score,
        keyword_match=base_keyword_score,
    )

    overall = round(
        settings.weight_skill_match * dimension.skill_match
        + settings.weight_experience * dimension.experience_relevance
        + settings.weight_education * _estimate_education_score(cleaned_text)
        + settings.weight_keyword * dimension.keyword_match,
        1,
    )

    return dimension, f"AI 评分暂不可用，基于规则计算的综合评分为 {overall} 分。", "需 AI 评分补充"


def _parse_scoring_response(
    content: str,
    base_keyword_score: float,
    base_skill_score: float,
) -> Tuple[MatchDimension, str, str]:
    """解析 AI 评分响应"""
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
        content = content.rsplit("```", 1)[0]
    content = content.strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            try:
                data = json.loads(content[start:end + 1])
            except json.JSONDecodeError:
                data = {}

    if not data:
        return MatchDimension(
            skill_match=min(base_skill_score * 1.1, 100),
            experience_relevance=60.0,
            keyword_match=base_keyword_score,
        ), "评分解析失败，使用规则评分", ""

    dimension = MatchDimension(
        skill_match=min(float(data.get("skill_match", base_skill_score)), 100),
        experience_relevance=min(float(data.get("experience_relevance", 60)), 100),
        keyword_match=min(float(data.get("keyword_match", base_keyword_score)), 100),
        ai_score=min(float(data["ai_score"]), 100) if data.get("ai_score") is not None else None,
    )

    analysis = data.get("analysis_summary", "")
    job_summary = data.get("job_summary", "")

    return dimension, analysis, job_summary


def _estimate_experience_score(cleaned_text: str, job_description: str) -> float:
    """估算工作经验相关性"""
    # 简单规则：检查工作年限提及
    year_pattern = r'(\d+)[\+\-]?\s*年'
    text_years = re.findall(year_pattern, cleaned_text)
    job_years = re.findall(year_pattern, job_description)

    if text_years and job_years:
        text_max = max(int(y) for y in text_years)
        job_max = max(int(y) for y in job_years)
        if text_max >= job_max:
            return 80.0
        else:
            return max(40.0, (text_max / job_max) * 80)

    return 60.0


def _estimate_education_score(cleaned_text: str) -> float:
    """估算学历分数"""
    edu_levels = [
        (r'(?:博士|PhD)', 100),
        (r'(?:硕士|研究生|Master)', 85),
        (r'(?:本科|学士|Bachelor)', 70),
        (r'(?:大专|专科|Associate)', 50),
        (r'(?:高中|中专)', 30),
    ]
    for pattern, score in edu_levels:
        if re.search(pattern, cleaned_text):
            return score
    return 40.0
