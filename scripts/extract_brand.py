#!/usr/bin/env python3
"""Pull candidate brand tokens from a publication's homepage. Stdlib only.
The output is a STARTING POINT — use judgment to pick the final palette.

Usage:
    python3 extract_brand.py "https://publication.com" > brand.json
"""
import sys, re, json, html, urllib.request, collections

HDR = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=25).read().decode("utf-8", "ignore")

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: extract_brand.py URL > brand.json\n"); sys.exit(1)
    url = sys.argv[1]
    try:
        h = fetch(url)
    except Exception as e:
        sys.stderr.write("fetch error: %s\n" % e)
        h = ""

    theme = re.search(r'name="theme-color" content="([^"]+)"', h)

    # Count hex colors that appear in inline CSS / style blocks; bias toward saturated, non-neutral.
    hexes = re.findall(r'#([0-9a-fA-F]{6})\b', h)
    counts = collections.Counter(x.lower() for x in hexes)
    def is_neutral(hx):
        r, g, b = int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)
        mx, mn = max(r, g, b), min(r, g, b)
        return (mx - mn) < 28 or mx > 240 or mx < 25       # gray / near-white / near-black
    accents = [("#" + hx, n) for hx, n in counts.most_common(40) if not is_neutral(hx)][:8]

    fonts = []
    for m in re.findall(r'font-family\s*:\s*([^;"}<]+)', h, re.I):
        fam = re.split(r'[,;]', m.strip())[0].strip(" '\"")
        if fam and fam.lower() not in ("inherit", "initial", "unset") and len(fam) < 40:
            fonts.append(fam)
    fonts = [f for f, _ in collections.Counter(fonts).most_common(8)]

    logos = re.findall(r'<img[^>]+(?:class="[^"]*logo[^"]*"|alt="[^"]*logo[^"]*")[^>]*src="([^"]+)"', h, re.I)

    result = {
        "_note": "Candidates only. Pick one strong accent + a serif (display) + a sans (labels). "
                 "Good fallbacks: cream #FBF6EE, ink #241F1C, serif Georgia, sans Arial.",
        "theme_color": theme.group(1) if theme else None,
        "accent_candidates": [c for c, _ in accents],
        "font_candidates": fonts,
        "logo_candidates": [html.unescape(l) for l in logos[:4]],
        "suggested": {
            "accent": (theme.group(1) if theme else (accents[0][0] if accents else "#2D2A26")),
            "ink": "#241F1C",
            "cream": "#FBF6EE",
            "serif": (fonts[0] + ", Georgia, serif") if fonts else "Georgia, 'Times New Roman', serif",
            "sans": "Arial, Helvetica, sans-serif",
        },
    }
    print(json.dumps(result, indent=1, ensure_ascii=False))

if __name__ == "__main__":
    main()
