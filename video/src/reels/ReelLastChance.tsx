import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { zoomBlur } from "@remotion/transitions/zoom-blur";
import { linearBlur } from "@remotion/transitions/linear-blur";
import { pushCut } from "@remotion/transitions/push-cut";
import { COLORS, SANS_FONT } from "../theme";
import {
  CLAMP, CODE, CtaScene, DEEP, EASE_OUT, INK, Photo, Sounds, WARM_SOFT,
  cream, rise, type Crop, type Cue,
} from "./kit";
import { BEAT, DISPLAY, RoundBadge, SERIF, Ticker, pop, shake, whipPan } from "./fx";

/*
 * Reel 4 — "Don't miss this."
 *
 * The last-chance Reel, for the final days of the offer. Everything is cut
 * to a 120 BPM grid (a beat every 15 frames), so it lines up with most
 * trending tracks dropped on top in Instagram. It's built to be impossible
 * to scroll past: slam text, a colour-pop montage, a calendar running out,
 * a stamp.
 */

const HOOK = 5 * BEAT;          // DON'T / MISS / THIS.
const SHOT = 8;                 // one montage photo, roughly half a beat
const MONTAGE_SHOTS = 12;
const MONTAGE = SHOT * MONTAGE_SHOTS;
const MOSAIC = 7 * BEAT;
const CALENDAR = 7 * BEAT;
const STAMP = 11 * BEAT;
const CTA = 8 * BEAT;

const CROPS = {
  ocean: { file: "ocean-blue-scrunchie.jpg", focus: "48% 33%", zoom: 1.35 },
  bouquet: { file: "rose-bouquet.jpg", focus: "30% 74%", zoom: 1.25 },
  daisy: { file: "daisy-hanging-charm.jpg", focus: "52% 68%", zoom: 1.7 },
  claw: { file: "pink-bloom-claw-clip.jpg", focus: "70% 58%", zoom: 2.2 },
  sunflower: { file: "golden-sunflower.jpg", focus: "50% 55%", zoom: 1.12 },
  bag: { file: "ruby-bow-handbag.jpg", focus: "46% 54%", zoom: 1.8 },
  caramelBow: { file: "caramel-cream-bow.jpg", focus: "47% 100%", zoom: 1.6 },
  redRose: { file: "red-rose-stem.jpg", focus: "52% 42%", zoom: 1.4 },
  tricolour: { file: "tricolour-scrunchie.jpg", focus: "50% 74%", zoom: 1.6 },
  sunKeychain: { file: "sunflower-keychain.jpg", focus: "47% 58%", zoom: 1.7 },
  hearts: { file: "mini-hearts-set.jpg", focus: "32% 55%", zoom: 1.5 },
  blueBlossom: { file: "blue-blossom-scrunchie.jpg", focus: "56% 56%", zoom: 1.5 },
  rubyScrunchie: { file: "ruby-rose-scrunchie.jpg", focus: "50% 42%", zoom: 1.3 },
} satisfies Record<string, Crop>;

// --------------------------------------------------------------------------
// 1 · DON'T / MISS / THIS. — one word per beat, each one a hit
// --------------------------------------------------------------------------
const HITS = [0, BEAT, 2 * BEAT];

