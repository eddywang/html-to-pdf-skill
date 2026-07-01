---
name: html-to-pdf
description: HTML → PDF via WeasyPrint：矢量输出、CJK 支持、分页优化。面向 AI Agent 管线的轻量转换技能。
---

# HTML to PDF (WeasyPrint)

将 HTML 文件转换为高质量矢量 PDF，支持复杂布局、CJK 字体、分页控制。

## When to Use

- 用户要求将 HTML 转为 PDF
- 生成报告/简历/文档的 PDF 版本
- 批量转换 HTML 文档

## 转换命令

```bash
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
python scripts/html_to_pdf_weasyprint.py input.html output.pdf
```

## 特点

- 矢量 PDF，文字可选可搜索
- CSS Paged Media 分页控制（`@page`、`break-inside`、`break-after`）
- CJK 字体原生支持
- 体积小（通常 100-300 KB）
- 无 Chromium 依赖

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

/* 避免标题孤悬页尾 */
h2, h3 {
  break-after: avoid;
  page-break-after: avoid;
}

/* 内容块尽量不拆分 */
.timeline-item, .card, .callout, .info-card, .note-box {
  break-inside: avoid;
  page-break-inside: avoid;
}

/* 列表项不拆分 */
footer .sources li {
  break-inside: avoid;
  page-break-inside: avoid;
}
```

## 环境要求

```bash
# uv 快速搭建（推荐）
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install weasyprint

# macOS 动态库路径
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
```

## 验证步骤

生成 PDF 后必须验证：

1. `pdftotext output.pdf - | head -20` — 确认文字可提取
2. 检查无孤立标题、无空白页、无内容截断

## Troubleshooting

| 问题 | 解决 |
|------|------|
| `cannot load library 'libgobject-2.0-0'` | 用 Python 3.11+ venv，设置 `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` |
| 分页时标题孤立 | 加 `break-after: avoid` 到标题元素 |
| 时间线条目被劈开 | 加 `break-inside: avoid` 到条目容器 |
| 渐变背景丢失 | 检查 `linear-gradient` 语法，WeasyPrint 支持标准写法 |
| 中文乱码 | WeasyPrint 自动使用系统 CJK 字体，确认系统有 PingFang/Noto Sans CJK |
