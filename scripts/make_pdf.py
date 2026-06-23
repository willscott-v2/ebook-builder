#!/usr/bin/env python3
"""Render an HTML ebook to PDF using whatever engine is available.
Tries, in order: Playwright (Python), headless Chrome/Chromium, wkhtmltopdf.
If none are present, prints clear browser Print-to-PDF instructions and exits 0.

Usage:
    python3 make_pdf.py ebook.html ebook.pdf
"""
import sys, os, shutil, subprocess, urllib.request

def via_playwright(html_path, pdf_path):
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return False
    file_url = "file://" + os.path.abspath(html_path)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.goto(file_url, wait_until="networkidle")
        pg.pdf(path=pdf_path, width="8.5in", height="11in",
               print_background=True, prefer_css_page_size=True)
        b.close()
    return True

def via_chrome(html_path, pdf_path):
    candidates = [
        "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    exe = next((c for c in candidates if shutil.which(c) or os.path.exists(c)), None)
    if not exe:
        return False
    file_url = "file://" + os.path.abspath(html_path)
    try:
        subprocess.run([exe, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        "--print-to-pdf=" + os.path.abspath(pdf_path), file_url],
                       check=True, timeout=120,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return os.path.exists(pdf_path)
    except Exception:
        return False

def via_wkhtmltopdf(html_path, pdf_path):
    if not shutil.which("wkhtmltopdf"):
        return False
    try:
        subprocess.run(["wkhtmltopdf", "--enable-local-file-access",
                        "--page-width", "8.5in", "--page-height", "11in",
                        "--margin-top", "0", "--margin-bottom", "0",
                        "--margin-left", "0", "--margin-right", "0",
                        html_path, pdf_path], check=True, timeout=120,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return os.path.exists(pdf_path)
    except Exception:
        return False

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: make_pdf.py ebook.html [ebook.pdf]\n"); sys.exit(1)
    html_path = sys.argv[1]
    pdf_path = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(html_path)[0] + ".pdf"

    for name, fn in (("Playwright", via_playwright),
                     ("headless Chrome", via_chrome),
                     ("wkhtmltopdf", via_wkhtmltopdf)):
        try:
            if fn(html_path, pdf_path):
                print("Rendered %s with %s" % (pdf_path, name))
                return
        except Exception:
            pass

    print(
        "\nNo PDF engine found, so the HTML is your deliverable as-is. To make a PDF "
        "with zero installs:\n"
        "  1. Open %s in any web browser (double-click it).\n"
        "  2. Print (Cmd/Ctrl-P).\n"
        "  3. Destination: Save as PDF.\n"
        "  4. Paper: Letter. Margins: None (or Default). Turn ON 'Background graphics'.\n"
        "  5. Save.\n"
        "The page CSS already sets the size and margins, so it prints exactly as designed.\n"
        "\nTo automate next time, install one engine:\n"
        "  pip install playwright && playwright install chromium\n"
        "  (or install Google Chrome, or `brew install wkhtmltopdf`)\n"
        % os.path.abspath(html_path)
    )

if __name__ == "__main__":
    main()
