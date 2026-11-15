import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { loadFont as loadPlayfair } from "@remotion/google-fonts/PlayfairDisplay";
import { SANS_FONT, SCRIPT_FONT } from "../theme";
import { beatPulse, lerp } from "./fx";

const playfair = loadPlayfair("normal", { weights: ["500", "600", "700"], subsets: ["latin"] });
loadPlayfair("italic", { weights: ["400", "500"], subsets: ["latin"] });

export const SERIF = `${playfair.fontFamily}, Georgia, serif`;
export { SANS_FONT as SANS, SCRIPT_FONT as SCRIPT };

/** Brand palette (media/social/brand.md). */
export const BRAND = {
  rose: "#e58fa3",
  roseLight: "#f2b8c6",
  red: "#c8564a",
  ink: "#1d1d1f",
  inkSoft: "#5b4a46",
  cream: "#f9ece4",
  creamDeep: "#f1dcd0",
  white: "#ffffff",
  pollen: "#e8b23d",
  leaf: "#7d9b6a",
} as const;

export const W = 1080;
export const H = 1920;

/**
 * A product photo, cover-fitted, with an optional zoom around a focus point.
 * object-position x%/y% puts that point of the image at x%/y% of the box, so
 * scaling around the same origin keeps the piece itself centred in the zoom.
 */
export const Photo: React.FC<{
  src: string;
  focus?: { x: number; y: number };
  zoom?: number;
  style?: React.CSSProperties;
}> = ({ src, focus = { x: 0.5, y: 0.5 }, zoom = 1, style }) => (
  <Img
    src={staticFile(src)}
    style={{
      width: "100%",
      height: "100%",
      objectFit: "cover",
      objectPosition: `${focus.x * 100}% ${focus.y * 100}%`,
      transformOrigin: `${focus.x * 100}% ${focus.y * 100}%`,
      transform: `scale(${zoom})`,
      ...style,
    }}
  />
);

/**
 * Soft, blurred, slowly drifting copy of the photo behind everything.
 * Staged photos (weekly/…) come with a small pre-blurred "-soft" copy made by
 * tools/weekly_video.py; live CSS blur on a big photo every frame is what
 * crashes Chrome on an 8 GB PC, so it's only the fallback for Studio samples.
 */
export const Backdrop: React.FC<{ src: string; tint?: string; tintOpacity?: number }> = ({
  src,
  tint = BRAND.cream,
  tintOpacity = 0.55,
}) => {
  const frame = useCurrentFrame();
  const staged = src.startsWith("weekly/");
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: tint }}>
      <AbsoluteFill
        style={{
          transform: `scale(${1.35 + frame * 0.0006}) rotate(${frame * 0.01}deg)`,
          filter: staged ? "saturate(1.15)" : "blur(46px) saturate(1.15)",
        }}
      >
        <Photo src={staged ? src.replace(/\.jpg$/, "-soft.jpg") : src} />
      </AbsoluteFill>
      <AbsoluteFill style={{ backgroundColor: tint, opacity: tintOpacity }} />
    </AbsoluteFill>
  );
};

/** Film grain + vignette so flat colour never looks like a PowerPoint slide. */
export const Finish: React.FC<{ vignette?: number }> = ({ vignette = 0.28 }) => {
  return (
    <>
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(40,20,15,${vignette}) 100%)`,
          pointerEvents: "none",
        }}
      />
      {/* static grain: moving noise looks nice but triples the file size */}
      <AbsoluteFill style={{ opacity: 0.05, mixBlendMode: "multiply", pointerEvents: "none" }}>
        <Img src={staticFile("weekly/grain.png")} style={{ width: W, height: H, imageRendering: "pixelated" }} />
      </AbsoluteFill>
    </>
  );
};

/** Diagonal sheen that sweeps across a card once, starting at `at`. */
export const LightSweep: React.FC<{ at: number; length?: number }> = ({ at, length = 22 }) => {
  const frame = useCurrentFrame();
  const t = lerp(frame, [at, at + length], [-0.6, 1.6]);
  if (frame < at || frame > at + length) return null;
  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(115deg, rgba(255,255,255,0) ${t * 100 - 18}%, rgba(255,255,255,0.55) ${t * 100}%, rgba(255,255,255,0) ${t * 100 + 18}%)`,
        mixBlendMode: "soft-light",
        pointerEvents: "none",
      }}
    />
  );
};

