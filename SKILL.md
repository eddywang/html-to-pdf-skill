---
name: html-to-pdf
description: HTML → PDF 生成技能：WeasyPrint 主力 + Playwright 后备 + dompdf.js 前端注入。支持分页优化、CJK 字体、渐变背景。面向 AI Agent 管线。
---

# HTML to PDF Converter Skill

将 HTML 文件转换为高质量 PDF，支持复杂布局、CJK 字体、分页控制。

## When to Use

- 用户要求将 HTML 转为 PDF
- 生成报告/简历/文档的 PDF 版本
- 批量转换 HTML 文档
- 需要对比不同 PDF 生成方案

## 可用方法

### 方法 1: WeasyPrint（推荐主力）

最佳适用：标准报告、简历、文档、中文内容

```bash
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
python scripts/html_to_pdf_weasyprint.py input.html output.pdf
```

特点：
- 矢量 PDF，文字可选可搜索
- CSS Paged Media 分页控制好（`@page`、`break-inside`、`break-after`）
- CJK 字体原生支持
- 体积小（通常 100-300 KB）
- 不需要 Chromium

局限：
- 复杂 Flex/Grid 布局偶有偏差
- macOS 需 `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`
- 系统 Python 3.9 的 cffi 可能找不到 glib，建议用 Python 3.11+ venv

### 方法 2: Playwright Headless Print（后备）

最佳适用：复杂 CSS/JS 页面、SPA、需要 100% Chrome 渲染效果

```bash
python scripts/html_to_pdf_playwright.py input.html output.pdf
```

特点：
- Chromium 渲染 = 几乎 100% CSS 还原
- 支持 JS 动态内容
- 自动等待页面加载完成

局限：
- 需要 Chromium（~400MB）
- 输出体积较大（1-5 MB）
- 不支持 `@page` CSS 中的页眉页脚定制

### 方法 3: dompdf.js 注入（轻量矢量）

最佳适用：简单内容、需要极小体积、前端导出场景

```bash
python scripts/html_to_pdf_dompdf.py input.html output.pdf
```

特点：
- 极小体积（50-100 KB）
- 真矢量 PDF，文字可选
- 支持分页和页眉页脚

局限：
- CSS 支持不完整（渐变、阴影可能丢失）
- 仍需 Playwright 做注入宿主
- 不适合复杂排版

## 分页优化 CSS 模板

在 HTML 的 `<style>` 中加入：

```css
@page {
  size: A4;
  margin: 18mm 20mm 22mm 20mm;
}
@page :first {
  margin: 0;
}

h2, h3 {
  break-after: avoid;
  page-break-after: avoid;
}

.timeline-item, .card, .callout, .info-card, .note-box {
  break-inside: avoid;
  page-break-inside: avoid;
}

footer .sources li {
  break-inside: avoid;
  page-break-inside: avoid;
}
```

## 环境依赖

```bash
# uv 快速搭建（推荐）
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install weasyprint playwright pymupdf pillow

# macOS 动态库
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib

# Playwright Chromium（首次）
playwright install chromium
```

## 验证步骤

生成 PDF 后必须验证：

1. `pdftotext output.pdf - | head -20` — 确认文字可提取
2. 用 pymupdf 渲染首页检查排版：
   ```python
   import fitz
   doc = fitz.open('output.pdf')
   page = doc[0]
   pix = page.get_pixmap(dpi=150)
   pix.save('preview.png')
   ```
3. 检查无孤立标题、无空白页、无内容截断

## Troubleshooting

| 问题 | 解决 |
|------|------|
| WeasyPrint: `cannot load library 'libgobject-2.0-0'` | 用 Python 3.11+ venv，设置 `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` |
| Playwright: browser not found | `playwright install chromium` |
| PDF 中文乱码 | WeasyPrint 会自动使用系统 CJK 字体；Playwright 同理 |
| 分页时标题孤立 | 加 `break-after: avoid` 到标题元素 |
| 时间线条目被劈开 | 加 `break-inside: avoid` 到条目容器 |
| 渐变背景丢失 | WeasyPrint 支持 linear-gradient；如仍失败用 Playwright |
