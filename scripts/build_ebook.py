#!/usr/bin/env python3
"""Build a self-contained, print-ready recipe ebook HTML from config.json.
Standard library only. Images are embedded as data URIs.

Usage:
    python3 build_ebook.py config.json out.html

config.json schema: see references/config-schema.md
"""
import sys, json, html

def esc(s):
    return html.escape(str(s) if s is not None else "", quote=False)

def normalize_url(u):
    """Make a clickable href: pass through full URLs/anchors, else prepend https://."""
    u = (u or "").strip()
    if not u:
        return ""
    if u.startswith(("http://", "https://", "mailto:", "#")):
        return u
    return "https://" + u

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: build_ebook.py config.json [out.html]\n"); sys.exit(1)
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2] if len(sys.argv) > 2 else "ebook.html"

    B = cfg.get("brand", {})
    accent = B.get("accent", "#2D2A26")     # neutral warm-charcoal default; override per brand
    accent2 = B.get("accent2", "#A89B8C")   # neutral secondary (bullets); override per brand
    ink = B.get("ink", "#241F1C")
    cream = B.get("cream", "#FBF6EE")
    serif = B.get("serif", "Georgia, 'Times New Roman', serif")
    sans = B.get("sans", "Arial, Helvetica, sans-serif")

    recipes = cfg.get("recipes", [])
    cover_img = cfg.get("cover_image") or (recipes[0].get("image") if recipes else "")
    title = cfg.get("title", "Untitled Collection")
    subtitle = cfg.get("subtitle", "")
    contributors = cfg.get("contributors") or sorted({r.get("brand", "") for r in recipes if r.get("brand")})
    footer = cfg.get("footer", "")

    pages = []

    # ---- Cover ----
    brands_line = " &nbsp;·&nbsp; ".join(esc(c) for c in contributors)
    pages.append(
        '<div class="page cover">'
        '<div class="cover-img" style="background-image:url(\'' + (cover_img or "") + '\')"></div>'
        '<div class="cover-veil"></div>'
        '<div class="cover-txt">'
        + ('<div class="kicker">' + esc(cfg.get("kicker", "")) + '</div>' if cfg.get("kicker") else '')
        + '<h1>' + esc(title) + '</h1>'
        + ('<div class="sub">' + esc(subtitle) + '</div>' if subtitle else '')
        + ('<div class="brands">' + brands_line + '</div>' if brands_line else '')
        + '</div></div>'
    )

    # ---- Intro + table of contents ----
    intro = cfg.get("intro", {})
    toc = "".join(
        '<a class="toc-row" href="#r%d"><span class="tnum">%02d</span>'
        '<span class="tname">%s</span><span class="tbrand">%s</span></a>'
        % (i, i, esc(r.get("name", "")), esc(r.get("brand", "")))
        for i, r in enumerate(recipes, 1)
    )
    pages.append(
        '<div class="page pad">'
        '<div class="ornament">&#10087;</div>'
        '<h2 class="introh">' + esc(intro.get("heading", "Welcome")) + '</h2>'
        + "".join('<p%s>%s</p>' % (' class="lead"' if j == 0 else '', esc(p))
                  for j, p in enumerate(intro.get("paragraphs", [])))
        + '<div class="rule"></div><div class="toc">' + toc + '</div></div>'
    )

    # ---- Recipe pages ----
    for idx, r in enumerate(recipes, 1):
        racc = r.get("accent", accent)
        ings = r.get("ingredients") or []
        steps = r.get("steps") or []
        ing_li = "".join('<li>%s</li>' % esc(x) for x in ings)
        step_li = "".join('<li>%s</li>' % esc(x) for x in steps)
        body = '<div class="r-top">'
        if r.get("course"):
            body += '<span class="badge" style="background:%s">%s</span>' % (racc, esc(r["course"]))
        body += '<span class="r-brand" style="color:%s">%s</span></div>' % (racc, esc(r.get("brand", "")))
        body += '<h3 class="r-name">%s</h3>' % esc(r.get("name", ""))
        if r.get("headnote"):
            body += '<p class="r-head">%s</p>' % esc(r["headnote"])
        if ings:
            body += '<div class="ch" style="color:%s">Ingredients</div><ul class="ing">%s</ul>' % (racc, ing_li)
        if steps:
            body += '<div class="ch" style="color:%s;margin-top:.16in">Method</div><ol class="method">%s</ol>' % (racc, step_li)
        # article-roundup mode: render body paragraphs and/or key points instead of recipe fields
        for para in (r.get("body") or []):
            body += '<p class="r-article">%s</p>' % esc(para)
        pts = r.get("points") or []
        if pts:
            body += '<div class="ch" style="color:%s;margin-top:.12in">Highlights</div><ul class="ing onecol">%s</ul>' % (
                racc, "".join('<li>%s</li>' % esc(x) for x in pts))
        if r.get("url") or r.get("source_label"):
            is_recipe = bool(ings or steps)
            default_foot = ("Originally published in " if is_recipe else "Read the full story in ") + r.get("brand", "")
            foot_txt = esc(r.get("source_label", default_foot))
            if r.get("url"):
                foot_txt = '<a href="%s">%s</a>' % (normalize_url(r["url"]), foot_txt)
            body += '<div class="r-foot">%s</div>' % foot_txt
        pages.append(
            '<div class="rpage" id="r%d">' % idx
            + '<img class="r-hero" src="' + (r.get("image") or "") + '">'
            '<div class="r-body">' + body + '</div></div>'
        )

    # ---- Closing ----
    close = cfg.get("closing", {})
    cards = ""
    for s in close.get("subscribe", []):
        col = s.get("color", accent)
        href = normalize_url(s.get("link") or s.get("url"))
        cards += ('<a class="card" href="%s" style="border-top:6px solid %s">'
                  '<div class="cbrand" style="color:%s">%s</div>'
                  '<div class="curl">%s</div>'
                  '<div class="cbtn" style="background:%s">Subscribe</div></a>'
                  % (href, col, col, esc(s.get("name", "")), esc(s.get("url", "")), col))
    pages.append(
        '<div class="page pad close">'
        '<div class="ornament">&#10087;</div>'
        '<h2 class="introh">' + esc(close.get("heading", "Subscribe")) + '</h2>'
        + "".join('<p%s>%s</p>' % (' class="lead"' if j == 0 else '', esc(p))
                  for j, p in enumerate(close.get("paragraphs", [])))
        + ('<div class="cards">' + cards + '</div>' if cards else '')
        + ('<div class="endmark">' + esc(footer) + '</div>' if footer else '')
        + '</div>'
    )

    css = CSS
    for k, v in {"__ACCENT__": accent, "__ACCENT2__": accent2, "__INK__": ink,
                 "__CREAM__": cream, "__SERIF__": serif, "__SANS__": sans}.items():
        css = css.replace(k, v)

    doc = ('<!doctype html><html><head><meta charset="utf-8">'
           '<title>' + esc(title) + '</title><style>' + css + '</style></head><body>'
           + "".join(pages) + '</body></html>')
    open(out, "w", encoding="utf-8").write(doc)
    sys.stderr.write("wrote %s  (%d pages, %d bytes)\n" % (out, len(pages), len(doc)))


