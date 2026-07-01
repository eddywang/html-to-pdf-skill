# HTML to PDF Skill

一个面向 AI Agent（Hermes / Claude Code / Codex）的 HTML → PDF 生成技能，基于 **WeasyPrint** 主力管线 + **Playwright** 后备管线，附带 **dompdf.js** 前端方案的 Agent 注入用法。

## 核心能力

- **WeasyPrint**：轻量 Python 库，矢量 PDF 输出，CSS Paged Media 分页控制优秀，CJK 原生支持
- **Playwright headless print**：Chromium 渲染，CSS 100% 还原，适合复杂 JS/动画页面
- **dompdf.js 注入**：前端方案通过 Playwright 注入浏览器环境运行，输出极小体积矢量 PDF

## 快速开始

### 环境准备

```bash
# 方案一：uv（推荐）
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install weasyprint playwright pymupdf

# macOS 需要设置动态库路径
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib

# Playwright 需要安装 Chromium（首次）
playwright install chromium
```

### 用法

```bash
# WeasyPrint（推荐，适合大多数场景）
python scripts/html_to_pdf_weasyprint.py input.html output.pdf

# Playwright（复杂 CSS / JS 页面）
python scripts/html_to_pdf_playwright.py input.html output.pdf

# dompdf.js 注入（极小体积矢量 PDF，简单内容）
python scripts/html_to_pdf_dompdf.py input.html output.pdf
```

## 工具选型决策树

```
需要 PDF 输出
├─ 用户浏览器内直接导出？
│   └─ YES → dompdf.js（前端方案，npm/CDN 引入）
└─ 后端 / Agent / 批量？
    ├─ 内容是静态 HTML + CSS？ → WeasyPrint（轻量、矢量、分页好）
    └─ 内容依赖 JS 渲染 / 复杂动画 / SPA？ → Playwright headless print
```

## 实测对比

同一份中文简历 HTML（含渐变背景、时间线、卡片布局）：

| 方案 | 输出大小 | 保真度 | 文字可选 | 适合场景 |
|------|---------|--------|---------|---------|
| dompdf.js | 69 KB | ⭐⭐⭐ | ✅ | 前端导出、简单内容 |
| WeasyPrint | 229 KB | ⭐⭐⭐⭐ | ✅ | Agent 管线主力 |
| Playwright | 2.4 MB | ⭐⭐⭐⭐⭐ | ✅ | 复杂页面后备 |

## 分页优化最佳实践

WeasyPrint 对 `break-inside: avoid` 和 `break-after: avoid` 支持良好。在 HTML 中加入以下 CSS 可显著改善分页质量：

```css
/* 避免标题孤悬页尾 */
h2, h3 {
  break-after: avoid;
  page-break-after: avoid;
}

/* 卡片/时间线条目尽量不拆分 */
.timeline-item, .card, .callout {
  break-inside: avoid;
  page-break-inside: avoid;
}

/* A4 页面边距 */
@page {
  size: A4;
  margin: 18mm 20mm 22mm 20mm;
}
@page :first {
  margin: 0; /* 封面无边距 */
}
```

## 目录结构

```
.
├── SKILL.md                    # Agent skill 定义文件
├── README.md                   # 本文件
├── scripts/
│   ├── html_to_pdf_weasyprint.py   # WeasyPrint 转换脚本
│   ├── html_to_pdf_playwright.py   # Playwright 转换脚本
│   └── html_to_pdf_dompdf.py       # dompdf.js 注入转换脚本
├── references/
│   └── tool-landscape.md       # 工具选型详细对比文档
└── examples/
    ├── sample.html             # 示例 HTML（含分页优化 CSS）
    └── sample-output.pdf       # 示例输出 PDF
```

## 许可

MIT