/** The brand's own logo files (media/brand), copied to public/brand. */
export const Logo: React.FC<{
  kind?: "full" | "short";
  tone?: "light" | "dark" | "mono-white";
  width: number;
  style?: React.CSSProperties;
}> = ({ kind = "short", tone = "light", width, style }) => (
  <Img src={staticFile(`brand/logo-${kind}-${tone}.svg`)} style={{ width, ...style }} />
);

/** Rounded website pill. Kicks on every beat when `beats` is given. */
export const WebsitePill: React.FC<{
  website: string;
  beats?: readonly number[];
  size?: number;
  bg?: string;
  fg?: string;
  style?: React.CSSProperties;
}> = ({ website, beats = [], size = 44, bg = BRAND.red, fg = BRAND.white, style }) => {
  const frame = useCurrentFrame();
  const kick = beatPulse(frame, beats, 9);
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: size * 0.4,
        padding: `${size * 0.42}px ${size * 0.9}px`,
        borderRadius: 999,
        backgroundColor: bg,
        color: fg,
        fontFamily: SANS_FONT,
        fontWeight: 650,
        fontSize: size,
        letterSpacing: "-0.01em",
        boxShadow: `0 ${18 + kick * 10}px ${50 + kick * 30}px rgba(200,86,74,${0.28 + kick * 0.2})`,
        transform: `scale(${1 + kick * 0.06})`,
        whiteSpace: "nowrap",
        ...style,
      }}
    >
      <svg width={size * 0.9} height={size * 0.9} viewBox="0 0 24 24" fill="none" stroke={fg} strokeWidth={2}>
        <circle cx={12} cy={12} r={9.5} />
        <path d="M2.5 12h19M12 2.5c3 3.2 3 15.8 0 19M12 2.5c-3 3.2-3 15.8 0 19" />
      </svg>
      {website}
    </div>
  );
};

/** Words that rise and sharpen one after another (premium headline reveal). */
export const RiseWords: React.FC<{
  text: string;
  start: number;
  stagger?: number;
  style?: React.CSSProperties;
  wordStyle?: (i: number) => React.CSSProperties;
}> = ({ text, start, stagger = 4, style, wordStyle }) => {
  const frame = useCurrentFrame();
  const words = text.split(" ");
  return (
    <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", columnGap: "0.26em", ...style }}>
      {words.map((w, i) => {
        const s = start + i * stagger;
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              opacity: lerp(frame, [s, s + 10], [0, 1]),
              transform: `translateY(${lerp(frame, [s, s + 16], [42, 0])}px)`,
              filter: `blur(${lerp(frame, [s, s + 12], [12, 0])}px)`,
              ...(wordStyle ? wordStyle(i) : {}),
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

/** Thin hand-drawn thread line that draws itself, for under headlines. */
export const Thread: React.FC<{ start: number; width: number; color?: string; length?: number }> = ({
  start,
  width,
  color = BRAND.red,
  length = 24,
}) => {
  const frame = useCurrentFrame();
  const p = lerp(frame, [start, start + length], [0, 1]);
  const d = `M4 22 C ${width * 0.25} 2, ${width * 0.4} 40, ${width * 0.55} 20 S ${width * 0.85} 6, ${width - 4} 18`;
  return (
    <svg width={width} height={44} viewBox={`0 0 ${width} 44`} style={{ overflow: "visible" }}>
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={4}
        strokeLinecap="round"
        pathLength={1}
        strokeDasharray={1}
        strokeDashoffset={1 - p}
      />
    </svg>
  );
};
