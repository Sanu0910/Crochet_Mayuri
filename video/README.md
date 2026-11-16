# The Mayuri'z film

The promo film on the website (`media/mayuriz-film.mp4`) is generated from
this [Remotion](https://remotion.dev) project, so it can be re-rendered
whenever the catalogue changes instead of being re-edited by hand.

It runs 27 seconds at 1080×1350 (4:5): a yarn-thread flower intro, the
"Handmade." headline, then all 18 pieces one photo at a time, and a closing
card with the order address.

## Re-rendering after adding or changing photos

1. Add the new photo to `../images/` and add its entry to the `PRODUCTS`
   array in `../index.html` (see `../SETUP.md`).
2. Add the same entry to the `PRODUCTS` list in `src/theme.ts` — the film
   deliberately keeps its own copy so the two can be sequenced differently.
3. Render:

   ```bash
   cd video
   npm install          # first time only
   npm run render       # copies photos in, then renders to out/promo.mp4
   ```

4. Strip the (silent) audio track Remotion adds and compress for the web:

   ```bash
   node_modules/@remotion/compositor-linux-x64-gnu/ffmpeg \
     -y -i out/promo.mp4 -an -c:v libx264 -profile:v high -crf 30 \
     -preset slow -pix_fmt yuv420p -movflags +faststart \
     ../media/mayuriz-film.mp4
   ```

5. Refresh the poster frame if you want a different one on the page:

   ```bash
   npm run poster       # frame is computed by poster-frame.mjs
   ```

   Then convert `out/promo-poster.png` to `../media/mayuriz-film-poster.jpg`.

   Pick a frame that sits **inside** a scene rather than in one of the
   10-frame cross-fades between them, or the poster comes out half-faded.

6. Update the duration and file size in the `.film-meta` line of
   `../index.html` if they changed.

## Previewing while editing

```bash
npm run dev
```

This opens Remotion Studio, where each scene (`Intro`, `Statement`,
`Product`, `Outro`) is registered as its own composition so it can be
scrubbed and timed on its own.

## Notes

- Fonts are checked in at `public/fonts/` rather than fetched from Google
  at render time, so the render works offline and can't change under you.
- Product photos are **not** checked in here — `npm run sync-assets` copies
  them from `../images/`.
- Rendering needs a Chrome/Chromium build. If Remotion can't find one, pass
  `--browser-executable=/path/to/chrome-headless-shell`.

## Weekly promo ads (9:16, with music)

Two vertical 1080×1920 ads a week, made by `tools/weekly_video.py`:

- **AdShowcase** (Video 1, midweek): one hero piece. A hook over a blurred
  macro, the product card whipping in on the music's drop, two close-ups,
  "handmade by Mayuri" lines, the full logo with the tagline, then the call to
  action with the website.
- **AdCreative** (Video 2, weekend): a fast gift edit. Kinetic hook words on
  the beat, up to 6 polaroid cards whipping in, a gift collage, the brand
  sting and a red call to action.
- **AdCover**: the Reel cover still.

The Python script does the planning. It picks the products (newest, never
featured before), picks a licence-approved track from `tools/video_music.json`,
finds its beats and drop, and snaps every scene to a beat. The components in
`src/ads/` only draw that plan, which arrives as `--props`. The script also
writes `content.md` for each week: storyboard, captions (Instagram, Facebook,
YouTube Shorts), hashtags, links and the schedule.

```powershell
# once: Python venv for the beat analysis
py -m venv $env:LOCALAPPDATA\MayurizVideo\venv
& $env:LOCALAPPDATA\MayurizVideo\venv\Scripts\python.exe -m pip install numpy pillow
winget install Gyan.FFmpeg          # full ffmpeg (Remotion's bundled one can't output raw audio)

# each week (or let tools/install-weekly-video.ps1 do it every Sunday)
& $env:LOCALAPPDATA\MayurizVideo\venv\Scripts\python.exe -X utf8 tools\weekly_video.py
#   --plan-only  plan + captions, no render   --week 2026-W48   --hero <id>   --products id,id,...
```

Output goes to `%USERPROFILE%\Videos\Mayuriz Weekly\<week>\`. Nothing is
posted automatically.

- **Music is never committed.** It lives in `%USERPROFILE%\Music\Copyright Free Music`.
  Only tracks under `approved` in `tools/video_music.json` are used, each with
  its CC BY credit line, which goes into every caption. A shop ad is commercial
  use, so "free for personal / non-monetised use" tracks are listed under `rejected`.
- **Photos that are finished posters** (text on the image) need a hand-set
  focus in `tools/video_focus.json`, so the close-ups land on the crochet and
  not the lettering.
- **This PC has 8 GB of RAM.** Renders use `--concurrency=2`, backdrops are
  pre-blurred and the grain is a static image. Live CSS blur on big photos
  crashed Chrome ("Page crashed!"). Run one render at a time.

## Daily product reel (9:16, posted)

`tools/daily_reel.py` makes one ~17 s reel a day with the same `AdShowcase`
composition: hook ("Handmade. Limited pieces."), the piece revealed on the
drop, a close-up with a scarcity line, the brand, then "Limited Pieces. Order
Yours!". One piece per day (newest first, each once before repeats, never the
same category twice running), a different approved showcase track each day.
If every quality check passes, `tools/post_video.py` posts it to Instagram and
Facebook at 18:00 IST and tells the team on Telegram.

```powershell
pwsh tools\install-daily-reel.ps1          # daily: render 16:45, post 18:00
& $env:LOCALAPPDATA\MayurizVideoenv\Scripts\python.exe -X utf8 tools\daily_reel.py --no-post   # test render
```

Selling words stay true: pieces are handmade and made to order, so only a few
get made. Never stock counts, prices or materials.
