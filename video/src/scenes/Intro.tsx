import React from "react";
import {
  AbsoluteFill,
  Easing,
  Interactive,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { COLORS, SCRIPT_FONT, SANS_FONT } from "../theme";

const EASE = Easing.bezier(0.16, 1, 0.3, 1);

/** Petal ring: [rotation in degrees, fill, entrance frame]. */
const PETALS = [
  [0, COLORS.petalLight, 24],
  [180, COLORS.petalLight, 27],
  [60, COLORS.petalDark, 30],
  [120, COLORS.petalDark, 33],
  [300, COLORS.petalLight, 36],
  [240, COLORS.petalLight, 39],
] as const;

/**
 * Two yarn threads sweep in from the edges, curl into a six-petal flower,
 * and the brand mark rises underneath it — the same idea as the hero
 * animation on the website, rebuilt frame-accurately for video.
 */
export const Intro: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.surfaceAlt,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <svg
        viewBox="0 0 400 400"
        width={620}
        height={620}
        style={{ marginTop: -60 }}
      >
        <path
          d="M -40,205 C 40,150 110,255 168,202"
          fill="none"
          stroke={COLORS.accent}
          strokeWidth={7}
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          style={{
            strokeDashoffset: interpolate(frame, [0, 30], [1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: EASE,
            }),
            opacity: interpolate(frame, [36, 60], [1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: EASE,
            }),
          }}
        />
        <path
          d="M 440,205 C 360,150 290,255 232,202"
          fill="none"
          stroke={COLORS.accent}
          strokeWidth={7}
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          style={{
            strokeDashoffset: interpolate(frame, [2, 32], [1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: EASE,
            }),
            opacity: interpolate(frame, [36, 60], [1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: EASE,
            }),
          }}
        />

        {PETALS.map(([angle, fill, start]) => (
          <g key={angle} transform={`rotate(${angle} 200 200)`}>
            <g
              style={{
                transformBox: "view-box",
                transformOrigin: "200px 200px",
                opacity: interpolate(frame, [start, start + 10], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                }),
                scale: interpolate(frame, [start, start + 22], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                  easing: Easing.bezier(0.34, 1.4, 0.5, 1),
                  output: "perceptual-scale",
                }),
              }}
            >
              <ellipse cx={200} cy={130} rx={34} ry={62} fill={fill} />
            </g>
          </g>
        ))}

        <circle
          cx={200}
          cy={200}
          r={28}
          fill={COLORS.pollen}
          style={{
            transformBox: "view-box",
            transformOrigin: "200px 200px",
            scale: interpolate(frame, [44, 62], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.34, 1.5, 0.5, 1),
              output: "perceptual-scale",
            }),
          }}
        />
      </svg>

      <Interactive.Div
        name="Brand mark"
        style={{
          fontFamily: SCRIPT_FONT,
          fontSize: 168,
          lineHeight: 1,
          color: COLORS.ink,
          marginTop: -70,
          opacity: interpolate(frame, [56, 76], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
          translate: interpolate(frame, [56, 82], ["0px 34px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
        }}
      >
        Mayuri&rsquo;z
      </Interactive.Div>

      <Interactive.Div
        name="Kicker"
        style={{
          fontFamily: SANS_FONT,
          fontSize: 40,
          fontWeight: 500,
          letterSpacing: "0.42em",
          textTransform: "uppercase",
          color: COLORS.inkFaint,
          marginTop: 22,
          paddingLeft: "0.42em",
          opacity: interpolate(frame, [74, 94], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
        }}
      >
        Handmade Crochet
      </Interactive.Div>
    </AbsoluteFill>
  );
};
