import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { Audio } from "@remotion/media";
import type {
  TransitionPresentation,
  TransitionPresentationComponentProps,
} from "@remotion/transitions";
import { COLORS, SANS_FONT, SCRIPT_FONT } from "../theme";

/** Instagram Reels canvas. */
export const FPS = 30;
export const W = 1080;
export const H = 1920;

/*
 * Reels safe area. Instagram draws its own UI over the frame: the top bar,
 * the like / comment / share column down the right, and the caption, sound
 * and username block along the bottom. Anything a viewer must read sits
 * between y≈240 and y≈1480 and clear of the right-hand ~140px.
 */
export const SAFE_TOP = 240;
export const SAFE_BOTTOM = 1480;

export const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const EASE_OUT = Easing.bezier(0.16, 1, 0.3, 1);
export const EASE_IN_OUT = Easing.bezier(0.65, 0, 0.35, 1);
export const SPRINGY = Easing.bezier(0.34, 1.56, 0.64, 1);

/** 0→1 over [start, start+len] with the house ease-out. */
export const rise = (frame: number, start: number, len = 14) =>
  interpolate(frame, [start, start + len], [0, 1], { ...CLAMP, easing: EASE_OUT });

// --------------------------------------------------------------------------
// The zoom-through transition: the outgoing scene rushes past the camera
// while the next one arrives from a little way off — a push through one
// frame into the next, rather than a cut or a slide.
// --------------------------------------------------------------------------
type ZoomProps = Record<string, never>;

const ZoomThrough: React.FC<TransitionPresentationComponentProps<ZoomProps>> = ({
  children,
  presentationDirection,
  presentationProgress,
}) => {
  const p = presentationProgress;
  const entering = presentationDirection === "entering";
  return (
    <AbsoluteFill
      style={
        entering
          ? {
              opacity: interpolate(p, [0, 0.55], [0, 1], CLAMP),
              scale: interpolate(p, [0, 1], [0.8, 1], CLAMP),
            }
          : {
              opacity: interpolate(p, [0.2, 0.9], [1, 0], CLAMP),
              scale: interpolate(p, [0, 1], [1, 1.4], CLAMP),
            }
      }
    >
      {children}
    </AbsoluteFill>
  );
};

export const zoomThrough = (): TransitionPresentation<ZoomProps> => ({
  component: ZoomThrough,
  props: {},
});

// --------------------------------------------------------------------------
// A product photo cropped to the piece itself. Most source photos are
// finished promo graphics with text round the edges, so each one carries a
// focus point and zoom that keep that text out of frame.
// --------------------------------------------------------------------------
export type Crop = { file: string; focus: string; zoom: number };

export const Photo: React.FC<{
  crop: Crop;
  /** extra push-in across the scene, as [start, end] multipliers */
  push?: [number, number];
  durationInFrames?: number;
}> = ({ crop, push = [1, 1], durationInFrames = 60 }) => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, durationInFrames], push, CLAMP);
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
      <Img
        src={staticFile(`images/${crop.file}`)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          objectPosition: crop.focus,
          transformOrigin: crop.focus,
          scale: crop.zoom * drift,
        }}
      />
    </div>
  );
};

// --------------------------------------------------------------------------
// Sound. Three cues, synthesised for this campaign so there is nothing to
// license: a soft whoosh under each move, a ding when the offer lands and a
// pop as text arrives. Kept quiet so they sit under whatever trending track
// is added in Instagram rather than fighting it.
// --------------------------------------------------------------------------
export type Cue = {
  at: number;
  sound: "whoosh" | "ding" | "pop" | "impact" | "riser" | "shutter" | "whip";
  volume: number;
};

export const Sounds: React.FC<{ cues: Cue[] }> = ({ cues }) => (
  <>
    {cues.map((cue, i) => (
      <Sequence key={i} from={cue.at} durationInFrames={FPS * 2} layout="none">
        <Audio src={staticFile(`sfx/${cue.sound}.wav`)} volume={cue.volume} />
      </Sequence>
    ))}
  </>
);

// --------------------------------------------------------------------------
// Brand bits
// --------------------------------------------------------------------------
export const Flower: React.FC<{ size: number }> = ({ size }) => (
  <svg viewBox="0 0 400 400" width={size} height={size}>
    <g fill={COLORS.petalLight}>
      {[0, 180, 300, 240].map((a) => (
        <ellipse key={a} cx="200" cy="130" rx="34" ry="62" transform={`rotate(${a} 200 200)`} />
      ))}
    </g>
    <g fill={COLORS.petalDark}>
      {[60, 120].map((a) => (
        <ellipse key={a} cx="200" cy="130" rx="34" ry="62" transform={`rotate(${a} 200 200)`} />
      ))}
    </g>
    <circle cx="200" cy="200" r="28" fill={COLORS.pollen} />
  </svg>
);

export const cream: React.CSSProperties = {
  background: "radial-gradient(110% 70% at 50% 35%, #fff8f0 0%, #f7f1e8 55%, #efe5d8 100%)",
  fontFamily: SANS_FONT,
  color: "#2e1f1b",
};

