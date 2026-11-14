# Auto-posting to Facebook and Instagram (n8n)

n8n runs on the shop PC and posts every **new piece** on the live site to the
Facebook Page *Mayuri's Yarn Tales* (and Instagram, once linked).

## What it does

Every 15 minutes `shop-autopost.json` reads the `PRODUCTS` list on
https://mayurisyarntales.online/ and, for each piece it hasn't seen before:

1. skips it while it is still called "New Piece" or has a `MZ-NEW-…` code;
2. waits **30 minutes** after first spotting it (time for `/rename`, `/caption`);
3. posts the photo + name + description to Facebook (and Instagram if `META_IG_ID` is set);
4. sends "📣 Posted: …" or "⚠️ Couldn't post …" to the team Telegram group.

At most 3 pieces per run; a failing piece is retried 3 times, and nothing is
ever posted twice. On its very first run it only records the pieces already in
the shop, so old pieces are never posted.

## Where things live

| What | Where |
|---|---|
| n8n itself | `E:\dev\n8n` (`npm install n8n`), run with portable Node 24 in `E:\dev\node24` |
| Meta keys (never commit) | `%USERPROFILE%\.mayuriz\meta.env` |
| Telegram token (never commit) | `%USERPROFILE%\.mayuriz\bot.env` |
| n8n data (workflow, what's been posted) | `%USERPROFILE%\.n8n` |
| Log | `%LOCALAPPDATA%\MayurizN8n\n8n.log` |
| Editor | http://localhost:5678 (create the owner account on first visit) |

## Commands

```
node tools/meta-setup.mjs          # after putting a fresh Explorer token in meta.env
pwsh tools/install-n8n.ps1         # start at every logon (scheduled task) and start now
pwsh tools/install-n8n.ps1 -Remove # stop and remove
pwsh tools/run-n8n.ps1 -Import     # re-import shop-autopost.json after editing it
```

## Meta keys

`meta.env` holds `META_APP_ID`, `META_APP_SECRET`, `META_USER_TOKEN` (from Graph
API Explorer, app "Mayuriz Poster", Development mode) and, written by
`meta-setup.mjs`, `META_PAGE_ID`, `META_PAGE_TOKEN` (never expires) and `META_IG_ID`.

To add Instagram: give the app the `instagram_basic` and
`instagram_content_publish` permissions, generate a new Explorer token with
the Instagram account ticked, paste it as `META_USER_TOKEN`, run
`node tools/meta-setup.mjs`, then restart the task
(`pwsh tools/install-n8n.ps1`).
