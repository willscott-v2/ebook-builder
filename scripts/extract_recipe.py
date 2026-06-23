#!/usr/bin/env python3
"""Extract recipes from article URLs into JSON. Standard library only.

Usage:
    python3 extract_recipe.py "URL1" "URL2" ... > recipes.json

For each URL it returns: name, brand (publisher), url, image (base64 data URI of
the real hero photo), headnote, ingredients[], steps[]. Handles JSON-LD Recipe
(incl. HowToStep/HowToSection), WP Recipe Maker, Tasty Recipes, and EasyRecipe.

Known gotcha it works around: og:image is often a generic social share card, not
the dish photo. We prefer the JSON-LD recipe image, then a real content photo,
and only fall back to og:image as a last resort. See references/design-notes.md.
"""
import sys, re, json, html, base64, urllib.request

HDR = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}

def fetch(url, binary=False, timeout=25):
    req = urllib.request.Request(url, headers=HDR)
    data = urllib.request.urlopen(req, timeout=timeout).read()
    return data if binary else data.decode("utf-8", "ignore")

def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()

def meta(h, prop):
    m = (re.search(rf'property="{prop}" content="([^"]+)"', h) or
         re.search(rf'name="{prop}" content="([^"]+)"', h))
    return html.unescape(m.group(1)) if m else None

def jsonld_objects(h):
    out = []
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', h, re.S):
        try:
            out.append(json.loads(m.group(1)))
        except Exception:
            pass
    return out

def walk_find(obj, typ):
    """Find first dict whose @type includes `typ`."""
    if isinstance(obj, dict):
        t = obj.get("@type", "")
        if t == typ or (isinstance(t, list) and typ in t):
            return obj
        for v in obj.values():
            r = walk_find(v, typ)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = walk_find(v, typ)
            if r:
                return r
    return None

def jsonld_images(h):
    urls = []
    def walk(x):
        if isinstance(x, dict):
            if x.get("@type") == "ImageObject" and x.get("url"):
                urls.append(x["url"])
            img = x.get("image")
            if isinstance(img, str):
                urls.append(img)
            elif isinstance(img, dict) and img.get("url"):
                urls.append(img["url"])
            elif isinstance(img, list):
                for it in img:
                    if isinstance(it, str): urls.append(it)
                    elif isinstance(it, dict) and it.get("url"): urls.append(it["url"])
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    for o in jsonld_objects(h):
        walk(o)
    return urls

def collect_steps(instr):
    """recipeInstructions -> list[str], handling HowToStep and HowToSection."""
    steps = []
    if isinstance(instr, str):
        return [text(instr)]
    for s in (instr or []):
        if isinstance(s, str):
            steps.append(text(s))
        elif isinstance(s, dict):
            t = s.get("@type", "")
            if t == "HowToSection":
                steps += collect_steps(s.get("itemListElement", []))
            else:
                steps.append(text(s.get("text") or s.get("name") or ""))
    return [s for s in steps if s]

def extract_recipe_fields(h):
    """Return (ingredients, steps) using JSON-LD then plugin fallbacks."""
    ings, steps = [], []
    rec = walk_find_recipe(h)
    if rec:
        raw_ing = rec.get("recipeIngredient") or rec.get("ingredients") or []
        ings = [text(i) for i in raw_ing if text(i)]
        steps = collect_steps(rec.get("recipeInstructions"))
    # WP Recipe Maker
    if not ings:
        ings = [text(x) for x in re.findall(r'class="wprm-recipe-ingredient"[^>]*>(.*?)</li>', h, re.S) if text(x)]
    if not steps:
        steps = [text(x) for x in re.findall(r'class="wprm-recipe-instruction-text">(.*?)</div>', h, re.S) if text(x)]
    # EasyRecipe (class="ingredient" / class="instruction")
    if not ings:
        ings = [text(x) for x in re.findall(r'class="ingredient"[^>]*>(.*?)</li>', h, re.S) if text(x)]
    if not steps:
        steps = [text(x) for x in re.findall(r'class="instruction"[^>]*>(.*?)</li>', h, re.S) if text(x)]
    # Tasty Recipes
    if not ings:
        block = re.search(r'class="tasty-recipes-ingredients[^"]*"[^>]*>(.*?)</div>\s*</div>', h, re.S)
        if block:
            ings = [text(li) for li in re.findall(r'<li[^>]*>(.*?)</li>', block.group(1), re.S) if text(li)]
    if not steps:
        block = re.search(r'class="tasty-recipes-instructions[^"]*"[^>]*>(.*?)</div>\s*</div>', h, re.S)
        if block:
            steps = [text(li) for li in re.findall(r'<li[^>]*>(.*?)</li>', block.group(1), re.S) if text(li)]
    # microdata fallback
    if not ings:
        ings = [text(x) for x in re.findall(r'itemprop="(?:recipeIngredient|ingredients)"[^>]*>(.*?)</', h, re.S) if text(x)]
    return ings[:40], steps[:25]

