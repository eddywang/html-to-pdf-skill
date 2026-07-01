---
name: html-to-pdf
description: HTML → PDF via WeasyPrint：矢量输出、CJK 支持、分页优化。面向 AI Agent 管线的轻量转换技能。
version: "1.1.0"
status: active
created_at: 2026-07-01
updated_at: 2026-07-01
author: Eddy Wang
license: MIT
metadata:
  hermes:
    category: productivity
    tags: [pdf, html, weasyprint, document, export]
    requires_toolsets: [terminal, file]
---

# HTML to PDF (WeasyPrint)

将 HTML 文件转换为高质量矢量 PDF，支持复杂布局、CJK 字体、分页控制。

## When to Use

- 用户要求生成 PDF（报告/简历/文档/方案）
- 需要将 HTML 转为可打印、可分享的 PDF
- 涉及中文排版的 PDF 输出

## 转换命令

```bash
# Linux (hermes 容器内)
/opt/hermes/.venv/bin/python3 scripts/html_to_pdf_weasyprint.py input.html output.pdf

# macOS
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
python scripts/html_to_pdf_weasyprint.py input.html output.pdf
```

## 特点

- 矢量 PDF，文字可选可搜索
- CSS Paged Media 分页控制（`@page`、`break-inside`、`break-after`）
- CJK 字体原生支持
- 体积小（通常 100-300 KB）
- 无 Chromium 依赖

## 生成流程（必须按顺序）

### Step 1：写 HTML

先写完整 HTML 文件，`<style>` 块中必须包含下方「分页 CSS 模板」的内容。

⛔ **不要凭记忆写 CSS** —— 打开 `references/base-print.css` 逐字粘进 `<style>`。

### Step 2：渲染 PDF

```bash
/opt/hermes/.venv/bin/python3 scripts/html_to_pdf_weasyprint.py input.html output.pdf
```

### Step 3：验证（不可跳过）

```bash
# 1. 文字可提取
pdftotext output.pdf - | head -20

# 2. 检查空白页
python3 scripts/pdf-blank-check.py output.pdf

# 3. 目视检查（如有 vision 工具）
# 确认无孤立标题、无空白页、无内容截断
```

三项全过才能发给用户。

## 分页 CSS 模板

⛔ 每份 HTML 必须包含这段 CSS（也存在 `references/base-print.css`）：

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

/* 内容块尽量不拆分（只用在小块 < 半页 ≈ 130mm） */
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

## ⛔ WeasyPrint 兼容性铁律（违反必出错）

这些是实战踩出来的坑，必须遵守：

| 禁止 | 原因 | 替代方案 |
|------|------|----------|
| `display: flex` | WeasyPrint 支持不完整，居中/列布局会错位 | `display: table` / `display: table-cell` |
| `display: grid` | 同上 | `display: table` + 百分比宽度 |
| `align-items` / `justify-content` | flex 属性，不生效 | `text-align: center` + `margin: 0 auto` |
| 大容器加 `break-inside: avoid` | 超过半页的容器加 avoid 会导致整页空白 | 只给小块（< 130mm）加 avoid |
| `box-shadow` | 会报 WARNING（不影响但有噪音） | 可留，但不要依赖它的视觉效果 |

**多列布局正确写法：**
```css
.row { display: table; width: 100%; border-spacing: 16px 0; }
.col { display: table-cell; width: 50%; vertical-align: top; }
```

**居中正确写法：**
```css
.centered { text-align: center; margin: 0 auto; }
```

**封面垂直居中：** 用 `padding` 撑开，不用 flex/grid。

## 微信发送限制

- 微信文件上限：**实测约 15MB**，超过会超时失败
- 图片多的 PDF 提前算预算：图片数 × 单图大小 + ~300KB 开销
- 超过 15MB → 压缩图片或拆分文档

## 环境说明

### Hermes 容器（Linux）
- WeasyPrint 已预装在 `/opt/hermes/.venv`
- 调用：`/opt/hermes/.venv/bin/python3 scripts/html_to_pdf_weasyprint.py`
- 中文字体：`/usr/share/fonts/opentype/noto/NotoSansCJK-*.ttc`（已安装）
- 包管理用 `uv`（路径 `/usr/local/bin/uv`），系统 python3 无 pip
- 中文书法字体：从 jsdelivr CDN 下载（`https://cdn.jsdelivr.net/fontsource/fonts/...`），不要用 GitHub raw URL（会返回 HTML 错误页）

### macOS
```bash
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install weasyprint
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
```

## Troubleshooting

| 问题 | 解决 |
|------|------|
| `cannot load library 'libgobject-2.0-0'` | 用 Python 3.11+ venv，设置 `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` |
| 分页时标题孤立 | 加 `break-after: avoid` 到标题元素 |
| 时间线条目被劈开 | 加 `break-inside: avoid` 到条目容器（确保容器 < 半页） |
| 整页空白 | 大容器（.section/.chapter/article）去掉 `break-inside: avoid` |
| 渐变背景丢失 | 检查 `linear-gradient` 语法，WeasyPrint 支持标准写法 |
| 中文乱码 | WeasyPrint 自动使用系统 CJK 字体，确认系统有 Noto Sans CJK |
| 中文方框 | 检查 `font-family` 是否包含中文字体 |
| fpdf2 乱码 | 不要用 fpdf2 —— 对 .ttc 字体集合支持差，直接用 WeasyPrint |
| PDF 超 15MB | 压缩图片（`convert -resize 50%`）或拆分文档 |

## 工具选型参考

详见 `references/tool-landscape.md`。简要决策：

```
需要 PDF？
├─ 静态 HTML + CSS → WeasyPrint（本 skill，轻量矢量）
├─ 需要 JS 渲染/复杂动画 → Playwright headless print
└─ 前端用户点导出 → dompdf.js
```

## 版本记录

- v1.1.0（2026-07-01）：融合 hermes 租户实战经验——WeasyPrint 兼容性铁律（禁 flex/grid）、空白页防治、微信 15MB 限制、容器环境路径、中文字体 CDN 源、pdf-blank-check 验证脚本。
- v1.0.0：初版。WeasyPrint 转换 + 分页 CSS + 选型参考。
