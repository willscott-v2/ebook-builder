# config.json schema

The single input to `build_ebook.py`. Assemble it from the extractor output plus
the brand tokens and the copy you write. All colors are hex strings, all images
are data URIs or URLs.

> The example below uses a sample publication purely for illustration. Replace
> every value — title, brand names, colors, recipes, subscribe links — with your
> own. Nothing here is required to be a specific brand.

```json
{
  "title": "The Southern Tailgate",
  "subtitle": "Ten game-day dishes from four Southern kitchens",
  "kicker": "A Hoffman Media Collection",
  "footer": "Hoffman Media · Birmingham, Alabama",
  "cover_image": "data:image/jpeg;base64,...   (optional; defaults to first recipe image)",
  "contributors": ["Louisiana Cookin'", "Bake from Scratch", "Southern Cast Iron", "Taste of the South"],

  "brand": {
    "accent":  "#9C1B2E",   "_": "primary accent (badges, headings, step numbers)",
    "accent2": "#B0772F",   "_": "secondary accent (ingredient bullets)",
    "ink":     "#241F1C",
    "cream":   "#FBF6EE",
    "serif":   "Georgia, 'Times New Roman', serif",
    "sans":    "Arial, Helvetica, sans-serif"
  },

  "intro": {
    "heading": "Pull Up a Chair",
    "paragraphs": ["First paragraph (rendered larger/italic).", "Second.", "Third."]
  },

  "recipes": [
    {
      "name": "Boudin Balls",
      "brand": "Louisiana Cookin'",
      "course": "Appetizer",
      "headnote": "Acadiana's famous boudin, rolled and fried into a two-bite opener.",
      "image": "data:image/jpeg;base64,...",
      "ingredients": ["2 pounds pork shoulder, cubed", "..."],
      "steps": ["In a stockpot, cover pork shoulder with stock...", "..."],
      "accent": "#9C1B2E",            "_": "optional per-recipe accent; defaults to brand.accent",
      "source_label": "Originally published in Louisiana Cookin'"
    }
  ],

  "closing": {
    "heading": "Keep the Kitchen Full",
    "paragraphs": ["Subscribe CTA copy in the publication's voice.", "Second line."],
    "subscribe": [
      {"name": "Louisiana Cookin'",  "url": "louisianacookin.com/subscribe",        "color": "#9C1B2E"},
      {"name": "Bake from Scratch",  "url": "subscriptions.bakefromscratch.com",     "color": "#B0772F"}
    ]
  }
}
```

## Article-roundup item (non-recipe mode)
For a roundup, an item uses `body` and/or `points` instead of `ingredients`/`steps`:

```json
{
  "name": "How AI Search Is Changing Discovery",
  "brand": "The Visibility Report",
  "course": "Feature",
  "headnote": "A short deck or excerpt that sells the piece.",
  "image": "data:image/jpeg;base64,...",
  "body": ["First teaser paragraph.", "Second teaser paragraph."],
  "points": ["Optional bullet highlight", "Another key takeaway"],
  "url": "https://example.com/article",
  "accent": "#2D2A26"
}
```
The footer auto-reads "Read the full story in <brand>". Recipe items and article items can coexist in the same `recipes` array.

## Notes
- `recipes[]` comes straight from `extract_recipe.py`; you then set `course`, tidy `headnote`, set the display `brand` name (the extractor puts the host there), and assign `accent`/`color` per title.
- For a single-publication book, give every recipe the same `brand`/`accent` and use one subscribe card.
- `kicker`, `footer`, `subtitle`, `course`, `headnote`, `source_label`, `cover_image`, `accent` are all optional.
- Keep ingredient and step strings plain text (the extractor already strips HTML).
