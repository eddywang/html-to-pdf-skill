# HTML → PDF 工具选型速查

## 两大路线

| 维度 | 客户端（浏览器内） | 服务端 / CLI |
|------|-------------------|-------------|
| 代表工具 | dompdf.js (1.2k★)、jsPDF+html2canvas | WeasyPrint、Playwright/Puppeteer headless Chrome、wkhtmltopdf |
| 运行位置 | 用户浏览器，零后端 | Node/Python 进程或 Docker |
| 输出质量 | 矢量 PDF（文字可选/可编辑），但 CSS 支持有限 | 高保真（Chromium 渲染＝几乎 100% CSS 还原） |
| 依赖 | JS 库 ~200KB | Chromium ~400MB 或系统库 |
| 适用场景 | 前端用户点"导出 PDF" | 后端批量生成、Agent 自动化、CI |
| 分页控制 | 有限但可用（dompdf.js 有 pageBreak/divisionDisable） | 完善（`@page` CSS、`page-break-*`） |
| CJK 支持 | 需自行嵌入字体 | WeasyPrint/Chromium 原生支持系统字体 |

## dompdf.js (lmn1919/dompdf.js)

- 基于 html2canvas + jsPDF 魔改，输出真矢量 PDF（非截图）
- 纯前端、零服务器依赖；npm / CDN 引入
- 支持分页、页眉页脚（可按页定制函数）、强制分页 `pageBreak`、禁拆分 `divisionDisable`
- 文件体积小，不受 canvas 高度限制，能生成数千页
- 短板：基于 DOM 解析，CSS 支持不完整（不支持 iframe、部分阴影/渐变），复杂排版会有偏差
- 项目活跃（2026-05 更新），1.2k stars
- 适合场景：SaaS 产品前端"导出报告"功能

## 服务端方案对比

| 工具 | 优势 | 劣势 | 我们的用法 |
|------|------|------|-----------|
| **WeasyPrint** | 轻量 Python 库，CSS Paged Media 支持好，矢量输出 | 复杂 Flex/Grid 有限，macOS GTK 偶尔翻车 | 主力管线（pdf-report-standard skill） |
| **Playwright/Puppeteer** | Chromium 渲染＝完美 CSS，支持 JS 动态内容 | 依赖重（Chromium），headless 打印模式下负边距/渐变偶尔出问题 | 后备管线 |
| **wkhtmltopdf** | 单二进制，老牌稳定 | 基于旧 WebKit，CSS3 支持落后，已停维 | 不推荐新项目 |

## 选型决策树

```
需要 PDF 输出
├─ 用户浏览器内直接导出？
│   └─ YES → dompdf.js / jsPDF（前端方案）
└─ 后端/Agent/批量？
    ├─ 内容是静态 HTML + CSS？ → WeasyPrint（轻量、矢量、我们已有管线）
    └─ 内容依赖 JS 渲染/复杂动画/SPA？ → Playwright headless print
```

## 实测对比数据（2026-07 同一份简历 HTML）

| 方案 | 输出大小 | 特点 |
|------|---------|------|
| dompdf.js（Playwright 注入） | 69 KB | 矢量最轻，但渐变/复杂 CSS 丢失较多 |
| WeasyPrint | 229 KB | 矢量可选文字，CSS Paged Media 好，部分 Flex/渐变偏差 |
| Playwright headless print | 2.4 MB | 保真度最高（≈Chrome 打印），体积最大 |

## Agent 管线中使用 dompdf.js 的方法

前端方案也能在 Agent 里跑——通过 Playwright 打开 HTML 后注入 dompdf.min.js：

```python
from playwright.sync_api import sync_playwright
import base64

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 794, 'height': 1123})
    page.goto(f'file:///path/to/file.html', wait_until='networkidle')
    page.wait_for_timeout(2000)
    # 注入 dompdf.js（需提前下载到本地）
    with open('dompdf.min.js') as f:
        page.evaluate(f.read())
    page.wait_for_timeout(1000)
    # 调用 dompdf 生成 PDF blob → base64
    pdf_b64 = page.evaluate("""async () => {
        const blob = await dompdf(document.body, {pagination:true, format:'a4', compress:true});
        return new Promise(r => {
            const reader = new FileReader();
            reader.onloadend = () => r(reader.result.split(',')[1]);
            reader.readAsDataURL(blob);
        });
    }""")
    with open('output.pdf', 'wb') as f:
        f.write(base64.b64decode(pdf_b64))
    browser.close()
```

适用于需要极小体积矢量 PDF、且内容简单（无复杂渐变/Grid）的场景。

## 注意

- "长图 PDF"（截屏转单页 PDF）本质是图片，文字不可选不可搜，只适合演示/分享场景
- 对 Eddy 的交付物优先保证文字可提取（`pdftotext` 验证）
- 前端方案在 Agent 管线中可通过 Playwright 注入使用（见上），但日常交付仍优先 WeasyPrint/Playwright 原生打印