def walk_find_recipe(h):
    for o in jsonld_objects(h):
        r = walk_find(o, "Recipe")
        if r:
            return r
    return None

JUNK = re.compile(r'logo|favicon|icon|cropped|-\d+x\d+|placeholder|avatar|sprite|webimage|share|default', re.I)

def best_image(h, base_host):
    """Prefer real dish photo over the social share card."""
    cands = []
    rec = walk_find_recipe(h)
    if rec:
        img = rec.get("image")
        if isinstance(img, str): cands.append(img)
        elif isinstance(img, dict) and img.get("url"): cands.append(img["url"])
        elif isinstance(img, list):
            for it in img:
                cands.append(it if isinstance(it, str) else it.get("url"))
    cands += jsonld_images(h)
    cands += re.findall(r'(https?://[^"\s]+?/wp-content/uploads/\d{4}/\d{2}/[^"\s]+?\.(?:jpg|jpeg|png))', h)
    og = meta(h, "og:image")
    if og: cands.append(og)  # last resort
    seen = set()
    for u in cands:
        if not u or u in seen: continue
        seen.add(u)
        if JUNK.search(u): continue
        try:
            data = fetch(u, binary=True)
        except Exception:
            continue
        if len(data) > 40000:  # real photo, not a sliver/icon
            mime = "image/png" if u.lower().endswith(".png") else "image/jpeg"
            return "data:%s;base64,%s" % (mime, base64.b64encode(data).decode())
    # accept og even if small, rather than nothing
    if og:
        try:
            data = fetch(og, binary=True)
            return "data:image/jpeg;base64,%s" % base64.b64encode(data).decode()
        except Exception:
            pass
    return None

def title_of(h):
    t = meta(h, "og:title")
    if not t:
        m = re.search(r"<title>(.*?)</title>", h, re.S)
        t = text(m.group(1)) if m else "Untitled"
    # strip a trailing " - Publication" / " | Publication" site-name segment
    return re.sub(r"\s*[|\-–—]\s*[^|\-–—]+$", "", t).strip() or t

def main():
    urls = sys.argv[1:]
    if not urls:
        sys.stderr.write("usage: extract_recipe.py URL [URL ...] > recipes.json\n")
        sys.exit(1)
    out = []
    for url in urls:
        host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
        try:
            h = fetch(url)
        except Exception as e:
            sys.stderr.write("FETCH ERROR %s: %s\n" % (url, e))
            out.append({"url": url, "error": str(e)})
            continue
        ings, steps = extract_recipe_fields(h)
        rec = {
            "name": title_of(h),
            "brand": host,                       # publisher; rename in config.json
            "url": url,
            "image": best_image(h, host),
            "headnote": meta(h, "og:description") or meta(h, "description") or "",
            "ingredients": ings,
            "steps": steps,
        }
        sys.stderr.write("ok  %-44s img=%s ing=%d steps=%d\n" %
                         (rec["name"][:44], "Y" if rec["image"] else "N", len(ings), len(steps)))
        out.append(rec)
    print(json.dumps(out, indent=1, ensure_ascii=False))

if __name__ == "__main__":
    main()
