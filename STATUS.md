# Health check

Last checked: **2026-11-07**. Overall: **everything working** ✅

| Check | Result |
|---|---|
| Live site https://mayurisyarntales.online/ | ✅ 200 OK, serves the same `index.html` as `main` |
| `robots.txt`, `sitemap.xml` | ✅ 200 OK |
| Repo | ✅ `main` up to date with GitHub, no uncommitted changes |
| `bot/test_site_edit.py` | ✅ all passed |
| `bot/test_publish.py` | ✅ all passed (every photo has exactly one card) |
| Products | 81 products, 81 photos in `images/`, 51 marked "Just in" (the row shows the first 10) |
| Telegram bot (`@YarnTales_bot`, runs on the PC) | ✅ scheduled task "Mayuriz Telegram bot" running, last restart 19:39 |

## Notes

- The bot log shows a short internet outage at 15:30 (`No such host is known`).
  The bot came back on its own by 19:30.
- `gh` (GitHub CLI) isn't installed on the PC, so this check couldn't look at
  GitHub Actions runs. Check them on the repo's **Actions** tab if needed.

## How to re-run this check

```
git pull origin main
cd bot
py test_site_edit.py
py test_publish.py
```

Then open the live site at phone width and on desktop, and look at the end of
`%LOCALAPPDATA%\MayurizBot\bot.log` to see whether the bot is running.
