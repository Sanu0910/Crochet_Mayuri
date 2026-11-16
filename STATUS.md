# Health check

Last checked: **2026-11-16**. Overall: **everything working** ✅

| Check | Result |
|---|---|
| Live site https://mayurisyarntales.online/ | ✅ 200 OK (0.4 s) |
| Repo | ✅ `main` pulled (bot had added 11 pieces) |
| `bot/test_site_edit.py` | ✅ all passed |
| `bot/test_publish.py` | ✅ all passed (every photo has exactly one card) |
| Products | 99 products, 99 unique codes, none left as "New" |
| Sitemap | ✅ valid, 2 pages + 99 product images (`bot/sitemap.py`, refreshed on every bot commit) |
| Daily reel | ✅ `Mayuriz daily reel` task installed; first reel posts 18:00 today |

## Notes

- 11 photos came in without a caption and were named by hand (10 flower hair
  ties, 1 gajra). Tip: add a name and `#category` to the photo caption.
- `new-piece-12` (Turquoise) and `new-piece-18` (Sky Blue) hair ties look
  alike; if they're the same piece, remove one with `/remove`.
- Owner step for SEO: submit `https://mayurisyarntales.online/sitemap.xml` in
  Google Search Console (Sitemaps).

## How to re-run this check

```
git pull origin main
cd bot
py test_site_edit.py
py test_publish.py
```

Then open the live site at phone width and on desktop, and look at the end of
`%LOCALAPPDATA%\MayurizBot\bot.log` to see whether the bot is running.
