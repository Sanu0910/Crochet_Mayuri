# Launch week — 7 to 11 October 2026

Posters for the website launch offer (20% off everything, code LAUNCH20).

This branch exists only so the Telegram sender can post these images.
GitHub Pages builds the website from `claude/website-mobile-redesign-xfmicu`,
so nothing here ever appears on the site. Don't merge it.

## Reels

| | |
|---|---|
| `reels/Mayuriz-Reel-1-Launch.mp4` | 22 s · "Our little shop is now online" → six pieces → offer → link |
| `reels/Mayuriz-Reel-2-Something-For-Everyone.mp4` | 28 s · one continuous zoom through the range → offer → link |
| `reels/*-Cover.jpg` | cover frames, laid out for the 4:5 profile grid |

Source: `video/src/reels/` (compositions `ReelLaunch` and `ReelRange` in the
`LaunchWeekReels` folder of Remotion Studio). Re-render with

```bash
cd video
npx remotion render src/index.ts ReelLaunch out/ReelLaunch.mp4 --crf=18
npx remotion render src/index.ts ReelRange  out/ReelRange.mp4  --crf=18
```

The sound effects in `video/public/sfx/` are synthesised, so they carry no
licence. Add the music in Instagram itself, since its library is licensed for Reels.
