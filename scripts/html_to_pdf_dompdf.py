#!/usr/bin/env python3
"""HTML to PDF via dompdf.js injection — lightweight vector PDF.

Injects dompdf.js into a Playwright browser context to generate a client-side
vector PDF. Produces the smallest file size but has limited CSS support.

Usage:
    python html_to_pdf_dompdf.py input.html [output.pdf]

Requirements:
    pip install playwright
    playwright install chromium
    # dompdf.min.js must be downloaded to scripts/ directory:
    # curl -sL "https://cdn.jsdelivr.net/npm/dompdf.js@latest/dist/dompdf.min.js" -o scripts/dompdf.min.js
"""

import sys
import os
import base64


def convert(input_html: str, output_pdf: str | None = None) -> str:
    from playwright.sync_api import sync_playwright

    if not os.path.exists(input_html):
        raise FileNotFoundError(f"Input file not found: {input_html}")

    if output_pdf is None:
        base = os.path.splitext(input_html)[0]
        output_pdf = f"{base}.pdf"

    abs_html = os.path.abspath(input_html)

    # Locate dompdf.min.js relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dompdf_js_path = os.path.join(script_dir, "dompdf.min.js")
    if not os.path.exists(dompdf_js_path):
        raise FileNotFoundError(
            f"dompdf.min.js not found at {dompdf_js_path}.\n"
            "Download it: curl -sL 'https://cdn.jsdelivr.net/npm/dompdf.js@latest/dist/dompdf.min.js' "
            f"-o '{dompdf_js_path}'"
        )

    with open(dompdf_js_path, "r") as f:
        dompdf_code = f.read()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # A4 width in pixels at 96 DPI
        page = browser.new_page(viewport={"width": 794, "height": 1123})
        page.goto(f"file://{abs_html}", wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Inject dompdf.js
        page.evaluate(dompdf_code)
        page.wait_for_timeout(1000)

        # Generate PDF
        pdf_base64 = page.evaluate(
            """async () => {
            return new Promise((resolve, reject) => {
                if (typeof dompdf === 'undefined') {
                    reject('dompdf not loaded');
                    return;
                }
                dompdf(document.body, {
                    pagination: true,
                    format: 'a4',
                    compress: true
                }).then((blob) => {
                    const reader = new FileReader();
                    reader.onloadend = () => resolve(reader.result.split(',')[1]);
                    reader.readAsDataURL(blob);
                }).catch(reject);
            });
        }"""
        )

        with open(output_pdf, "wb") as f:
            f.write(base64.b64decode(pdf_base64))

        browser.close()

    size_kb = os.path.getsize(output_pdf) / 1024
    print(f"✅ Generated: {output_pdf} ({size_kb:.0f} KB)")
    return output_pdf


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python html_to_pdf_dompdf.py input.html [output.pdf]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    convert(input_file, output_file)
