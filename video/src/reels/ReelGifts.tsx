import React from "react";
import { AbsoluteFill, interpolate, random, useCurrentFrame } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { crossZoom } from "@remotion/transitions/cross-zoom";
import { filmBurn } from "@remotion/transitions/film-burn";
import { ripple } from "@remotion/transitions/ripple";
import { crosswarp } from "@remotion/transitions/crosswarp";
import { zoomBlur } from "@remotion/transitions/zoom-blur";
import { pushCut } from "@remotion/transitions/push-cut";
import { COLORS, SANS_FONT, SCRIPT_FONT } from "../theme";
import {
  CLAMP, CODE, CtaScene, DEEP, EASE_OUT, INK, Photo, Sounds, WARM_SOFT,
  cream, rise, type Crop, type Cue,
} from "./kit";
import { DISPLAY, MaskLine, Polaroid, SERIF, Sticker, lightLeak, pop, shake } from "./fx";

/*
 * Reel 3 — "Gifts they'll actually keep."
 *
 * A gift guide: one chapter per person on the viewer's list, so everyone
 * watching thinks of someone. Gift guides get saved and sent on, and those
 * are the two things Instagram rewards most. Each chapter hands over to the
 * next with a different cinematic transition, then the gift "opens" to
 * reveal the offer.
 */

const HOOK = 84;
const CHAPTER = 96;
const OFFER = 165;
const CTA = 110;
const T = 18;

const C = {
  bouquet: { file: "rose-bouquet.jpg", focus: "30% 74%", zoom: 1.25 },
  coralRose: { file: "coral-rose-stem.jpg", focus: "50% 42%", zoom: 1.7 },
  redRose: { file: "red-rose-stem.jpg", focus: "52% 40%", zoom: 1.45 },
  ocean: { file: "ocean-blue-scrunchie.jpg", focus: "48% 33%", zoom: 1.35 },
  rubyScrunchie: { file: "ruby-rose-scrunchie.jpg", focus: "50% 42%", zoom: 1.3 },
  tricolour: { file: "tricolour-scrunchie.jpg", focus: "50% 72%", zoom: 1.35 },
  sunflower: { file: "golden-sunflower.jpg", focus: "50% 55%", zoom: 1.12 },
  sunKeychain: { file: "sunflower-keychain.jpg", focus: "47% 58%", zoom: 1.7 },
  sunClips: { file: "sunflower-hair-clips.jpg", focus: "50% 74%", zoom: 1.6 },
  caramelBow: { file: "caramel-cream-bow.jpg", focus: "47% 100%", zoom: 1.6 },
  creamBow: { file: "cream-bow.jpg", focus: "49% 45%", zoom: 1.45 },
  maroonBow: { file: "classic-maroon-bow-alt.jpg", focus: "50% 35%", zoom: 1.8 },
  bag: { file: "ruby-bow-handbag.jpg", focus: "46% 54%", zoom: 1.8 },
  claw: { file: "pink-bloom-claw-clip.jpg", focus: "70% 58%", zoom: 2.2 },
  daisy: { file: "daisy-hanging-charm.jpg", focus: "52% 68%", zoom: 1.7 },
} satisfies Record<string, Crop>;

