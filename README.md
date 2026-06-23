# Ebook Builder — Quick Start

Turn a list of web links into a finished, designed ebook — a cover, an intro, one page
per item, and a closing "subscribe" page — as a single file you can email or print. It
matches the look and voice of a publication you choose.

**Built for recipes first** (each page shows the dish photo, ingredients, and method), and
it also handles **article roundups** (a "best of" collection of features or posts).

**You don't run any code yourself.** You hand this folder to Claude and tell it what you
want. Claude does the rest.

It's a [Claude](https://claude.com/claude-code) **skill** (works in Claude Code and the
Claude desktop/Cowork app). Everything runs on Python's standard library — no SEO tools,
no API keys, no web hosting.

## Install
```bash
# Claude Code
git clone https://github.com/willscott-v2/ebook-builder.git ~/.claude/skills/ebook-builder
```
For the desktop / Cowork app, download this repo and attach the folder to your project.

## What you need
- **A list of links** to the recipes (or articles) you want in the book — 5 to 15 works well.
- **The publication** they come from (name + website), so the book looks and reads like it.
- Optional: a title and theme (e.g. "Summer Cookout"), and the magazine's subscribe links.

You do **not** need any special software, an SEO tool, or anywhere to put files online.

## How to use it
1. Make sure this `recipe-ebook-builder` folder is available to Claude (in Claude Code,
   it lives in `~/.claude/skills/`; in the desktop/Cowork app, attach the folder to your
   project).
2. Just ask, in plain language. For example:

   > Build a recipe ebook called "Summer Cookout" from these links, in the style of
   > [Publication]: <paste your links>

3. Claude will:
   - read each link and pull the photo, ingredients, and steps,
   - match the publication's colors, fonts, and writing voice,
   - write a warm intro and a "subscribe" closing,
   - and produce **two files**: a self-contained **HTML** (opens and emails as-is) and a
     **PDF**.

That's it. If your computer can't make the PDF automatically, Claude will tell you the
one-step way to do it: open the HTML in any browser and choose Print → "Save as PDF."

## What you get
- **`<your-title>.html`** — the whole ebook in one file, photos included. Double-click to
  open; attach to an email; no website needed.
- **`<your-title>.pdf`** — the print/share-ready version.

## Two kinds of books
- **Recipes** (the default): each page shows the dish photo, ingredients, and method.
- **Article roundups**: a "best of" collection of features or posts — each page shows the
  photo, a short teaser, and a link to read the full piece. Just tell Claude it's an
  article roundup.

## Tips
- Pick links that already have a nice main photo; the builder uses each page's hero image.
- If a recipe page uses an unusual format and a couple of fields come up empty, Claude can
  fix it — just say which recipe looks off.
- Want a different cover photo, color, or title? Ask. It regenerates in seconds.
