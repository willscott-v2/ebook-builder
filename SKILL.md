---
name: recipe-ebook-builder
description: Build a branded, print-ready recipe ebook (a single self-contained HTML plus a PDF) from a list of recipe article URLs, matched to a publication's look and voice. Use when someone wants to turn already-published recipes into a cohesive downloadable cookbook or lead magnet with a cover, intro, recipe pages, and a subscribe call-to-action. Needs only the article URLs the user provides. No SEO tools and no web hosting required.
---

# Recipe Ebook Builder

Turn a list of recipe URLs into a designed ebook: a cover, an intro written in the publication's voice, one page per recipe (hero photo, ingredients, numbered method), and a closing "subscribe" page. Output is a **single self-contained HTML file** (images embedded, so it needs no hosting) and a **PDF**.

The whole thing runs on the URLs the user brings. It does not need any paid SEO tool. It does not need a server or cloud storage.

## When to use
- The user has a set of published recipes (their own magazine/blog) and wants a downloadable ebook, sampler, or lead magnet.
- They want it to look and read like a specific publication.
- **Article-roundup mode:** also builds non-recipe roundups (features, guides, posts) — use `scripts/extract_article.py` instead of `extract_recipe.py`. See "Article-roundup mode" near the end.

## What to collect from the user first
1. **The recipe URLs** — the articles to include (5–15 is a good ebook).
2. **The publication** — name and homepage URL, used to derive the look and the voice. If the recipes come from several titles, pick one as the voice anchor (usually the one contributing the most/most-iconic recipes).
3. **Title and theme** — e.g. "Summer Cookout — warm-weather dishes." If they don't have one, propose a few.
4. **Subscribe targets** for the closing CTA — the magazine subscribe URLs (one per contributing brand). Optional; can be left as the homepage.

Ask for these up front. Don't start extracting until you have at least the URLs and the publication.

## Workflow

Run from a working directory. The scripts are in `scripts/` next to this file; reference them by absolute path.

### 1. Extract every recipe
For each URL, run the extractor. It fetches the page and parses the title, the real hero photo (not the social share card — see design-notes), the headnote, the ingredients, and the method, handling JSON-LD plus the common WordPress recipe plugins.

```bash
python3 scripts/extract_recipe.py "URL1" "URL2" ... > recipes.json
```

Review `recipes.json`. If any recipe has empty `ingredients` or `steps`, open that page's HTML and check which plugin it uses (see references/design-notes.md → "Recipe extraction"), then add the selector. If the hero `image` is tiny or a logo, the extractor already tries to skip share cards; if it still missed, grab the real content photo manually.

### 2. Derive the look (brand tokens)
Pull the publication's palette and fonts to make the ebook feel like theirs:

```bash
python3 scripts/extract_brand.py "https://publication-homepage.com" > brand.json
```

This returns candidate accent colors (from `theme-color`, CSS, the logo), the cream/paper tone, the ink tone, and the font families it finds. **Then use judgment:** open the site (fetch it, or look at a screenshot if you can) and pick a tasteful set — one strong accent, a near-white cream paper, a dark ink, a serif for display and a sans for labels. Confirm the palette with the user in one line before building. Good defaults if the site is bare: accent from the brand's known color, cream `#FBF6EE`, ink `#241F1C`, serif Georgia, sans Arial.

### 3. Capture the voice
Read 2–3 of the supplied articles (their intros/headnotes are enough). Write a 3–4 line voice summary (cadence, vocabulary, what it celebrates). You'll write the intro and closing in that voice. Match it; don't impose a generic "cookbook" tone. Watch for and avoid AI tells per the house voice rules if any are loaded.

### 4. Write the intro and closing
- **Intro** (~3 short paragraphs): welcome the reader, name the theme, and set the table in the publication's voice. Avoid hype.
- **Closing**: a short subscribe CTA in the same voice, plus one card per contributing brand with its subscribe URL.

### 5. Assemble the config
Build `config.json` combining everything (schema in references/config-schema.md). It carries: title/subtitle, brand tokens, intro paragraphs, the recipes (from step 1), and the closing copy + subscribe cards. Set each recipe's `course` (Appetizer/Main/Side/Bread/Dessert) and a one-line `headnote` if you want to override the extracted one.

### 6. Build the ebook HTML
```bash
python3 scripts/build_ebook.py config.json ebook.html
```
This emits one self-contained HTML file: cover, intro + table of contents, a page per recipe, and the closing. Images are embedded as data URIs, so the file is portable and prints with photos intact. The print CSS already handles the hard-won details: cream page canvas, clean top/bottom buffers at page breaks, two-column ingredients, numbered method steps, long recipes that flow to a second page.

### 7. Make the PDF
```bash
python3 scripts/make_pdf.py ebook.html ebook.pdf
```
It tries, in order: Playwright, headless Chrome/Chromium, then wkhtmltopdf. **If none are installed, it prints clear instructions** to open the HTML in any browser and use Print → "Save as PDF" with margins set to None / Default and "Background graphics" on. That browser route needs nothing installed and produces the same result.

### 8. Deliver
Hand back the `.html` (self-contained, shareable as-is) and the `.pdf`. Tell the user the file paths. The HTML can be emailed or opened directly; no upload needed.

## Portability notes (why this works for anyone)
- **No SEO tools.** Discovery isn't part of this skill — the user supplies the URLs. Extraction uses only Python's standard library plus `urllib`.
- **No hosting.** Images are base64-embedded; the HTML is one self-contained file.
- **No required PDF engine.** Detected if present; otherwise browser Print-to-PDF.
- **Stdlib only.** `extract_recipe.py`, `extract_brand.py`, and `build_ebook.py` use only the Python standard library. `make_pdf.py` uses whatever rendering engine exists, or none.

## Article-roundup mode
For non-recipe collections (a "best features of the year," a guide roundup, a blog digest), the workflow is identical except two things:
- **Extract** with `python3 scripts/extract_article.py "URL1" "URL2" ... > articles.json`. It pulls the title, hero image, headnote, and a short body excerpt (no ingredients/method).
- **In `config.json`**, each item carries `body` (a few teaser paragraphs) and/or `points` (bullet highlights) instead of `ingredients`/`steps`, and `course` becomes a section label (e.g. "Feature", "Guide", "Profile"). The template renders an article page, and the footer reads "Read the full story in <brand>." Cover, intro, subscribe CTA, palette, and voice all work the same. A single book can even mix recipe items and article items.

## Troubleshooting
See `references/design-notes.md` for the gotchas worth knowing: social share images masquerading as hero photos, the recipe-plugin selector zoo (WP Recipe Maker / Tasty / EasyRecipe / JSON-LD HowToStep), the page-break buffer trick, and why the hero is matted rather than full-bleed at the top.