const Slam: React.FC = () => {
  const frame = useCurrentFrame();
  const words = ["DON'T", "MISS", "THIS."];
  return (
    <AbsoluteFill style={{ background: INK, translate: shake(frame, HITS, 26), overflow: "hidden" }}>
      <AbsoluteFill style={{ background: `radial-gradient(70% 45% at 50% 50%, rgba(200,86,74,.35), rgba(0,0,0,0) 70%)`,
        opacity: rise(frame, 2 * BEAT, 8) }} />
      {words.map((w, i) => {
        const at = HITS[i];
        const s = interpolate(frame, [at, at + 5], [2.4, 1], { ...CLAMP, easing: EASE_OUT });
        return (
          <div key={w} style={{
            position: "absolute", left: 0, right: 0, top: 470 + i * 300, textAlign: "center",
            fontFamily: DISPLAY, fontSize: 300, lineHeight: 1, letterSpacing: "0.01em",
            color: i === 2 ? COLORS.accent : "#fff8f0",
            opacity: frame >= at ? 1 : 0, scale: s,
            textShadow: i === 2 ? "0 0 60px rgba(200,86,74,.6)" : undefined,
          }}>{w}</div>
        );
      })}
      <div style={{ position: "absolute", left: 0, right: 0, top: 1400, textAlign: "center", fontFamily: SANS_FONT,
        fontWeight: 700, fontSize: 38, letterSpacing: "0.22em", color: COLORS.pollen,
        opacity: rise(frame, 3 * BEAT, 8) }}>LAUNCH WEEK ENDS SUNDAY</div>
    </AbsoluteFill>
  );
};

// --------------------------------------------------------------------------
// 2 · Colour-pop montage — a new piece and a new colour every half beat
// --------------------------------------------------------------------------
const MONTAGE_PHOTOS: Crop[] = [
  CROPS.ocean, CROPS.bouquet, CROPS.daisy, CROPS.claw, CROPS.sunflower, CROPS.caramelBow,
  CROPS.redRose, CROPS.tricolour, CROPS.sunKeychain, CROPS.hearts, CROPS.blueBlossom, CROPS.bag,
];
const POPS = [COLORS.accent, COLORS.pollen, COLORS.petalLight, COLORS.leaf, "#2e1f1b", COLORS.petalDark];
const WORDS = ["HANDMADE.", "MADE TO ORDER.", "ANY COLOUR."];

const Montage: React.FC = () => {
  const frame = useCurrentFrame();
  const i = Math.min(MONTAGE_SHOTS - 1, Math.floor(frame / SHOT));
  const local = frame - i * SHOT;
  const bg = POPS[i % POPS.length];
  const dark = bg === "#2e1f1b" || bg === COLORS.accent || bg === COLORS.leaf;
  const word = WORDS[Math.min(WORDS.length - 1, Math.floor(frame / (2 * BEAT)))];
  const punch = interpolate(local, [0, SHOT], [1.1, 1], { ...CLAMP, easing: EASE_OUT });
  const tilt = (i % 2 === 0 ? -1 : 1) * (2 + (i % 3));
  return (
    <AbsoluteFill style={{ background: bg }}>
      <div style={{ position: "absolute", left: 100, top: 270, width: 880, height: 960, borderRadius: 34,
        overflow: "hidden", border: "12px solid #fffdf9", boxShadow: "0 36px 70px rgba(0,0,0,.3)",
        rotate: `${tilt}deg`, scale: punch }}>
        <Photo crop={MONTAGE_PHOTOS[i]} />
      </div>
      <AbsoluteFill style={{ background: "#fff", opacity: interpolate(local, [0, 3], [0.55, 0], CLAMP) }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 1290, textAlign: "center", fontFamily: DISPLAY,
        fontSize: 132, lineHeight: 1, color: dark ? "#fff8f0" : INK, letterSpacing: "0.01em" }}>{word}</div>
    </AbsoluteFill>
  );
};

// --------------------------------------------------------------------------
// 3 · Four tiles flip in on the beat around a turning badge
// --------------------------------------------------------------------------
const TILES: Crop[] = [CROPS.claw, CROPS.rubyScrunchie, CROPS.hearts, CROPS.tricolour];

