#!/usr/bin/env python3
"""Extract articles (non-recipe) from URLs into JSON, for roundup ebooks.
Standard library only.

Usage:
    python3 extract_article.py "URL1" "URL2" ... > articles.json

For each URL it returns: name, brand, url, image (base64 data URI hero photo),
headnote (the deck/excerpt), body[] (first few content paragraphs as a teaser).
Pair with build_ebook.py — items with `body`/`points` instead of
`ingredients`/`steps` render as article pages and the footer reads
"Read the full story in <brand>".
"""
import sys, re, json, html, base64, urllib.request

HDR = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

def fetch(url, binary=False, timeout=25):
    data = urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=timeout).read()
    return data if binary else data.decode("utf-8", "ignore")

def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()

def meta(h, prop):
    m = (re.search(rf'property="{prop}" content="([^"]+)"', h) or
         re.search(rf'name="{prop}" content="([^"]+)"', h))
    return html.unescape(m.group(1)) if m else None

JUNK = re.compile(r'logo|favicon|icon|cropped|-\d+x\d+|placeholder|avatar|sprite|webimage|share|default', re.I)

def best_image(h):
    cands = []
    og = meta(h, "og:image")
    cands += re.findall(r'(https?://[^"\s]+?/wp-content/uploads/\d{4}/\d{2}/[^"\s]+?\.(?:jpg|jpeg|png))', h)
    if og:
        cands.insert(0, og)
    seen = set()
    for u in cands:
        if not u or u in seen:
            continue
        seen.add(u)
        if JUNK.search(u):
            continue
        try:
            data = fetch(u, binary=True)
        except Exception:
            continue
        if len(data) > 30000:
            mime = "image/png" if u.lower().endswith(".png") else "image/jpeg"
            return "data:%s;base64,%s" % (mime, base64.b64encode(data).decode())
    if og:
        try:
            return "data:image/jpeg;base64,%s" % base64.b64encode(fetch(og, binary=True)).decode()
        except Exception:
            pass
    return None

def title_of(h):
    t = meta(h, "og:title")
    if not t:
        m = re.search(r"<title>(.*?)</title>", h, re.S)
        t = text(m.group(1)) if m else "Untitled"
    return re.sub(r"\s*[|\-–—]\s*[^|\-–—]+$", "", t).strip() or t

def body_excerpt(h, n=3):
    """First n substantial paragraphs from the main content."""
    # narrow to an article/content container if present
    m = re.search(r'<(?:article|main)[^>]*>(.*?)</(?:article|main)>', h, re.S)
    scope = m.group(1) if m else h
    paras = []
    for p in re.findall(r'<p[^>]*>(.*?)</p>', scope, re.S):
        t = text(p)
        if len(t) >= 60 and not re.search(r'subscribe|cookie|newsletter|©|all rights reserved', t, re.I):
            paras.append(t)
        if len(paras) >= n:
            break
    return paras

def main():
    urls = sys.argv[1:]
    if not urls:
        sys.stderr.write("usage: extract_article.py URL [URL ...] > articles.json\n"); sys.exit(1)
    out = []
    for url in urls:
        host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
        try:
            h = fetch(url)
        except Exception as e:
            sys.stderr.write("FETCH ERROR %s: %s\n" % (url, e))
            out.append({"url": url, "error": str(e)}); continue
        body = body_excerpt(h)
        rec = {
            "name": title_of(h),
            "brand": host,
            "url": url,
            "image": best_image(h),
            "headnote": meta(h, "og:description") or meta(h, "description") or "",
            "body": body,
        }
        sys.stderr.write("ok  %-48s img=%s paras=%d\n" %
                         (rec["name"][:48], "Y" if rec["image"] else "N", len(body)))
        out.append(rec)
    print(json.dumps(out, indent=1, ensure_ascii=False))

if __name__ == "__main__":
    main()
