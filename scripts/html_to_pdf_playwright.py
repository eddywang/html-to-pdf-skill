#!/usr/bin/env python3
"""HTML to PDF via Playwright headless Chromium print — fallback pipeline.

Usage:
    python html_to_pdf_playwright.py input.html [output.pdf]

If output path is omitted, generates input_name.pdf in the same directory.

Requirements:
    pip install playwright
    playwright install chromium
"""

import sys
import os


def convert(input_html: str, output_pdf: str | None = None) -> str:
    from playwright.sync_api import sync_playwright

    if not os.path.exists(input_html):
        raise FileNotFoundError(f"Input file not found: {input_html}")

    if output_pdf is None:
        base = os.path.splitext(input_html)[0]
        output_pdf = f"{base}.pdf"

    abs_html = os.path.abspath(input_html)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file://{abs_html}", wait_until="networkidle")
        page.wait_for_timeout(2000)  # wait for animations/lazy content
        page.pdf(
            path=output_pdf,
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()

    size_kb = os.path.getsize(output_pdf) / 1024
    print(f"✅ Generated: {output_pdf} ({size_kb:.0f} KB)")
    return output_pdf


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python html_to_pdf_playwright.py input.html [output.pdf]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    convert(input_file, output_file)