const Mosaic: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={cream}>
      {TILES.map((crop, i) => {
        const at = Math.round(i * BEAT / 2);
        const p = interpolate(frame, [at, at + 10], [0, 1], { ...CLAMP, easing: EASE_OUT });
        const col = i % 2;
        const row = Math.floor(i / 2);
        return (
          <div key={crop.file} style={{ position: "absolute", left: 80 + col * 470, top: 250 + row * 545,
            width: 450, height: 525, perspective: 1400 }}>
            <div style={{ width: "100%", height: "100%", borderRadius: 26, overflow: "hidden",
              boxShadow: "0 22px 48px rgba(46,31,27,.22)",
              transform: `rotateY(${(1 - p) * (col ? -95 : 95)}deg)`, opacity: p > 0 ? 1 : 0 }}>
              <Photo crop={crop} push={[1, 1.08]} durationInFrames={MOSAIC} />
            </div>
          </div>
        );
      })}
      <div style={{ position: "absolute", left: 540 - 150, top: 250 + 525 + 10 - 150 }}>
        <RoundBadge start={2 * BEAT} size={300} bg={COLORS.accent} color="#fff8f0"
          text="100% HANDMADE • MADE TO ORDER • "
          center={<div style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 700, fontSize: 64,
            color: "#fff8f0", lineHeight: 1 }}>by hand</div>} />
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 1345, textAlign: "center", fontFamily: SERIF,
        fontWeight: 600, fontSize: 66, color: INK, opacity: rise(frame, 3 * BEAT, 12) }}>
        Every piece, <i style={{ color: COLORS.accent }}>one at a time.</i>
      </div>
    </AbsoluteFill>
  );
};

// --------------------------------------------------------------------------
// 4 · The calendar runs out: Thu, Fri, Sat struck off, Sunday circled
// --------------------------------------------------------------------------
const DAYS = [["THU", "8"], ["FRI", "9"], ["SAT", "10"], ["SUN", "11"]];

const Calendar: React.FC = () => {
  const frame = useCurrentFrame();
  const circle = interpolate(frame, [4 * BEAT, 4 * BEAT + 14], [0, 1], { ...CLAMP, easing: EASE_OUT });
  return (
    <AbsoluteFill style={cream}>
      <div style={{ position: "absolute", top: 330, left: 0, right: 0, textAlign: "center", fontFamily: DISPLAY,
        fontSize: 104, color: INK, opacity: rise(frame, 0, 8) }}>THE OFFER ENDS</div>
      {DAYS.map(([d, n], i) => {
        const at = Math.round(i * BEAT / 3);
        const p = pop(frame, at, 12);
        const strikeAt = BEAT + i * BEAT;
        const strike = i < 3 ? interpolate(frame, [strikeAt, strikeAt + 6], [0, 1], CLAMP) : 0;
        const sunday = i === 3;
        return (
          <div key={d} style={{ position: "absolute", left: 75 + i * 240, top: 540, width: 210, height: 270,
            perspective: 900 }}>
            <div style={{ width: "100%", height: "100%", borderRadius: 24, background: "#fffdf9",
              boxShadow: "0 18px 40px rgba(46,31,27,.16)", overflow: "hidden",
              transform: `rotateX(${(1 - Math.min(1, p)) * 90}deg)`, transformOrigin: "50% 0%",
              scale: sunday ? 1 + circle * 0.08 : 1, opacity: sunday ? 1 : 1 - strike * 0.45 }}>
              <div style={{ background: sunday ? COLORS.accent : WARM_SOFT, color: "#fff", fontFamily: SANS_FONT,
                fontWeight: 800, fontSize: 38, letterSpacing: "0.12em", textAlign: "center", padding: "12px 0" }}>{d}</div>
              <div style={{ fontFamily: DISPLAY, fontSize: 130, color: INK, textAlign: "center", lineHeight: 1.35 }}>{n}</div>
            </div>
            {i < 3 ? (
              <svg viewBox="0 0 210 270" width={210} height={270} style={{ position: "absolute", inset: 0 }}>
                <path d="M 24 236 L 186 40" stroke={COLORS.accent} strokeWidth={14} strokeLinecap="round"
                  pathLength={1} strokeDasharray={1} strokeDashoffset={1 - strike} fill="none" />
              </svg>
            ) : (
              <svg viewBox="0 0 300 360" width={300} height={360} style={{ position: "absolute", left: -45, top: -45 }}>
                <path d="M 150 18 C 260 14, 292 120, 285 190 C 276 290, 210 345, 140 340 C 50 334, 12 260, 14 180 C 16 90, 70 26, 168 30"
                  stroke={COLORS.accent} strokeWidth={10} strokeLinecap="round" fill="none"
                  pathLength={1} strokeDasharray={1} strokeDashoffset={1 - circle} />
              </svg>
            )}
          </div>
        );
      })}
      <div style={{ position: "absolute", top: 930, left: 0, right: 0, textAlign: "center", fontFamily: SERIF,
        fontStyle: "italic", fontWeight: 700, fontSize: 190, color: COLORS.accent, lineHeight: 1,
        opacity: rise(frame, 4 * BEAT + 6, 10), scale: interpolate(rise(frame, 4 * BEAT + 6, 14), [0, 1], [0.85, 1]) }}>
        Sunday.
      </div>
      <div style={{ position: "absolute", top: 1170, left: 0, right: 0, textAlign: "center", fontFamily: SANS_FONT,
        fontWeight: 600, fontSize: 44, color: WARM_SOFT, opacity: rise(frame, 5 * BEAT + 6, 12) }}>
        Then it&rsquo;s gone.
      </div>
    </AbsoluteFill>
  );
};

