# Mayuri'z — handmade crochet shop website

Live at https://mayurisyarntales.online/ (GitHub Pages, custom domain via `CNAME`).
Owner: Sanu Roy. The maker is Mayuri. Plain static site: one `index.html`, photos
in `images/`, no build step.

## How changes go live

- **`main` is the live site.** Whatever lands on `main` is published by GitHub
  Pages within a minute or two.
- The Telegram bot (GitHub Actions, `.github/workflows/telegram-uploader.yml`)
  also commits uploads straight to `main`. **Always `git pull origin main`
  before starting and again before pushing.**
- Preview locally: `py -m http.server 8000` (Windows) or
  `python3 -m http.server 8000`, then open http://localhost:8000.
- After a change: check the page at phone width (390px) and desktop, then
  commit with a clear message and push to `main`.

## Products

All products live in the `PRODUCTS` array in `index.html`, between the
`/* PRODUCTS:START */` and `/* PRODUCTS:END */` markers. **Never remove or
rename those markers**: the bot edits between them. `video/src/theme.ts` holds a
matching list (same markers) for the promo film; keep both in step.

Each entry:

```js
{
  id: 'white-daisy-bookmark',          // url-safe, unique, never changes
  sku: 'MZ-BMK-002',                   // product code, see below
  name: 'White Daisy Bookmark',
  cat: 'bookmarks', tag: 'Bookmarks', badge: 'Just in', fresh: true,
  desc: 'One or two short, warm sentences.',
  image: 'images/white-daisy-bookmark.jpg'
},
```

- **New pieces go at the top** of the list with `badge: 'Just in', fresh: true`.
  The "Just in" row under the hero shows the first 10 `fresh` items.
- **One photo per product.** Use the photo exactly as given (no edits, no
  slideshows). Name the file after the product, lowercase-with-dashes.
- **No duplicates:** if two photos show the same piece, list it once.
- `cat` is the gallery filter key (must exist in the `CATEGORIES` list in
  `index.html`); `tag` is the type printed on the card ("shows under").
- Every photo in `images/` must have exactly one card; delete the photo when a
  product is removed. `bot/test_publish.py` checks this.

## Product codes (SKU)

`MZ-<group>-<number>`, e.g. `MZ-SCR-007`. The group comes from `tag`
(`GROUP_CODES` in `bot/catalogue.py`): SCR Scrunchies, BOW Bows, CLW Claw Clips,
HCL Hair Clips, HPN Hair Pins, HBD Hair Bands, ROS Roses, FLW Flowers,
GAR Garlands, KEY Keychains, CHM Charms, HRT Hearts, BMK Bookmarks,
CST Coasters, BNG Bangles, BAG Bags, NEW (no category yet).

- A new product gets the **next unused number in its group**. Codes never
  change and are never reused.
- A new kind of product needs: a `CATEGORIES` entry and an order-form
  `<option>` + `CATEGORY_MAP` entry in `index.html`, a `Category` and a
  `GROUP_CODES` entry (and a keyword) in `bot/catalogue.py`, and a row in
  `GROUPS` in `bot/price_list.py`.

## Prices and the price list

- Prices are **not on the site yet**. The plan: fill the price list, then add
  prices, a cart and Razorpay checkout.
- `py bot/price_list.py index.html <path outside the repo>.xlsx` builds the
  price list workbook from the site.
- **Never commit spreadsheets** (`*.xlsx` is in `.gitignore`). The repository
  is public and the filled sheet holds costs and profit.
- Mayuri'z is **not GST registered**: never add GST to prices or show a GSTIN.
- Razorpay's **secret key must never go in the website code**. It belongs in
  GitHub/Cloudflare secrets and is used only by a server-side function.

## Tests

```
cd bot
py test_site_edit.py
py test_publish.py
```

Both must print `all passed` before pushing changes to `bot/` or to the
`PRODUCTS` list.

## Also

- `CHANGELOG.md`: add a short dated entry, newest first, for visible changes.
- `bot/README.md`: how the Telegram bot works (captions, `#category`
  hashtags, `/rename`, `/caption`, `/remove`, `/film`).
- `SETUP.md`: domain DNS and EmailJS. Don't delete `CNAME`.
- `tools/setup-windows.ps1`: sets up a Windows PC to work on the site.