// --------------------------------------------------------------------------
// Hook
// --------------------------------------------------------------------------
const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const underline = interpolate(frame, [30, 46], [0, 1], { ...CLAMP, easing: EASE_OUT });
  return (
    <AbsoluteFill style={cream}>
      <Polaroid crop={C.redRose} start={0} x={50} y={235} w={330} rotate={-10} sceneLength={HOOK} />
      <Polaroid crop={C.claw} start={6} x={700} y={225} w={320} rotate={9} sceneLength={HOOK} />
      <Polaroid crop={C.daisy} start={12} x={60} y={1105} w={320} rotate={7} sceneLength={HOOK} />
      <Polaroid crop={C.ocean} start={18} x={690} y={1095} w={330} rotate={-8} sceneLength={HOOK} />
      <div style={{ position: "absolute", top: 650, left: 0, right: 0, textAlign: "center", color: INK }}>
        <MaskLine start={4} style={{ fontFamily: SANS_FONT, fontWeight: 800, fontSize: 30,
          letterSpacing: "0.3em", color: COLORS.accent }}>THE GIFT GUIDE</MaskLine>
        <MaskLine start={10} style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 132, lineHeight: 1.02,
          letterSpacing: "-0.02em", marginTop: 18 }}>Gifts they&rsquo;ll</MaskLine>
        <MaskLine start={16} style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 132, lineHeight: 1.02,
          letterSpacing: "-0.02em" }}>actually</MaskLine>
        <div style={{ position: "relative", display: "inline-block" }}>
          <MaskLine start={22} style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 700, fontSize: 176,
            lineHeight: 1, color: COLORS.accent, letterSpacing: "-0.03em" }}>keep.</MaskLine>
          <svg viewBox="0 0 400 40" width={400} height={40}
            style={{ position: "absolute", left: "50%", marginLeft: -200, bottom: -14 }}>
            <path d="M8 26 C 90 8, 210 6, 392 20" fill="none" stroke={COLORS.pollen} strokeWidth={10}
              strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - underline} />
          </svg>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// --------------------------------------------------------------------------
// A chapter: a big outlined number behind the picture, then who it's for.
// --------------------------------------------------------------------------
const Chapter: React.FC<{
  num: string;
  kicker: string;
  who: string;
  line: string;
  children: React.ReactNode;
}> = ({ num, kicker, who, line, children }) => {
  const frame = useCurrentFrame();
  const n = pop(frame, 6, 10);
  return (
    <AbsoluteFill style={cream}>
      {children}
      <div style={{ position: "absolute", left: 62, top: 262, width: 150, height: 150, borderRadius: 999,
        background: COLORS.accent, color: "#fff8f0", display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: DISPLAY, fontSize: 76, boxShadow: "0 14px 30px rgba(143,47,42,.35)", border: "6px solid #fff8f0",
        scale: Math.max(0, n), rotate: `${(1 - n) * -40 - 6}deg` }}>{num}</div>
      <div style={{ position: "absolute", top: 1205, left: 90, right: 90, color: INK }}>
        <MaskLine start={10} style={{ fontFamily: SANS_FONT, fontWeight: 800, fontSize: 34,
          letterSpacing: "0.3em", color: COLORS.accent }}>{kicker}</MaskLine>
        <MaskLine start={15} style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 600, fontSize: 142,
          lineHeight: 0.98, letterSpacing: "-0.03em" }}>{who}</MaskLine>
        <div style={{ fontFamily: SCRIPT_FONT, fontWeight: 700, fontSize: 60, color: WARM_SOFT, marginTop: 4,
          opacity: rise(frame, 26, 12), translate: `${(1 - rise(frame, 26, 14)) * 30}px 0px` }}>{line}</div>
      </div>
    </AbsoluteFill>
  );
};

/** A framed photo card that settles into place. */
const Card: React.FC<{
  crop: Crop;
  x: number; y: number; w: number; h: number;
  rotate?: number;
  from?: "left" | "right" | "below" | "scale";
  start?: number;
}> = ({ crop, x, y, w, h, rotate = 0, from = "scale", start = 0 }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [start, start + 18], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const off = (1 - p) * 700;
  const translate = from === "left" ? `${-off}px 0px` : from === "right" ? `${off}px 0px`
    : from === "below" ? `0px ${off}px` : "0px 0px";
  return (
    <div style={{
      position: "absolute", left: x, top: y, width: w, height: h, borderRadius: 30, overflow: "hidden",
      boxShadow: "0 30px 60px rgba(46,31,27,.25)", border: "10px solid #fffdf9",
      rotate: `${rotate}deg`, translate,
      scale: from === "scale" ? interpolate(p, [0, 1], [1.12, 1]) : 1,
      opacity: interpolate(frame, [start, start + 6], [0, 1], CLAMP),
    }}>
      <Photo crop={crop} push={[1, 1.1]} durationInFrames={CHAPTER} />
    </div>
  );
};