// --------------------------------------------------------------------------
// 5 · The stamp — 20% slams down between two running tickers
// --------------------------------------------------------------------------
const STAMP_HIT = 10;

const Stamp: React.FC = () => {
  const frame = useCurrentFrame();
  const s = interpolate(frame, [STAMP_HIT - 6, STAMP_HIT], [2.6, 1], { ...CLAMP, easing: EASE_OUT });
  const code = rise(frame, 3 * BEAT, 14);
  return (
    <AbsoluteFill style={{ background: `radial-gradient(90% 60% at 50% 45%, #d8665a, ${COLORS.accent} 60%, #a9433a)`,
      overflow: "hidden" }}>
      <Ticker text="20% OFF  •  CODE LAUNCH20  •  ENDS SUNDAY" y={260} rotate={-5} bg={COLORS.pollen}
        color={INK} size={62} speed={7} />
      <Ticker text="HANDMADE  •  MADE TO ORDER  •  ANY COLOUR" y={1420} rotate={4} bg="#fff8f0"
        color={COLORS.accent} size={58} speed={-6} start={6} />
      <div style={{ position: "absolute", inset: 0, translate: shake(frame, [STAMP_HIT], 24) }}>
        <div style={{ position: "absolute", left: 0, right: 0, top: 470, textAlign: "center", opacity: frame >= STAMP_HIT - 6 ? 1 : 0,
          scale: s, rotate: "-6deg" }}>
          <div style={{ display: "inline-block", border: "14px solid #fff8f0", borderRadius: 40, padding: "10px 60px 30px",
            color: "#fff8f0", fontFamily: DISPLAY, lineHeight: 0.95, boxShadow: "0 0 0 8px rgba(255,248,240,.25)" }}>
            <div style={{ fontSize: 330 }}>20%</div>
            <div style={{ fontSize: 150, letterSpacing: "0.04em" }}>OFF</div>
          </div>
        </div>
        <div style={{ position: "absolute", right: 70, top: 380 }}>
          <RoundBadge start={STAMP_HIT + 8} size={230} bg={COLORS.pollen} color={INK}
            text="EVERYTHING • EVERYTHING • "
            center={<div style={{ fontFamily: DISPLAY, fontSize: 70, color: INK }}>ALL</div>} />
        </div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 1110, textAlign: "center", opacity: code,
        translate: `0px ${(1 - code) * 40}px`, fontFamily: SANS_FONT, color: "#fff8f0" }}>
        <div style={{ fontSize: 34, fontWeight: 600 }}>Mention this code when you order</div>
        <div style={{ display: "inline-block", marginTop: 16, background: "#fff", color: INK,
          fontFamily: "ui-monospace, Menlo, monospace", fontWeight: 800, fontSize: 72, letterSpacing: "0.08em",
          padding: "8px 36px", borderRadius: 18, border: `4px dashed ${DEEP}` }}>{CODE}</div>
      </div>
    </AbsoluteFill>
  );
};

