#!/usr/bin/env python3
"""PDF 空白页检测脚本（无外部依赖版）。

Usage:
    python pdf-blank-check.py output.pdf

检测逻辑：
  1. 读取 PDF 二进制，按 /Page 对象计算总页数
  2. 检测每个 stream 的文本内容量
  3. 页面 stream 过小 → 疑似空白页

退出码：
  0 = 无空白页
  1 = 发现空白页（需要修复后再发）

注意：这是轻量检测，不依赖 pdftotext/poppler。
如果系统有 pdftotext 会优先使用（更准确）。
"""

import os
import re
import shutil
import subprocess
import sys


def check_with_pdftotext(pdf_path: str) -> list[int]:
    """用 pdftotext 检测（更准确）。"""
    result = subprocess.run(
        ["pdftotext", pdf_path, "-", "-layout"],
        capture_output=True, text=True
    )
    pages = result.stdout.split("\f")
    blank_pages = []
    for i, page_text in enumerate(pages, 1):
        stripped = page_text.strip()
        if len(stripped.replace(" ", "").replace("\n", "")) < 10:
            blank_pages.append(i)
    return blank_pages, len(pages)


def check_with_pypdf(pdf_path: str) -> list[int]:
    """用 pypdf 检测（Python 纯库）。"""
    try:
        from pypdf import PdfReader
    except ImportError:
        return None, None

    reader = PdfReader(pdf_path)
    blank_pages = []
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        if len(text.strip().replace(" ", "").replace("\n", "")) < 10:
            blank_pages.append(i)
    return blank_pages, len(reader.pages)


def check_basic(pdf_path: str) -> tuple[list[int], int]:
    """基础二进制检测（最后手段）：只报告总页数和文件大小。"""
    with open(pdf_path, "rb") as f:
        data = f.read()
    # 粗略统计页数
    page_count = len(re.findall(rb"/Type\s*/Page[^s]", data))
    size_kb = os.path.getsize(pdf_path) / 1024
    # 无法精确检测空白页，只做基础判断
    # 如果平均每页 < 1KB，可能有空白页
    avg_per_page = size_kb / max(page_count, 1)
    suspect = []
    if avg_per_page < 1:
        suspect = [-1]  # 标记为可疑但无法定位
    return suspect, page_count


def main(pdf_path: str):
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        sys.exit(2)

    size_kb = os.path.getsize(pdf_path) / 1024

    # 优先级：pdftotext > pypdf > basic
    blanks, total = None, None

    if shutil.which("pdftotext"):
        blanks, total = check_with_pdftotext(pdf_path)
        method = "pdftotext"
    else:
        blanks, total = check_with_pypdf(pdf_path)
        method = "pypdf"

    if blanks is None:
        blanks, total = check_basic(pdf_path)
        method = "basic"

    if blanks and blanks != [-1]:
        print(f"❌ 发现 {len(blanks)} 个空白页: {blanks}")
        print(f"   总页数: {total} | 大小: {size_kb:.0f} KB | 检测方式: {method}")
        print(f"   修复: 找到空白页前的大容器，去掉 break-inside:avoid 或拆小")
        sys.exit(1)
    elif blanks == [-1]:
        print(f"⚠️  文件可能有空白页（平均每页内容过少）")
        print(f"   总页数: {total} | 大小: {size_kb:.0f} KB | 检测方式: {method}")
        print(f"   建议: 用 vision 工具目视检查")
        sys.exit(1)
    else:
        print(f"✅ 无空白页 (共 {total} 页, {size_kb:.0f} KB, 检测方式: {method})")
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf-blank-check.py output.pdf")
        sys.exit(1)
    main(sys.argv[1])
