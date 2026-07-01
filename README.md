# HTML to PDF Skill

基于 **WeasyPrint** 的 HTML → PDF 生成技能，面向 AI Agent（Hermes / Claude Code / Codex）。专注矢量 PDF 输出、CJK 字体支持、分页优化。

## 一键安装（Agent Skill）

```bash
# Claude Code
curl -sL https://raw.githubusercontent.com/eddywang/html-to-pdf-skill/main/SKILL.md -o .claude/skills/html-to-pdf/SKILL.md && mkdir -p .claude/skills/html-to-pdf/scripts && curl -sL https://raw.githubusercontent.com/eddywang/html-to-pdf-skill/main/scripts/html_to_pdf_weasyprint.py -o .claude/skills/html-to-pdf/scripts/html_to_pdf_weasyprint.py

# Hermes Agent
git clone https://github.com/eddywang/html-to-pdf-skill.git ~/.hermes/skills/creative/html-to-pdf
```

## 核心特点

- 矢量 PDF，文字可选可搜索
- CSS Paged Media 分页控制（`@page`、`break-inside`、`break-after`）
- CJK 字体原生支持，无需额外嵌入
- 输出体积小（通常 100-300 KB）
- 无 Chromium 依赖，轻量 Python 库

## 快速开始

```bash
# 环境准备（uv 推荐）
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install weasyprint

# macOS 需设置动态库路径
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib

# 转换
python scripts/html_to_pdf_weasyprint.py input.html output.pdf
```

## 分页优化

WeasyPrint 对 CSS 分页属性支持良好。在 HTML 中加入以下 CSS 可避免"孤立标题"和内容块被劈开：

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
```

## 目录结构

```
.
├── SKILL.md                        # Agent skill 定义
├── README.md
├── scripts/
│   └── html_to_pdf_weasyprint.py   # 转换脚本
├── references/
│   └── tool-landscape.md           # 工具选型对比（供参考）
└── examples/
    ├── sample.html                 # 示例 HTML（含分页优化 CSS）
    └── sample-output.pdf           # 示例输出
```

## Troubleshooting

| 问题 | 解决 |
|------|------|
| `cannot load library 'libgobject-2.0-0'` | 用 Python 3.11+ venv + `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` |
| 分页时标题孤立在页尾 | 加 `break-after: avoid` |
| 时间线/卡片被劈开 | 加 `break-inside: avoid` |
| 渐变背景未渲染 | WeasyPrint 支持 `linear-gradient`，检查语法 |

## 许可

MIT
