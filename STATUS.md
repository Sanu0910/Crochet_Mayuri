# Health check

Last checked: **2026-11-09**. Overall: **everything working** ✅

| Check | Result |
|---|---|
| Live site https://mayurisyarntales.online/ | ✅ 200 OK; `manifest.webmanifest`, `sw.js`, `sitemap.xml` 200 OK |
| Repo | ✅ `main` pulled from GitHub (bot had added 2 pieces) |
| `bot/test_site_edit.py` | ✅ all passed |
| `bot/test_publish.py` | ✅ all passed (every photo has exactly one card) |
| Products | 83 products, no duplicate codes |
| Telegram bot (`@YarnTales_bot`, runs on the PC) | ✅ running, restarted 23:29 and sent its report |
| Android app | ✅ APKs built 2026-11-08 (`app-arm64-v8a-release.apk` 16.9 MB) |

## Notes

- Two photos came in from Telegram without a caption ("New Piece", no
  category). They were named by hand: Daisy Key Ring and Flower Bookmarks.
  Tip: add a name and `#category` to the photo caption so this isn't needed.
- The bot log shows GitHub/Telegram errors (502, timeouts) around 18:25.
  The bot recovered on its own and was restarted at 23:29.

## How to re-run this check

```
git pull origin main
cd bot
py test_site_edit.py
py test_publish.py
```

Then open the live site at phone width and on desktop, and look at the end of
`%LOCALAPPDATA%\MayurizBot\bot.log` to see whether the bot is running.