// --------------------------------------------------------------------------
// Assembly
// --------------------------------------------------------------------------
const SCENES: { len: number; node: React.ReactNode; out?: unknown; t?: number }[] = [
  { len: HOOK, node: <Slam />, out: whipPan("left"), t: 10 },
  { len: MONTAGE, node: <Montage />, out: zoomBlur({}), t: 14 },
  { len: MOSAIC, node: <Mosaic />, out: whipPan("up"), t: 10 },
  { len: CALENDAR, node: <Calendar />, out: pushCut({ flashColor: "#ffffff", flashOpacity: 0.9, flashFrames: 4 }), t: 10 },
  { len: STAMP, node: <Stamp />, out: linearBlur({}), t: 14 },
  { len: CTA, node: <CtaScene /> },
];

const STARTS = SCENES.reduce<number[]>((acc, _s, i) => {
  acc.push(i === 0 ? 0 : acc[i - 1] + SCENES[i - 1].len - (SCENES[i - 1].t ?? 0));
  return acc;
}, []);

export const LAST_CHANCE_DURATION = STARTS[STARTS.length - 1] + SCENES[SCENES.length - 1].len;

const [, MONTAGE_AT, MOSAIC_AT, CALENDAR_AT, STAMP_AT, CTA_AT] = STARTS;

const CUES: Cue[] = [
  ...HITS.map((at) => ({ at, sound: "impact" as const, volume: 0.55 })),
  { at: MONTAGE_AT - 8, sound: "whip", volume: 0.5 },
  ...Array.from({ length: MONTAGE_SHOTS }, (_, i) => ({ at: MONTAGE_AT + i * SHOT, sound: "shutter" as const, volume: 0.28 })),
  { at: MOSAIC_AT - 6, sound: "whoosh", volume: 0.4 },
  ...[0, 1, 2, 3].map((i) => ({ at: MOSAIC_AT + Math.round(i * BEAT / 2), sound: "pop" as const, volume: 0.3 })),
  { at: CALENDAR_AT - 8, sound: "whip", volume: 0.5 },
  ...[1, 2, 3].map((i) => ({ at: CALENDAR_AT + i * BEAT, sound: "pop" as const, volume: 0.35 })),
  { at: CALENDAR_AT + 4 * BEAT, sound: "ding", volume: 0.35 },
  { at: STAMP_AT - 36, sound: "riser", volume: 0.4 },
  { at: STAMP_AT + STAMP_HIT, sound: "impact", volume: 0.6 },
  { at: STAMP_AT + 3 * BEAT, sound: "pop", volume: 0.35 },
  { at: CTA_AT - 6, sound: "whoosh", volume: 0.3 },
];

export const ReelLastChance: React.FC = () => {
  const timeline: React.ReactNode[] = [];
  SCENES.forEach((s, i) => {
    timeline.push(
      <TransitionSeries.Sequence key={`s${i}`} durationInFrames={s.len} premountFor={30}>
        {s.node}
      </TransitionSeries.Sequence>,
    );
    if (s.out) {
      timeline.push(
        <TransitionSeries.Transition key={`t${i}`} presentation={s.out as never}
          timing={linearTiming({ durationInFrames: s.t ?? 12 })} />,
      );
    }
  });
  return (
    <AbsoluteFill style={{ background: INK }}>
      <TransitionSeries>{timeline}</TransitionSeries>
      <Sounds cues={CUES} />
    </AbsoluteFill>
  );
};