const Mum = () => (
  <Chapter num="01" kicker="FOR YOUR" who="mum." line="roses that never wilt">
    <Card crop={C.bouquet} x={150} y={330} w={780} h={820} rotate={-2} />
    <Polaroid crop={C.coralRose} start={22} x={660} y={800} w={330} rotate={8} label="for mum" sceneLength={CHAPTER} />
  </Chapter>
);

const BestFriend = () => (
  <Chapter num="02" kicker="FOR YOUR" who="best friend." line="she keeps stealing yours">
    <Card crop={C.ocean} x={80} y={330} w={450} h={830} from="left" start={0} />
    <Card crop={C.rubyScrunchie} x={550} y={330} w={450} h={405} from="right" start={7} />
    <Card crop={C.tricolour} x={550} y={755} w={450} h={405} from="below" start={14} />
    <Sticker start={30} rotate={7} bg={COLORS.pollen} style={{ left: 560, top: 690, fontFamily: SANS_FONT, fontSize: 36 }}>
      matching sets!
    </Sticker>
  </Chapter>
);

const SunflowerGirl = () => (
  <Chapter num="03" kicker="FOR THE" who="sunflower girl." line="a little sunshine, every day">
    <Card crop={C.sunflower} x={120} y={330} w={840} h={820} rotate={1.5} />
    <Polaroid crop={C.sunClips} start={18} x={700} y={290} w={320} rotate={8} label="hair clips" sceneLength={CHAPTER} />
    <Polaroid crop={C.sunKeychain} start={28} x={40} y={790} w={320} rotate={-9} label="keychain" sceneLength={CHAPTER} />
  </Chapter>
);

const Sister = () => (
  <Chapter num="04" kicker="FOR YOUR" who="sister." line="bows in every colour">
    <Polaroid crop={C.caramelBow} start={2} x={80} y={300} w={470} rotate={-7} label="caramel" sceneLength={CHAPTER} />
    <Polaroid crop={C.creamBow} start={12} x={520} y={370} w={470} rotate={6} label="cream" sceneLength={CHAPTER} />
    <Polaroid crop={C.maroonBow} start={22} x={290} y={560} w={470} rotate={-2} label="maroon" sceneLength={CHAPTER} />
  </Chapter>
);

const You = () => (
  <Chapter num="05" kicker="AND FOR" who="you. obviously." line="treat yourself first">
    <Card crop={C.bag} x={120} y={330} w={840} h={820} rotate={-1.5} />
    <Sticker start={20} rotate={-8} bg={COLORS.petalLight} style={{ left: 150, top: 1050, fontFamily: SCRIPT_FONT,
      fontSize: 64, padding: "6px 34px" }}>new!</Sticker>
    <Sticker start={32} rotate={7} bg={COLORS.pollen} style={{ left: 640, top: 360, fontFamily: SANS_FONT, fontSize: 36 }}>
      the Ruby Bag
    </Sticker>
  </Chapter>
);

// --------------------------------------------------------------------------
// The gift opens: ribbon on, bow on, ribbon off — and the offer is inside.
// --------------------------------------------------------------------------
const OPEN = 34;

const Confetti: React.FC<{ start: number }> = ({ start }) => {
  const frame = useCurrentFrame();
  const t = frame - start;
  if (t < 0 || t > 70) return null;
  const colours = [COLORS.pollen, "#fff8f0", COLORS.petalLight, COLORS.petalDark, "#f6d58e"];
  return (
    <>
      {Array.from({ length: 60 }, (_, i) => {
        const a = random(`a${i}`) * Math.PI * 2;
        const v = 18 + random(`v${i}`) * 26;
        const x = 540 + Math.cos(a) * v * t;
        const y = 560 + Math.sin(a) * v * t * 0.8 + 0.9 * t * t;
        const spin = random(`s${i}`) * 720 * (t / 30);
        return (
          <div key={i} style={{
            position: "absolute", left: x, top: y, width: 18, height: 30, borderRadius: 4,
            background: colours[i % colours.length], rotate: `${spin}deg`,
            opacity: interpolate(t, [45, 70], [1, 0], CLAMP),
          }} />
        );
      })}
    </>
  );
};

