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

const PETALS = [0, 60, 120, 180, 240, 300] as const;

const PROMISES = ["Made to order", "Any colour you like", "Gift-ready"] as const;

/** Closing card: the mark, what you get, and how to ask for it. */
export const Outro: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.surfaceAlt,
        justifyContent: "center",
        alignItems: "center",
        padding: "0 88px",
      }}
    >
      <svg
        viewBox="0 0 400 400"
        width={230}
        height={230}
        style={{
          opacity: interpolate(frame, [0, 18], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
          rotate: interpolate(frame, [0, 105], ["-14deg", "6deg"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
        }}
      >
        {PETALS.map((angle) => (
          <g key={angle} transform={`rotate(${angle} 200 200)`}>
            <ellipse
              cx={200}
              cy={130}
              rx={34}
              ry={62}
              fill={angle % 120 === 0 ? COLORS.petalLight : COLORS.petalDark}
            />
          </g>
        ))}
        <circle cx={200} cy={200} r={28} fill={COLORS.pollen} />
      </svg>

      <Interactive.Div
        name="Brand mark"
        style={{
          fontFamily: SCRIPT_FONT,
          fontSize: 150,
          lineHeight: 1,
          color: COLORS.ink,
          marginTop: 8,
          opacity: interpolate(frame, [10, 30], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
          translate: interpolate(frame, [10, 36], ["0px 28px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
        }}
      >
        Mayuri&rsquo;z
      </Interactive.Div>

      <Interactive.Div
        name="Promises"
        style={{
          display: "flex",
          gap: 20,
          alignItems: "center",
          whiteSpace: "nowrap",
          marginTop: 34,
          fontFamily: SANS_FONT,
          fontSize: 32,
          fontWeight: 500,
          color: COLORS.inkSoft,
          opacity: interpolate(frame, [26, 48], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
        }}
      >
        {PROMISES.map((promise, i) => (
          <React.Fragment key={promise}>
            {i > 0 ? <span style={{ color: COLORS.petalDark }}>·</span> : null}
            <span>{promise}</span>
          </React.Fragment>
        ))}
      </Interactive.Div>

      <Interactive.Div
        name="Call to action"
        style={{
          marginTop: 78,
          textAlign: "center",
          fontFamily: SANS_FONT,
          opacity: interpolate(frame, [44, 66], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
          translate: interpolate(frame, [44, 72], ["0px 30px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
        }}
      >
        <div
          style={{
            fontSize: 68,
            fontWeight: 600,
            letterSpacing: "-0.02em",
            color: COLORS.ink,
          }}
        >
          Order yours
        </div>
        <div
          style={{
            fontSize: 42,
            fontWeight: 500,
            marginTop: 16,
            color: COLORS.accent,
          }}
        >
          mayurighoshblg@gmail.com
        </div>
      </Interactive.Div>
    </AbsoluteFill>
  );
};
