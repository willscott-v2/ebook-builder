# Design notes & gotchas

Hard-won lessons baked into the scripts. Read this when something looks wrong.

## Recipe extraction

Recipe sites store the recipe in one of several ways. `extract_recipe.py` tries them in order; if a page returns empty `ingredients`/`steps`, identify its method and add the selector.

- **JSON-LD `Recipe`** (best): `recipeIngredient[]` and `recipeInstructions[]`. Instructions can be plain strings, `HowToStep` objects (`.text`), or `HowToSection` containing `itemListElement` — the extractor flattens all three.
- **WP Recipe Maker**: ingredients in `class="wprm-recipe-ingredient"`, steps in `class="wprm-recipe-instruction-text"`.
- **Tasty Recipes**: `class="tasty-recipes-ingredients"` / `tasty-recipes-instructions` wrappers with `<li>`.
- **EasyRecipe** (common on older WordPress magazine sites): plain `class="ingredient"` and `class="instruction"` on `<li>`. Easy to miss because the class names are generic — recipes look "missing" until you match these.
- **Microdata**: `itemprop="recipeIngredient"`.

To diagnose a stubborn page: `curl -s -A "Mozilla/5.0" URL | grep -oiE 'class="[^"]*(ingredient|instruction|recipe)[^"]*"' | sort | uniq -c`.

## Hero images — avoid the social share card

`og:image` is frequently a **generic branded share card**, not the dish photo (tell-tale: every recipe on the site has the same `og:image` file size, or it contains "share"/"web"/the logo). `extract_recipe.py` prefers, in order: the JSON-LD recipe `image`, then a real `wp-content/uploads/YYYY/MM/` photo over ~40 KB, and only falls back to `og:image` last. It also skips files matching `logo|icon|cropped|-NNxNN|placeholder|webimage|share`. If a hero still comes through wrong, grab the real content `<img>` URL by hand and drop it into `config.json` (a data URI or a plain URL both work).

Images are **base64-embedded** into the HTML so the file is self-contained — no hosting, prints with photos, emails cleanly.

## Page layout (in build_ebook.py CSS)

- **Cream page canvas, full bleed.** `html{background:<cream>}` so continuation pages and any uncovered area match instead of showing white. Keep `@page{margin:0}` — do **not** use named `@page` margins (e.g. `@page recipe{margin:.5in 0}`), because Chromium does **not** paint the root background into a named page's margin boxes, so those strips print **white** at the top and bottom of recipe pages. That was a real bug.
- **Clean page breaks via `box-decoration-break: clone`.** The recipe body panel uses `-webkit-box-decoration-break:clone; box-decoration-break:clone` with its own padding (~`.42in` top, `.45in` bottom) and cream background. When a long recipe flows to a second page, the clone repeats that padding and background on **each** page fragment, so the last line on page one keeps a buffer below it and the first line on page two keeps one above — and the cream fills full-bleed. This replaces the @page-margin approach and avoids the white stripes.
- **Hero bleeds full to the top edge.** With `@page{margin:0}` and no negative margins, the recipe hero sits at the very top of its page (page-break-before starts a fresh page). Don't use a negative `margin-top` to force a bleed — it *leaks the next recipe's hero onto the previous page* at a break. The clone-padding approach gives the break buffer without any negative margin, so the hero bleeds cleanly and nothing leaks.
- **Ingredients** are a two-column list; **method** is a single column with numbered circles. Both use `break-inside:avoid` so an item never splits across pages.
- **Long recipes flow naturally** to a second page (no fixed page height on `.rpage`); short recipes end and the cream canvas fills the rest.

## PDF

`make_pdf.py` detects Playwright → headless Chrome → wkhtmltopdf. With none installed it prints browser Print-to-PDF steps (Letter, margins None/Default, Background graphics ON), which reproduces the design exactly because the size/margins live in the CSS.

## Voice

Don't impose a generic cookbook tone. Read 2–3 of the source articles and match their cadence and vocabulary in the intro and closing. The closing is a subscribe CTA — one card per contributing title.
