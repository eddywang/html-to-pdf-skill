#!/usr/bin/env python3
"""HTML to PDF via WeasyPrint — primary pipeline.

Usage:
    python html_to_pdf_weasyprint.py input.html [output.pdf]

If output path is omitted, generates input_name.pdf in the same directory.

Requirements:
    pip install weasyprint
    export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib  # macOS only
"""

import sys
import os

def convert(input_html: str, output_pdf: str | None = None) -> str:
    from weasyprint import HTML

    if not os.path.exists(input_html):
        raise FileNotFoundError(f"Input file not found: {input_html}")

    if output_pdf is None:
        base = os.path.splitext(input_html)[0]
        output_pdf = f"{base}.pdf"

    HTML(input_html).write_pdf(output_pdf)
    size_kb = os.path.getsize(output_pdf) / 1024
    print(f"✅ Generated: {output_pdf} ({size_kb:.0f} KB)")
    return output_pdf


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python html_to_pdf_weasyprint.py input.html [output.pdf]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    convert(input_file, output_file)