/** Campaign colours not in the site palette: the posters' deep red and warm grey. */
export const DEEP = "#8f2f2a";
export const WARM_SOFT = "#7a6a63";
export const INK = "#2e1f1b";

export const DOMAIN = "mayurisyarntales.online";
export const CODE = "LAUNCH20";

// --------------------------------------------------------------------------
// Shared closing scenes — the offer, then where to go.
// --------------------------------------------------------------------------
export const OfferScene: React.FC = () => {
  const frame = useCurrentFrame();
  // the number counts up rather than appearing, which is what makes it land
  const count = Math.round(interpolate(frame, [8, 30], [0, 20], { ...CLAMP, easing: EASE_OUT }));
  const code = rise(frame, 66, 16);
  return (
    <AbsoluteFill style={{ background: COLORS.accent, fontFamily: SANS_FONT, color: "#fff8f0" }}>
      <div style={{ position: "absolute", top: 400, left: 0, right: 0, textAlign: "center",
        fontSize: 30, fontWeight: 700, letterSpacing: "0.26em", opacity: rise(frame, 0, 10) }}>
        LAUNCH WEEK OFFER
      </div>
      <div style={{ position: "absolute", top: 470, left: 0, right: 0, textAlign: "center",
        fontSize: 400, fontWeight: 900, letterSpacing: "-0.06em", lineHeight: 1,
        scale: interpolate(frame, [8, 30], [0.86, 1], { ...CLAMP, easing: EASE_OUT }),
        opacity: rise(frame, 6, 8) }}>
        {count}%
      </div>
      <div style={{ position: "absolute", top: 880, left: 0, right: 0, textAlign: "center",
        fontSize: 104, fontWeight: 900, letterSpacing: "-0.02em",
        opacity: rise(frame, 30, 10),
        translate: `0px ${interpolate(rise(frame, 30, 14), [0, 1], [50, 0])}px` }}>
        OFF EVERYTHING
      </div>
      <div style={{ position: "absolute", top: 1018, left: 0, right: 0, display: "flex", justifyContent: "center",
        opacity: rise(frame, 44, 10), scale: interpolate(rise(frame, 44, 16), [0, 1], [0.8, 1]) }}>
        <span style={{ background: COLORS.pollen, color: INK, fontSize: 38, fontWeight: 800,
          padding: "16px 34px", borderRadius: 999 }}>Till Sunday &middot; 11 October</span>
      </div>
      <div style={{ position: "absolute", top: 1182, left: 0, right: 0, textAlign: "center",
        opacity: code, translate: `0px ${interpolate(code, [0, 1], [40, 0])}px` }}>
        <div style={{ fontSize: 34, fontWeight: 500, opacity: 0.92 }}>Mention this when you order</div>
        <div style={{ display: "inline-block", marginTop: 18, background: "#fff", color: INK,
          fontFamily: "ui-monospace, Menlo, monospace", fontWeight: 800, fontSize: 70,
          letterSpacing: "0.08em", padding: "10px 34px", borderRadius: 18,
          border: `4px dashed ${DEEP}` }}>{CODE}</div>
      </div>
    </AbsoluteFill>
  );
};

export const CtaScene: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={cream}>
      <div style={{ position: "absolute", top: 470, left: 0, right: 0, display: "flex", flexDirection: "column",
        alignItems: "center", opacity: rise(frame, 0, 12),
        scale: interpolate(rise(frame, 0, 18), [0, 1], [0.9, 1]) }}>
        <Flower size={110} />
        <div style={{ fontFamily: SCRIPT_FONT, fontWeight: 700, fontSize: 150, lineHeight: 1, marginTop: 6 }}>
          Mayuri&rsquo;z
        </div>
      </div>
      <div style={{ position: "absolute", top: 790, left: 0, right: 0, textAlign: "center", fontSize: 40,
        fontWeight: 600, color: WARM_SOFT, opacity: rise(frame, 8, 12) }}>
        Handmade crochet, made to order
      </div>
      <div style={{ position: "absolute", top: 900, left: 0, right: 0, display: "flex", justifyContent: "center",
        opacity: rise(frame, 14, 10), scale: interpolate(rise(frame, 14, 18), [0, 1], [0.85, 1]) }}>
        <span style={{ background: COLORS.accent, color: "#fff", fontSize: 50, fontWeight: 700,
          padding: "26px 52px", borderRadius: 999, boxShadow: "0 18px 40px rgba(200,86,74,.35)" }}>
          {DOMAIN}
        </span>
      </div>
      <div style={{ position: "absolute", top: 1062, left: 0, right: 0, textAlign: "center", fontSize: 34,
        fontWeight: 600, color: INK, opacity: rise(frame, 24, 12) }}>
        Tap the link in our bio
      </div>
      <div style={{ position: "absolute", top: 1124, left: 0, right: 0, textAlign: "center", fontSize: 30,
        color: WARM_SOFT, opacity: rise(frame, 30, 12) }}>
        20% off till Sunday &middot; code <b style={{ color: COLORS.accent }}>{CODE}</b>
      </div>
    </AbsoluteFill>
  );
};
