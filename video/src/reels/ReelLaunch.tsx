import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { TransitionSeries, springTiming } from "@remotion/transitions";
import { SANS_FONT, SCRIPT_FONT, COLORS } from "../theme";
import {
  CLAMP, CtaScene, Cue, DEEP, EASE_OUT, FPS, Flower, INK, OfferScene, Photo, Sounds,
  WARM_SOFT, cream, rise, zoomThrough, type Crop,
} from "./kit";

/*
 * Reel 1 — "We're online."
 *
 *   0.0s  hook: the shop is now online — words land one by one
 *   2.5s  six pieces, each pushing through into the next
 *  11.0s  why: made by hand, made to order, in any colour
 *  13.6s  the offer: 20% off everything, till Sunday, code LAUNCH20
 *  18.7s  where: the domain, link in bio
 *
 * The first and last frames are the same cream, so when Instagram loops the
 * Reel the restart is seamless — a loop that doesn't jar gets rewatched.
 */

const HOOK = 75;
const PRODUCT = 54;
const VALUES = 90;
const OFFER = 165;
const CTA = 120;
const T = 12; // every transition

type Piece = { crop: Crop; tag: string; name: string; detail: string; sticker?: string };

const PIECES: Piece[] = [
  { crop: { file: "ruby-bow-handbag.jpg", focus: "46% 54%", zoom: 1.8 }, tag: "NEW IN BAGS",
    name: "The Ruby Bag", detail: "A zip that really closes.", sticker: "new!" },
  { crop: { file: "rose-bouquet.jpg", focus: "30% 74%", zoom: 1.25 }, tag: "ROSES",
    name: "Red Rose Bouquet", detail: "Five roses that never wilt." },
  { crop: { file: "ocean-blue-scrunchie.jpg", focus: "48% 33%", zoom: 1.35 }, tag: "SCRUNCHIES",
    name: "Ocean Blue Scrunchie", detail: "Soft ruffles, in any colour." },
  { crop: { file: "daisy-hanging-charm.jpg", focus: "52% 68%", zoom: 1.7 }, tag: "CHARMS",
    name: "Daisy Hanging Charm", detail: "Made to hang where you'll see it." },
  { crop: { file: "pink-bloom-claw-clip.jpg", focus: "70% 58%", zoom: 2.2 }, tag: "CLAW CLIPS",
    name: "Pink Bloom Claw Clip", detail: "A whole bloom, holding your hair." },
  { crop: { file: "golden-sunflower.jpg", focus: "50% 55%", zoom: 1.12 }, tag: "FLOWERS",
    name: "Golden Sunflower", detail: "A little sunshine, made by hand." },
];

// ------------------------------------------------------------------ hook
const Word: React.FC<{ at: number; children: React.ReactNode; style?: React.CSSProperties }> = ({
  at, children, style,
}) => {
  const frame = useCurrentFrame();
  const p = rise(frame, at, 9);
  return (
    <span style={{ display: "inline-block", opacity: p, marginRight: "0.22em",
      translate: `0px ${interpolate(p, [0, 1], [42, 0])}px`,
      scale: interpolate(p, [0, 1], [0.9, 1]), ...style }}>
      {children}
    </span>
  );
};

