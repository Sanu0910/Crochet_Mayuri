import React from "react";
import { loadFont } from "@remotion/fonts";
import {
  AbsoluteFill,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
} from "remotion";
import type {
  TransitionPresentation,
  TransitionPresentationComponentProps,
} from "@remotion/transitions";
import { CLAMP, EASE_IN_OUT, EASE_OUT, FPS, Photo, type Crop } from "./kit";

/*
 * Effects for the second pair of Reels: two display faces, extra
 * transitions, and the stickers, tickers and polaroids that give a Reel its
 * collage look. Fonts are local files (OFL, see public/fonts/licenses) so a
 * render never depends on reaching Google.
 */
await Promise.all([
  loadFont({ family: "Anton", url: staticFile("fonts/Anton.woff2"), weight: "400", format: "woff2" }),
  loadFont({ family: "Fraunces", url: staticFile("fonts/Fraunces.woff2"), weight: "100 900", format: "woff2" }),
  loadFont({ family: "Fraunces", url: staticFile("fonts/Fraunces-Italic.woff2"), weight: "100 900",
    style: "italic", format: "woff2" }),
]);

/** Tall condensed poster face — for anything that has to hit hard. */
export const DISPLAY = "Anton, Impact, sans-serif";
/** Soft editorial serif — for anything that should feel like a gift. */
export const SERIF = "Fraunces, Georgia, serif";

/** 120 BPM at 30 fps: a beat every 15 frames. Cuts land on these. */
export const BEAT = 15;

/** A bouncy 0→1 from `start`, for things that pop in. */
export const pop = (frame: number, start: number, damping = 11) =>
  spring({ frame: frame - start, fps: FPS, config: { damping, stiffness: 190, mass: 0.7 } });

// --------------------------------------------------------------------------
// Transitions
// --------------------------------------------------------------------------

type WhipProps = { direction: "left" | "up" };

/** A whip pan: both scenes smear past together, the way a phone camera does
 *  when it is flicked to the next thing. */
const Whip: React.FC<TransitionPresentationComponentProps<WhipProps>> = ({
  children, presentationDirection, presentationProgress, passedProps,
}) => {
  const p = EASE_IN_OUT(presentationProgress);
  const entering = presentationDirection === "entering";
  const travel = passedProps.direction === "left" ? 1080 : 1920;
  const offset = entering ? (1 - p) * travel : -p * travel;
  // the blur peaks mid-move, which is what sells the speed
  const blur = Math.sin(Math.PI * presentationProgress) * 28;
  const t = passedProps.direction === "left" ? `${offset}px 0px` : `0px ${offset}px`;
  return (
    <AbsoluteFill style={{ translate: t, filter: blur > 0.5 ? `blur(${blur}px)` : undefined }}>
      {children}
    </AbsoluteFill>
  );
};

export const whipPan = (direction: WhipProps["direction"] = "left"): TransitionPresentation<WhipProps> => ({
  component: Whip,
  props: { direction },
});

type LeakProps = Record<string, never>;

/** A crossfade with a warm light leak washing over the join. */
const Leak: React.FC<TransitionPresentationComponentProps<LeakProps>> = ({
  children, presentationDirection, presentationProgress,
}) => {
  const p = presentationProgress;
  if (presentationDirection === "exiting") {
    return <AbsoluteFill>{children}</AbsoluteFill>;
  }
  const glow = Math.sin(Math.PI * p);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ opacity: interpolate(p, [0.25, 0.75], [0, 1], CLAMP) }}>{children}</AbsoluteFill>
      <AbsoluteFill style={{
        opacity: glow * 0.9,
        mixBlendMode: "screen",
        background: `radial-gradient(60% 45% at ${20 + 60 * p}% ${30 + 25 * p}%, rgba(255,190,120,.95), rgba(255,120,90,.55) 45%, rgba(255,90,90,0) 75%)`,
      }} />
    </AbsoluteFill>
  );
};

export const lightLeak = (): TransitionPresentation<LeakProps> => ({ component: Leak, props: {} });

// --------------------------------------------------------------------------
// Pieces of a Reel collage
// --------------------------------------------------------------------------

/** Text that slides up out of an invisible slot. */
export const MaskLine: React.FC<{
  start: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
  len?: number;
}> = ({ start, children, style, len = 14 }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [start, start + len], [0, 1], { ...CLAMP, easing: EASE_OUT });
  return (
    <div style={{ overflow: "hidden", paddingBottom: "0.08em", ...style }}>
      <div style={{ translate: `0px ${(1 - p) * 110}%` }}>{children}</div>
    </div>
  );
};

/** A tilted label that pops on like a sticker being slapped down. */
export const Sticker: React.FC<{
  start: number;
  rotate?: number;
  bg?: string;
  color?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ start, rotate = -6, bg = "#fff", color = "#2e1f1b", children, style }) => {
  const frame = useCurrentFrame();
  const s = pop(frame, start, 9);
  return (
    <div style={{
      position: "absolute",
      background: bg,
      color,
      borderRadius: 999,
      padding: "14px 30px",
      fontWeight: 800,
      boxShadow: "0 12px 30px rgba(46,31,27,.22)",
      rotate: `${rotate + (1 - s) * 18}deg`,
      scale: Math.max(0, s),
      opacity: frame >= start ? 1 : 0,
      whiteSpace: "nowrap",
      ...style,
    }}>{children}</div>
  );
};

