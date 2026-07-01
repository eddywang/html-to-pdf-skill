# HTML to PDF Skill

基于 **WeasyPrint** 的 HTML → PDF 生成技能，面向 AI Agent（Hermes / Claude Code / Codex）。矢量 PDF 输出、CJK 字体支持、分页优化、空白页检测。

## 一键安装

```bash
# Claude Code
curl -sL https://raw.githubusercontent.com/eddywang/html-to-pdf-skill/main/SKILL.md -o .claude/skills/html-to-pdf/SKILL.md && mkdir -p .claude/skills/html-to-pdf/{scripts,references} && curl -sL https://raw.githubusercontent.com/eddywang/html-to-pdf-skill/main/scripts/html_to_pdf_weasyprint.py -o .claude/skills/html-to-pdf/scripts/html_to_pdf_weasyprint.py && curl -sL https://raw.githubusercontent.com/eddywang/html-to-pdf-skill/main/scripts/pdf-blank-check.py -o .claude/skills/html-to-pdf/scripts/pdf-blank-check.py && curl -sL https://raw.githubusercontent.com/eddywang/html-to-pdf-skill/main/references/base-print.css -o .claude/skills/html-to-pdf/references/base-print.css

# Hermes Agent
git clone https://github.com/eddywang/html-to-pdf-skill.git ~/.hermes/skills/creative/html-to-pdf
```

## 核心特点

- 矢量 PDF，文字可选可搜索
- CSS Paged Media 分页控制（`@page`、`break-inside`、`break-after`）
- CJK 字体原生支持，无需额外嵌入
- 输出体积小（通常 100-300 KB）
- 无 Chromium 依赖，轻量 Python 库
- 空白页自动检测脚本
- WeasyPrint 兼容性铁律（禁 flex/grid，用 table 布局）

## 快速开始

```bash
# macOS
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install weasyprint
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
python scripts/html_to_pdf_weasyprint.py input.html output.pdf

# Linux (Hermes 容器)
/opt/hermes/.venv/bin/python3 scripts/html_to_pdf_weasyprint.py input.html output.pdf
```

## 生成流程

1. **写 HTML** — `<style>` 中必须包含 `references/base-print.css` 的内容
2. **渲染 PDF** — `python scripts/html_to_pdf_weasyprint.py input.html output.pdf`
3. **验证**（不可跳过）：
   ```bash
   pdftotext output.pdf - | head -20          # 文字可提取
   python scripts/pdf-blank-check.py output.pdf  # 无空白页
   ```

## ⛔ WeasyPrint 兼容性铁律

| 禁止 | 替代 |
|------|------|
| `display: flex` | `display: table` / `display: table-cell` |
| `display: grid` | `display: table` + 百分比宽度 |
| 大容器加 `break-inside: avoid` | 只给小块（< 130mm）加 |

## 目录结构

```
.
├── SKILL.md                        # Agent skill 定义（含完整流程+铁律+troubleshooting）
├── README.md
├── scripts/
│   ├── html_to_pdf_weasyprint.py   # 转换脚本
│   └── pdf-blank-check.py          # 空白页检测
├── references/
│   ├── base-print.css              # 分页+布局 CSS 模板（直接粘进 HTML）
│   └── tool-landscape.md           # 工具选型对比
└── examples/
    ├── sample.html                 # 示例（含分页优化 CSS）
    ├── sample-output.pdf           # 示例输出
    └── test-chinese.html           # 中文排版测试页
```

## 许可

MIT