const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const pulse = 1 + 0.25 * Math.max(0, Math.sin((frame - 36) / 5));
  return (
    <AbsoluteFill style={cream}>
      <svg viewBox="0 0 1080 1920" style={{ position: "absolute", inset: 0 }}>
        <path d="M -40 1260 C 200 1150, 420 1380, 640 1270 S 980 1120, 1120 1200" fill="none"
          stroke={COLORS.accent} strokeWidth={5} strokeLinecap="round" opacity={0.35}
          pathLength={1} strokeDasharray={1}
          style={{ strokeDashoffset: interpolate(frame, [0, 34], [1, 0], { ...CLAMP, easing: EASE_OUT }) }} />
      </svg>
      <div style={{ position: "absolute", top: 300, left: 0, right: 0, display: "flex", justifyContent: "center",
        alignItems: "center", gap: 14, opacity: rise(frame, 0, 10) }}>
        <Flower size={60} />
        <span style={{ fontFamily: SCRIPT_FONT, fontWeight: 700, fontSize: 76, lineHeight: 1 }}>Mayuri&rsquo;z</span>
      </div>
      <div style={{ position: "absolute", top: 620, left: 70, right: 70, textAlign: "center",
        fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1.04, fontSize: 116 }}>
        <div><Word at={6}>Our</Word><Word at={11}>little</Word><Word at={16}>shop</Word></div>
        <div><Word at={23}>is</Word><Word at={28}>now</Word></div>
        <div style={{ marginTop: 10 }}>
          <Word at={36} style={{ fontSize: 236, fontWeight: 900, color: COLORS.accent, letterSpacing: "-0.06em", marginRight: 0 }}>
            online.
          </Word>
        </div>
      </div>
      <div style={{ position: "absolute", top: 1188, left: 0, right: 0, display: "flex", justifyContent: "center",
        opacity: rise(frame, 44, 10) }}>
        <span style={{ display: "inline-flex", alignItems: "center", gap: 14, background: INK, color: "#fff",
          fontSize: 28, fontWeight: 700, letterSpacing: "0.18em", padding: "16px 28px", borderRadius: 999 }}>
          <span style={{ width: 16, height: 16, borderRadius: 999, background: "#5fd38d",
            boxShadow: "0 0 0 8px rgba(95,211,141,.25)", scale: pulse }} />
          NOW LIVE
        </span>
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ one piece
const PieceScene: React.FC<{ piece: Piece; index: number }> = ({ piece, index }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={cream}>
      <div style={{ position: "absolute", top: 262, right: 110, fontSize: 26, fontWeight: 600,
        letterSpacing: "0.16em", color: WARM_SOFT, opacity: rise(frame, 2, 10) }}>
        0{index + 1} / 0{PIECES.length}
      </div>
      <div style={{ position: "absolute", left: 90, top: 316, width: 900, height: 940, borderRadius: 48,
        overflow: "hidden", border: "14px solid #fff", boxShadow: "0 30px 60px rgba(60,35,25,.22)" }}>
        <Photo crop={piece.crop} push={[1, 1.09]} durationInFrames={PRODUCT} />
      </div>
      {piece.sticker ? (
        // covers the label printed in the corner of the source graphic
        <div style={{ position: "absolute", left: 104, top: 1128, width: 210, height: 110, borderRadius: 18,
          background: "#f3d9d3", border: "5px solid #fff", rotate: "-9deg",
          boxShadow: "0 10px 22px rgba(60,35,25,.18)", display: "flex", alignItems: "center",
          justifyContent: "center", scale: interpolate(rise(frame, 4, 14), [0, 1], [0.6, 1]),
          opacity: rise(frame, 4, 8) }}>
          <span style={{ fontFamily: SCRIPT_FONT, fontWeight: 700, fontSize: 70, color: DEEP, lineHeight: 1 }}>
            {piece.sticker}
          </span>
        </div>
      ) : null}
      <div style={{ position: "absolute", top: 1292, left: 0, right: 0, textAlign: "center",
        fontSize: 26, fontWeight: 700, letterSpacing: "0.24em", color: COLORS.accent,
        opacity: rise(frame, 6, 10) }}>
        {piece.tag}
      </div>
      <div style={{ position: "absolute", top: 1332, left: 60, right: 60, textAlign: "center",
        fontSize: 76, fontWeight: 800, letterSpacing: "-0.035em", lineHeight: 1,
        opacity: rise(frame, 9, 10), translate: `0px ${interpolate(rise(frame, 9, 14), [0, 1], [26, 0])}px` }}>
        {piece.name}
      </div>
      <div style={{ position: "absolute", top: 1420, left: 0, right: 0, textAlign: "center",
        fontFamily: SCRIPT_FONT, fontWeight: 700, fontSize: 50, color: DEEP, lineHeight: 1,
        opacity: rise(frame, 14, 10) }}>
        {piece.detail}
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ why
const VALUE_LINES: [string, string, number][] = [
  ["Made by", "hand.", 4],
  ["Made to", "order.", 22],
  ["In any", "colour.", 40],
];

const Values: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={cream}>
      {VALUE_LINES.map(([plain, script, at], i) => {
        const p = rise(frame, at, 12);
        return (
          <div key={plain} style={{ position: "absolute", top: 560 + i * 210, left: 0, right: 0,
            textAlign: "center", opacity: p, translate: `${interpolate(p, [0, 1], [i % 2 ? 80 : -80, 0])}px 0px` }}>
            <span style={{ fontSize: 108, fontWeight: 800, letterSpacing: "-0.04em" }}>{plain} </span>
            <span style={{ fontFamily: SCRIPT_FONT, fontWeight: 700, fontSize: 136, color: COLORS.accent }}>{script}</span>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ timeline
const SCENES = [HOOK, ...PIECES.map(() => PRODUCT), VALUES, OFFER, CTA];
export const LAUNCH_DURATION = SCENES.reduce((a, b) => a + b, 0) - T * (SCENES.length - 1);

/** Frame each scene starts at, once the overlapping transitions are taken out. */
const starts = SCENES.map((_, i) => SCENES.slice(0, i).reduce((a, b) => a + b, 0) - T * i);

const CUES: Cue[] = [
  { at: 36, sound: "pop", volume: 0.5 },                                        // "online."
  ...starts.slice(1, 8).map((s) => ({ at: s - 3, sound: "whoosh" as const, volume: 0.32 })),
  ...VALUE_LINES.map(([, , at]) => ({ at: starts[7] + at, sound: "pop" as const, volume: 0.3 })),
  { at: starts[8] - 3, sound: "whoosh", volume: 0.4 },                          // into the red
  { at: starts[8] + 30, sound: "ding", volume: 0.55 },                          // 20% lands
  { at: starts[8] + 66, sound: "pop", volume: 0.45 },                           // the code
  { at: starts[9] - 3, sound: "whoosh", volume: 0.32 },
];

const cut = (key: string) => (
  <TransitionSeries.Transition key={key} presentation={zoomThrough()}
    timing={springTiming({ config: { damping: 200 }, durationInFrames: T })} />
);

// TransitionSeries wants a flat run of scene, transition, scene... so the
// list is built flat rather than nesting fragments inside it.
const timeline: React.ReactNode[] = [
  <TransitionSeries.Sequence key="hook" durationInFrames={HOOK} premountFor={FPS} name="Hook">
    <Hook />
  </TransitionSeries.Sequence>,
];
PIECES.forEach((piece, i) => {
  timeline.push(cut(`t-piece-${i}`));
  timeline.push(
    <TransitionSeries.Sequence key={piece.name} durationInFrames={PRODUCT} premountFor={FPS} name={piece.name}>
      <PieceScene piece={piece} index={i} />
    </TransitionSeries.Sequence>,
  );
});
timeline.push(
  cut("t-why"),
  <TransitionSeries.Sequence key="why" durationInFrames={VALUES} premountFor={FPS} name="Why">
    <Values />
  </TransitionSeries.Sequence>,
  cut("t-offer"),
  <TransitionSeries.Sequence key="offer" durationInFrames={OFFER} premountFor={FPS} name="Offer">
    <OfferScene />
  </TransitionSeries.Sequence>,
  cut("t-cta"),
  <TransitionSeries.Sequence key="cta" durationInFrames={CTA} premountFor={FPS} name="Where">
    <CtaScene />
  </TransitionSeries.Sequence>,
);

export const ReelLaunch: React.FC = () => (
  <AbsoluteFill style={{ background: "#f7f1e8", fontFamily: SANS_FONT }}>
    <TransitionSeries>{timeline}</TransitionSeries>
    <Sounds cues={CUES} />
  </AbsoluteFill>
);