/** A polaroid print that drops onto the table. */
export const Polaroid: React.FC<{
  crop: Crop;
  start: number;
  x: number;
  y: number;
  w: number;
  rotate: number;
  label?: string;
  sceneLength?: number;
}> = ({ crop, start, x, y, w, rotate, label, sceneLength = 100 }) => {
  const frame = useCurrentFrame();
  const s = pop(frame, start, 13);
  const pad = Math.round(w * 0.05);
  return (
    <div style={{
      position: "absolute", left: x, top: y, width: w,
      background: "#fffdf9",
      padding: `${pad}px ${pad}px ${label ? pad * 3.4 : pad * 2.6}px`,
      boxShadow: "0 24px 50px rgba(46,31,27,.28), 0 2px 6px rgba(46,31,27,.12)",
      rotate: `${rotate + (1 - s) * -14}deg`,
      translate: `0px ${(1 - s) * -160}px`,
      scale: interpolate(s, [0, 1], [1.25, 1]),
      opacity: interpolate(frame, [start, start + 4], [0, 1], CLAMP),
    }}>
      <div style={{ position: "relative", width: "100%", aspectRatio: "1 / 1.08", overflow: "hidden" }}>
        <Photo crop={crop} push={[1, 1.08]} durationInFrames={sceneLength} />
      </div>
      {label ? (
        <div style={{ position: "absolute", left: 0, right: 0, bottom: pad * 0.9, textAlign: "center",
          fontFamily: "Caveat, cursive", fontWeight: 700, fontSize: w * 0.1, color: "#5a463f" }}>{label}</div>
      ) : null}
    </div>
  );
};

/** An endless band of text running across the frame. */
export const Ticker: React.FC<{
  text: string;
  y: number;
  rotate: number;
  bg: string;
  color: string;
  speed?: number;
  size?: number;
  start?: number;
}> = ({ text, y, rotate, bg, color, speed = 6, size = 64, start = 0 }) => {
  const frame = useCurrentFrame();
  const enter = interpolate(frame, [start, start + 12], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const unit = `${text}  •  `;
  return (
    <div style={{
      position: "absolute", left: -200, right: -200, top: y,
      background: bg, color, rotate: `${rotate}deg`,
      fontFamily: DISPLAY, fontSize: size, lineHeight: 1, padding: `${size * 0.28}px 0`,
      whiteSpace: "nowrap", overflow: "hidden",
      boxShadow: "0 14px 34px rgba(0,0,0,.18)",
      scale: `${enter} 1`,
    }}>
      <div style={{ translate: `${-frame * speed}px 0px`, letterSpacing: "0.02em" }}>
        {unit.repeat(12)}
      </div>
    </div>
  );
};

/** Text set round a circle, slowly turning — the badge on a shop window. */
export const RoundBadge: React.FC<{
  text: string;
  size: number;
  bg: string;
  color: string;
  center?: React.ReactNode;
  start: number;
}> = ({ text, size, bg, color, center, start }) => {
  const frame = useCurrentFrame();
  const s = pop(frame, start, 12);
  const r = 140;
  return (
    <div style={{ width: size, height: size, scale: Math.max(0, s), rotate: `${(1 - s) * -90}deg` }}>
      <svg viewBox="0 0 400 400" width={size} height={size}>
        <circle cx="200" cy="200" r="196" fill={bg} />
        <defs>
          <path id="badge-ring" d={`M 200 200 m -${r} 0 a ${r} ${r} 0 1 1 ${r * 2} 0 a ${r} ${r} 0 1 1 -${r * 2} 0`} />
        </defs>
        <g style={{ transformOrigin: "200px 200px", rotate: `${frame * 1.6}deg` }}>
          <text fill={color} style={{ fontFamily: DISPLAY, fontSize: 44, letterSpacing: 6 }}>
            <textPath href="#badge-ring">{text}</textPath>
          </text>
        </g>
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
        {center}
      </div>
    </div>
  );
};

/** Screen shake that decays after each hit. */
export const shake = (frame: number, hits: number[], strength = 22) => {
  let x = 0;
  let y = 0;
  for (const h of hits) {
    const t = frame - h;
    if (t < 0 || t > 10) continue;
    const decay = Math.exp(-t * 0.45);
    x += Math.sin(t * 2.7 + h) * strength * decay;
    y += Math.cos(t * 3.3 + h * 0.7) * strength * 0.7 * decay;
  }
  return `${x}px ${y}px`;
};

/** A soft dark edge, so the eye stays in the middle. */
export const Vignette: React.FC<{ strength?: number }> = ({ strength = 0.35 }) => (
  <AbsoluteFill style={{
    pointerEvents: "none",
    background: `radial-gradient(120% 85% at 50% 50%, rgba(0,0,0,0) 55%, rgba(30,15,10,${strength}) 100%)`,
  }} />
);
