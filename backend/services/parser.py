"""PDF 解析服务模块

使用 PyMuPDF 解析简历 PDF 文件，提取文本内容和页数信息。
"""
import fitz
from typing import Tuple


async def parse_pdf(file_path: str) -> Tuple[str, int]:
    """解析 PDF 文件，提取文本内容和页数

    Args:
        file_path: PDF 文件路径

    Returns:
        (提取的原始文本, 总页数)

    Raises:
        ValueError: 文件读取失败或内容为空
    """
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise ValueError(f"无法打开 PDF 文件: {e}")

    if doc.page_count == 0:
        doc.close()
        raise ValueError("PDF 文件为空")

    pages_text = []
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text()
        if text:
            pages_text.append(text)

    doc.close()

    if not pages_text:
        raise ValueError("未能从 PDF 中提取到任何文本内容")

    raw_text = "\n\n".join(pages_text)
    return raw_text, doc.page_count