CSS = """
*{margin:0;padding:0;box-sizing:border-box}
@page{size:8.5in 11in;margin:0}
html{background:__CREAM__}
body{font-family:__SERIF__;color:__INK__}
a{color:inherit;text-decoration:none}
.page{width:8.5in;position:relative;overflow:hidden;page-break-before:always;background:__CREAM__}
.pad{padding:1.1in 1in;min-height:10.9in}
.cover{background:__INK__;height:11in}
.cover-img{position:absolute;inset:0;background-size:cover;background-position:center}
.cover-veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(20,16,14,.35),rgba(20,16,14,.82))}
.cover-txt{position:absolute;left:0;right:0;bottom:1in;text-align:center;color:__CREAM__;padding:0 .8in}
.kicker{font-family:__SANS__;letter-spacing:.32em;text-transform:uppercase;font-size:11pt;color:#E9C98B;margin-bottom:.22in}
.cover h1{font-size:54pt;line-height:.98;font-weight:700;letter-spacing:-.5pt;text-shadow:0 2px 18px rgba(0,0,0,.4)}
.cover .sub{font-style:italic;font-size:17pt;margin-top:.18in;color:#F3E7D4}
.cover .brands{font-family:__SANS__;font-size:9.5pt;letter-spacing:.08em;margin-top:.42in;color:#D9C7AE}
.ornament{font-size:30pt;color:__ACCENT__;text-align:center;margin-bottom:.15in}
.introh{font-size:34pt;text-align:center;color:__INK__;margin-bottom:.28in}
.lead{font-size:15pt;line-height:1.6;font-style:italic;color:#4A3F38;margin-bottom:.2in}
.pad p{font-size:12.5pt;line-height:1.7;margin-bottom:.16in;color:#3A322D}
.rule{height:2px;background:#D8C7AE;margin:.32in 0}
.toc-row{display:flex;align-items:baseline;gap:.18in;padding:.085in 0;border-bottom:1px solid #E7DAC6}
.tnum{font-family:__SANS__;color:__ACCENT__;font-weight:700;width:.4in}
.tname{flex:1;font-size:12.5pt}
.tbrand{font-family:__SANS__;font-size:8.5pt;color:#8A7B6B;text-transform:uppercase;letter-spacing:.06em}
.rpage{width:8.5in;page-break-before:always;background:__CREAM__}
.r-hero{display:block;width:8.5in;height:3.05in;object-fit:cover}
.r-body{background:__CREAM__;border-radius:18px 18px 0 0;margin-top:-.3in;position:relative;padding:.34in .72in .4in;min-height:0;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.r-top{display:flex;align-items:center;gap:.16in;margin-bottom:.05in}
.badge{font-family:__SANS__;color:#fff;font-size:8pt;letter-spacing:.12em;text-transform:uppercase;padding:3px 11px;border-radius:20px}
.r-brand{font-family:__SANS__;font-size:8.5pt;text-transform:uppercase;letter-spacing:.10em;font-weight:700}
.r-name{font-size:23pt;line-height:1.03;margin-bottom:.04in}
.r-head{font-style:italic;font-size:10.5pt;line-height:1.4;color:#5A4E45;margin-bottom:.1in}
.ch{font-family:__SANS__;font-size:9pt;letter-spacing:.14em;text-transform:uppercase;margin-bottom:.06in;font-weight:700}
ul.ing{list-style:none;columns:2;column-gap:.5in;margin-bottom:.04in}
ul.ing li{font-size:8.8pt;line-height:1.3;padding-left:.15in;position:relative;margin-bottom:2px;color:#332C27;break-inside:avoid}
ul.ing li:before{content:"";position:absolute;left:0;top:.048in;width:4px;height:4px;border-radius:50%;background:__ACCENT2__}
ol.method{list-style:none;counter-reset:m}
ol.method li{font-size:9.2pt;line-height:1.37;padding-left:.32in;position:relative;margin-bottom:.055in;color:#2E2723;break-inside:avoid}
ol.method li:before{counter-increment:m;content:counter(m);position:absolute;left:0;top:.005in;font-family:__SANS__;font-weight:700;font-size:8.5pt;color:__ACCENT__;border:1.5px solid #D8B79A;border-radius:50%;width:.19in;height:.19in;line-height:.165in;text-align:center}
.r-foot{font-family:__SANS__;font-size:8pt;letter-spacing:.04em;color:#A1907D;margin-top:.16in;break-before:avoid;page-break-before:avoid}
.r-article{font-size:10.5pt;line-height:1.5;color:#3A322D;margin-bottom:.12in}
ul.ing.onecol{columns:1}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:.28in;margin-top:.4in}
.card{display:block;background:#fff;border:1px solid #E7DAC6;border-radius:10px;padding:.28in;text-align:center;box-shadow:0 4px 14px rgba(0,0,0,.05)}
.cbrand{font-size:16pt;font-weight:700;margin-bottom:.08in}
.curl{font-family:__SANS__;font-size:9pt;color:#8A7B6B;margin-bottom:.16in;word-break:break-all}
.cbtn{display:inline-block;color:#fff;font-family:__SANS__;font-size:10pt;letter-spacing:.1em;text-transform:uppercase;padding:7px 22px;border-radius:22px}
.endmark{text-align:center;font-family:__SANS__;font-size:9pt;letter-spacing:.18em;text-transform:uppercase;color:#A99A88;margin-top:.5in}
body>*:first-child{page-break-before:avoid}
/* On-screen only: center the pages on a neutral gutter so the HTML reads like a document.
   Print ignores this block entirely, so the PDF stays full-bleed. */
@media screen{
  body{background:#E7E2DA}
  .page,.rpage{margin:0 auto 14px;box-shadow:0 2px 12px rgba(0,0,0,.14)}
}
"""

if __name__ == "__main__":
    main()