const GiftOffer: React.FC = () => {
  const frame = useCurrentFrame();
  const inV = interpolate(frame, [0, 12], [-1, 0], { ...CLAMP, easing: EASE_OUT });
  const inH = interpolate(frame, [4, 16], [-1, 0], { ...CLAMP, easing: EASE_OUT });
  const out = interpolate(frame, [OPEN, OPEN + 14], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const bow = pop(frame, 14, 10);
  const count = Math.round(interpolate(frame, [OPEN + 6, OPEN + 26], [0, 20], { ...CLAMP, easing: EASE_OUT }));
  const big = rise(frame, OPEN + 4, 10);
  const code = rise(frame, 96, 16);
  const band = (style: React.CSSProperties) => (
    <div style={{ position: "absolute", background: `linear-gradient(90deg, #d99e2b, ${COLORS.pollen} 30%, #f6d58e 50%, ${COLORS.pollen} 70%, #d99e2b)`,
      boxShadow: "0 0 30px rgba(0,0,0,.18)", ...style }} />
  );
  return (
    <AbsoluteFill style={{ background: `radial-gradient(90% 60% at 50% 40%, #d8665a, ${COLORS.accent} 60%, #a9433a)`,
      fontFamily: SANS_FONT, color: "#fff8f0", overflow: "hidden", translate: shake(frame, [OPEN], 18) }}>
      {band({ left: 480, width: 120, top: 0, height: 1920, translate: `0px ${(inV + out) * 1920}px` })}
      {band({ top: 500, height: 120, left: 0, width: 1080,
        background: `linear-gradient(180deg, #d99e2b, ${COLORS.pollen} 30%, #f6d58e 50%, ${COLORS.pollen} 70%, #d99e2b)`,
        translate: `${(inH + out) * 1080}px 0px` })}
      <div style={{ position: "absolute", left: 540 - 170, top: 560 - 120, width: 340, height: 240,
        scale: Math.max(0, bow) * (1 + out * 1.4), opacity: 1 - out }}>
        <svg viewBox="0 0 340 240" width={340} height={240}>
          <ellipse cx="95" cy="110" rx="90" ry="60" fill="#e7ac35" stroke="#b9801f" strokeWidth="8" transform="rotate(-18 95 110)" />
          <ellipse cx="245" cy="110" rx="90" ry="60" fill="#e7ac35" stroke="#b9801f" strokeWidth="8" transform="rotate(18 245 110)" />
          <rect x="138" y="78" width="64" height="70" rx="20" fill="#f3c55a" stroke="#b9801f" strokeWidth="8" />
        </svg>
      </div>
      <Confetti start={OPEN} />
      <div style={{ position: "absolute", top: 330, left: 0, right: 0, textAlign: "center", fontWeight: 800,
        fontSize: 32, letterSpacing: "0.3em", opacity: rise(frame, OPEN + 2, 10) }}>A LITTLE GIFT FROM US</div>
      <div style={{ position: "absolute", top: 420, left: 0, right: 0, textAlign: "center", fontFamily: DISPLAY,
        fontSize: 460, lineHeight: 1, opacity: big, scale: interpolate(big, [0, 1], [0.6, 1]),
        textShadow: "0 18px 40px rgba(80,20,15,.35)" }}>{count}%</div>
      <div style={{ position: "absolute", top: 965, left: 0, right: 0, textAlign: "center", fontFamily: DISPLAY,
        fontSize: 124, lineHeight: 1, letterSpacing: "0.01em", opacity: rise(frame, 62, 10),
        translate: `0px ${(1 - rise(frame, 62, 14)) * 50}px` }}>OFF EVERY GIFT</div>
      <div style={{ position: "absolute", top: 1125, left: 0, right: 0, display: "flex", justifyContent: "center",
        scale: Math.max(0, pop(frame, 78, 10)) }}>
        <span style={{ background: COLORS.pollen, color: INK, fontSize: 40, fontWeight: 800, padding: "16px 36px",
          borderRadius: 999 }}>Till Sunday &middot; 11 October</span>
      </div>
      <div style={{ position: "absolute", top: 1250, left: 0, right: 0, textAlign: "center", opacity: code,
        translate: `0px ${(1 - code) * 40}px` }}>
        <div style={{ fontSize: 34, fontWeight: 500, opacity: 0.92 }}>Mention this code when you order</div>
        <div style={{ display: "inline-block", marginTop: 16, background: "#fff", color: INK,
          fontFamily: "ui-monospace, Menlo, monospace", fontWeight: 800, fontSize: 70, letterSpacing: "0.08em",
          padding: "8px 34px", borderRadius: 18, border: `4px dashed ${DEEP}` }}>{CODE}</div>
      </div>
    </AbsoluteFill>
  );
};

// --------------------------------------------------------------------------
// Assembly
// --------------------------------------------------------------------------
const timing = linearTiming({ durationInFrames: T });

const SCENES: { len: number; node: React.ReactNode; out?: unknown }[] = [
  { len: HOOK, node: <Hook />, out: crossZoom({}) },
  { len: CHAPTER, node: <Mum />, out: filmBurn({ seed: 4 }) },
  { len: CHAPTER, node: <BestFriend />, out: ripple({}) },
  { len: CHAPTER, node: <SunflowerGirl />, out: crosswarp({}) },
  { len: CHAPTER, node: <Sister />, out: zoomBlur({}) },
  { len: CHAPTER, node: <You />, out: pushCut({ flashColor: "#fff8f0", flashOpacity: 0.85, flashFrames: 4 }) },
  { len: OFFER, node: <GiftOffer />, out: lightLeak() },
  { len: CTA, node: <CtaScene /> },
];

const STARTS = SCENES.reduce<number[]>((acc, s, i) => {
  acc.push(i === 0 ? 0 : acc[i - 1] + SCENES[i - 1].len - T);
  return acc;
}, []);

export const GIFTS_DURATION = STARTS[STARTS.length - 1] + SCENES[SCENES.length - 1].len;

const OFFER_AT = STARTS[6];

const CUES: Cue[] = [
  ...[0, 6, 12, 18].map((at) => ({ at, sound: "shutter" as const, volume: 0.35 })),
  { at: 22, sound: "pop", volume: 0.35 },
  ...STARTS.slice(1, 6).map((s) => ({ at: s - 6, sound: "whoosh" as const, volume: 0.4 })),
  ...STARTS.slice(1, 6).map((s) => ({ at: s + 18, sound: "pop" as const, volume: 0.25 })),
  { at: OFFER_AT - 30, sound: "riser", volume: 0.35 },
  { at: OFFER_AT + 14, sound: "pop", volume: 0.4 },
  { at: OFFER_AT + OPEN, sound: "impact", volume: 0.5 },
  { at: OFFER_AT + 60, sound: "ding", volume: 0.35 },
  { at: OFFER_AT + 96, sound: "pop", volume: 0.35 },
  { at: STARTS[7], sound: "whoosh", volume: 0.3 },
];

export const ReelGifts: React.FC = () => {
  const timeline: React.ReactNode[] = [];
  SCENES.forEach((s, i) => {
    timeline.push(
      <TransitionSeries.Sequence key={`s${i}`} durationInFrames={s.len} premountFor={30}>
        {s.node}
      </TransitionSeries.Sequence>,
    );
    if (s.out) {
      timeline.push(<TransitionSeries.Transition key={`t${i}`} presentation={s.out as never} timing={timing} />);
    }
  });
  return (
    <AbsoluteFill style={{ background: "#f7f1e8" }}>
      <TransitionSeries>{timeline}</TransitionSeries>
      <Sounds cues={CUES} />
    </AbsoluteFill>
  );
};
