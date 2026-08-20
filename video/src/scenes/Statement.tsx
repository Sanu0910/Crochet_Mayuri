import React from "react";
import {
  AbsoluteFill,
  Easing,
  Interactive,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { COLORS, SANS_FONT } from "../theme";

const EASE = Easing.bezier(0.16, 1, 0.3, 1);

const LINES = [
  { text: "Handmade.", start: 4, muted: false },
  { text: "In every sense", start: 12, muted: true },
  { text: "of the word.", start: 20, muted: true },
] as const;

/** The site's headline, delivered one line at a time. */
export const Statement: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.surfaceAlt,
        justifyContent: "center",
        alignItems: "flex-start",
        padding: "0 96px",
      }}
    >
      {LINES.map((line) => (
        <div key={line.text} style={{ overflow: "hidden", paddingBottom: 12 }}>
          <Interactive.Div
            name={line.text}
            style={{
              fontFamily: SANS_FONT,
              fontSize: 116,
              fontWeight: 600,
              letterSpacing: "-0.03em",
              lineHeight: 1.06,
              color: line.muted ? COLORS.inkSoft : COLORS.ink,
              translate: interpolate(
                frame,
                [line.start, line.start + 26],
                ["0px 130px", "0px 0px"],
                {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                  easing: EASE,
                },
              ),
            }}
          >
            {line.text}
          </Interactive.Div>
        </div>
      ))}

      <Interactive.Div
        name="Rule"
        style={{
          height: 4,
          marginTop: 42,
          backgroundColor: COLORS.accent,
          width: interpolate(frame, [34, 62], [0, 220], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
        }}
      />
    </AbsoluteFill>
  );
};
