"""文本清洗工具模块

对 PDF 提取的原始文本进行清洗和结构化处理。
"""
import re
from typing import List


def clean_text(text: str) -> str:
    """清洗提取的文本：去除冗余字符、规范化空白

    Args:
        text: 原始提取文本

    Returns:
        清洗后的文本
    """
    if not text:
        return ""

    # 替换零宽字符和不可见控制字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f​-‏ - ﻿]', '', text)

    # 规范化换行：多个换行符合并为两个
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 去除每行首尾空白
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # 合并被换行截断的短行（如行尾无标点且下一行长度 > 30，属于自然换行）
    # 保留简历中单行字段之间的换行，避免把整份简历合并成一段
    text = re.sub(r'(?<![。！？；：、，)\n])\n(?=[a-zA-Z0-9\(（\-])', '', text)

    # 规范化空格：多个空格合并为一个
    text = re.sub(r'[ \t]+', ' ', text)

    # 去除孤立的特殊字符（但不是中文、英文、数字、常用标点）
    text = re.sub(r'(?<![a-zA-Z一-鿿0-9])[#*•·→⇒⇨◆◇◉◎●○□■☆★▷▶▼▼▲△♯♮♭†‡§¶‖′″‼‽⁇⁈⁉]', '', text)

    return text.strip()


def segment_text(text: str) -> List[str]:
    """将清洗后的文本按段落分割

    Args:
        text: 清洗后的文本

    Returns:
        段落列表
    """
    paragraphs = re.split(r'\n\n+', text)
    return [p.strip() for p in paragraphs if p.strip()]


def extract_sections(text: str) -> dict:
    """尝试将文本按常见简历章节分类

    Args:
        text: 清洗后的文本

    Returns:
        章节字典: {section_name: content}
    """
    sections = {}
    # 常见的简历章节标题
    section_patterns = [
        (r'(?:个人信息|基本信息|个人资料)', 'basic_info'),
        (r'(?:教育背景|教育经历|学历)', 'education'),
        (r'(?:工作经历|工作经验|工作背景|职业经历)', 'experience'),
        (r'(?:项目经历|项目经验|项目)', 'project'),
        (r'(?:专业技能|技能|技术栈|技术能力)', 'skills'),
        (r'(?:自我评价|自我描述|关于我)', 'self_eval'),
        (r'(?:求职意向|期望职位|目标岗位)', 'job_intention'),
    ]

    lines = text.split('\n')
    current_section = 'header'
    header_lines = []

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        matched = False
        for pattern, section_name in section_patterns:
            if re.search(pattern, line_stripped):
                if current_section != 'header' and current_section not in sections:
                    sections[current_section] = []
                current_section = section_name
                matched = True
                break

        if not matched:
            if current_section == 'header':
                header_lines.append(line_stripped)
            else:
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append(line_stripped)

    if header_lines:
        sections['header'] = '\n'.join(header_lines)

    # 将列表合并为文本
    result = {}
    for k, v in sections.items():
        if isinstance(v, list):
            result[k] = '\n'.join(v)
        else:
            result[k] = v

    return result
