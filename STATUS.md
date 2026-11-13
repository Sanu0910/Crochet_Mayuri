# Health check

Last checked: **2026-11-13**. Overall: **everything working** ✅

| Check | Result |
|---|---|
| Live site https://mayurisyarntales.online/ | ✅ 200 OK; `manifest.webmanifest`, `sw.js`, `sitemap.xml`, `robots.txt` 200 OK |
| Repo | ✅ `main` pulled from GitHub (bot had added 5 pieces) |
| `bot/test_site_edit.py` | ✅ all passed |
| `bot/test_publish.py` | ✅ all passed (every photo has exactly one card) |
| Products | 88 products, no duplicate codes, none left as "New" |
| Telegram bot (`@YarnTales_bot`, runs on the PC) | ✅ scheduled task running |
| Visitor count | ✅ new, in the footer (Abacus counter, key `mayurisyarntales/visits`) |

## Notes

- Five photos came in without a caption again and were named by hand.
  Tip: add a name and `#category` to the photo caption.
- The bot reused `MZ-NEW-001`/`002` (retired on 11-09), because it picks the
  next number from what's on the site. Harmless here (all five now have real
  codes), but retired codes aren't remembered anywhere yet.
- The bot log shows short daily GitHub/Telegram errors (502, timeouts,
  "unreachable network"), mostly around 06:42. It recovers on its own.

## How to re-run this check

```
git pull origin main
cd bot
py test_site_edit.py
py test_publish.py
```

Then open the live site at phone width and on desktop, and look at the end of
`%LOCALAPPDATA%\MayurizBot\bot.log` to see whether the bot is running.
