"""AI 关键信息提取服务模块

使用阿里云通义千问 (DashScope) 从简历文本中提取结构化信息。
"""
import json
from typing import Optional
from models.schemas import ExtractedInfo, BasicInfo, JobIntention, BackgroundInfo
from config import settings


def _build_extraction_prompt(cleaned_text: str) -> str:
    """构建信息提取的 system prompt"""
    return f"""你是一个专业的简历信息提取助手。请从以下简历文本中提取关键信息，并以 JSON 格式返回。

请严格按以下 JSON 结构返回（不要包含 markdown 代码块标记，仅返回纯 JSON）：
{{
    "basic_info": {{
        "name": "姓名",
        "phone": "电话",
        "email": "邮箱",
        "address": "地址"
    }},
    "job_intention": {{
        "job_intention": "求职意向",
        "expected_salary": "期望薪资"
    }},
    "background_info": {{
        "work_years": "工作年限",
        "education": "学历背景（最高学历及学校专业）",
        "project_experience": ["项目经历1", "项目经历2"]
    }}
}}

注意：
1. 基本信息的四个字段（name/phone/email/address）必须提取，找不到则填 null
2. job_intention 和 background_info 是加分项，尽量提取
3. 项目经历用数组形式列出每个项目
4. 如果某个字段在简历中找不到，设为 null 即可，不要编造

简历文本：
{cleaned_text}
"""


_EXTRACTION_SYSTEM_PROMPT = "你是一个专业的简历信息提取助手。请从简历文本中提取关键信息，严格按指定 JSON 格式返回，不要编造不存在的信息。"


async def extract_info(cleaned_text: str) -> ExtractedInfo:
    """使用 AI 从清洗后的简历文本中提取关键信息

    Args:
        cleaned_text: 清洗后的简历文本

    Returns:
        提取的结构化信息
    """
    if not settings.dashscope_api_key:
        # 无 API key 时使用正则后备方案提取基本信息
        return _fallback_extract(cleaned_text)

    try:
        import dashscope
        dashscope.api_key = settings.dashscope_api_key

        messages = [
            {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": _build_extraction_prompt(cleaned_text)},
        ]

        response = dashscope.Generation.call(
            model=settings.dashscope_model,
            messages=messages,
            result_format="message",
            temperature=0.1,
        )

        if response.status_code == 200:
            content = response.output.choices[0].message.content
            return _parse_extraction_response(content)
        else:
            print(f"[DashScope API Error] {response.status_code}: {response.message}")
            return _fallback_extract(cleaned_text)

    except ImportError:
        print("dashscope 未安装，使用后备提取方案")
        return _fallback_extract(cleaned_text)
    except Exception as e:
        print(f"[提取异常] {e}")
        return _fallback_extract(cleaned_text)


def _parse_extraction_response(content: str) -> ExtractedInfo:
    """解析 AI 返回的 JSON 内容"""
    # 尝试提取 JSON（去除可能的 markdown 代码块标记）
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
        content = content.rsplit("```", 1)[0]
    content = content.strip()

    # 尝试修复常见的 JSON 格式问题
    content = content.replace("'", '"')

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # 尝试查找 JSON 对象边界
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(content[start:end + 1])
            except json.JSONDecodeError:
                return ExtractedInfo()
        else:
            return ExtractedInfo()

    basic = data.get("basic_info", {}) or {}
    job = data.get("job_intention", {}) or {}
    bg = data.get("background_info", {}) or {}

    return ExtractedInfo(
        basic_info=BasicInfo(
            name=basic.get("name"),
            phone=basic.get("phone"),
            email=basic.get("email"),
            address=basic.get("address"),
        ),
        job_intention=JobIntention(
            job_intention=job.get("job_intention"),
            expected_salary=job.get("expected_salary"),
        ) if any(job.values()) else None,
        background_info=BackgroundInfo(
            work_years=bg.get("work_years"),
            education=bg.get("education"),
            project_experience=bg.get("project_experience"),
        ) if any(bg.values()) else None,
    )


def _fallback_extract(text: str) -> ExtractedInfo:
    """后备方案：使用正则表达式提取基本信息"""
    import re

    name = None
    phone = None
    email = None
    address = None

    # --- 电话 ---
    # 先尝试从字段标签提取：电话: 138-0000-1234
    phone_match = re.search(
        r'(?:电话|手机|联系电话|Tel|Phone)[:：\s]*'
        r'(\+?\d{2,3}[-\s]?)?'
        r'(1[3-9][-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d)',
        text,
    )
    if phone_match:
        raw = phone_match.group(2) or phone_match.group(0).split(":")[-1].strip()
        phone = re.sub(r'[-\s]', '', raw)  # 去除连字符和空格，统一格式
    else:
        # 直接匹配纯数字手机号（11位）
        phone_match2 = re.search(r'1[3-9]\d{9}', text)
        if phone_match2:
            phone = phone_match2.group(0)

    # --- 邮箱 ---
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    if email_match:
        email = email_match.group(0)

    # --- 姓名 ---
    # 找"姓名"标签后的内容，或简历第一行纯中文
    name_from_label = re.search(r'(?:姓名|Name)[:：\s]*([一-鿿]{2,4})', text)
    if name_from_label:
        name = name_from_label.group(1)
    else:
        lines = text.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            # 姓名一般是 2-4 个中文字符
            name_match = re.match(r'^[一-鿿·]{2,6}$', first_line)
            if name_match:
                name = name_match.group(0)

    # --- 地址 ---
    address_match = re.search(r'(?:地址|现居|居住地|Location)[:：\s]*([^\n]+)', text)
    if address_match:
        address = address_match.group(1).strip()

    return ExtractedInfo(
        basic_info=BasicInfo(
            name=name,
            phone=phone,
            email=email,
            address=address,
        )
    )
