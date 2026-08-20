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
   npm run poster       # renders frame 572 — the rose bouquet card
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
