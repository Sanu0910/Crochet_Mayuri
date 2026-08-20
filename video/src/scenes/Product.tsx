import React from "react";
import {
  AbsoluteFill,
  CanvasImage,
  Easing,
  Interactive,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { COLORS, SANS_FONT, PRODUCTS } from "../theme";

const EASE = Easing.bezier(0.16, 1, 0.3, 1);

export type ProductSceneProps = {
  readonly index: number;
};

/**
 * One photo per scene, framed on the same warm off-white as the rest of the
 * film. The caption sits below the photo rather than on top of it, so the
 * piece itself is never covered by type. The slow push-in alternates
 * direction so a run of scenes doesn't feel mechanical.
 */
export const ProductScene: React.FC<ProductSceneProps> = ({ index }) => {
  const frame = useCurrentFrame();
  const product = PRODUCTS[index];
  const drift = index % 2 === 0 ? 1 : -1;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.surfaceAlt,
        flexDirection: "column",
        justifyContent: "center",
        padding: "0 100px",
      }}
    >
      <Interactive.Div
        name="Counter"
        style={{
          position: "absolute",
          top: 74,
          right: 100,
          fontFamily: SANS_FONT,
          fontSize: 30,
          fontWeight: 500,
          letterSpacing: "0.18em",
          color: COLORS.inkFaint,
          opacity: interpolate(frame, [2, 16], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
        }}
      >
        {String(index + 1).padStart(2, "0")} / {PRODUCTS.length}
      </Interactive.Div>

      <Interactive.Div
        name="Photo"
        style={{
          position: "relative",
          flexShrink: 0,
          width: 880,
          height: 880,
          borderRadius: 36,
          overflow: "hidden",
          backgroundColor: "#e6e1db",
          opacity: interpolate(frame, [0, 12], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
        }}
      >
        <AbsoluteFill
          style={{
            scale: interpolate(frame, [0, 40], [1.03, 1.12], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.linear,
              output: "perceptual-scale",
            }),
            translate: interpolate(
              frame,
              [0, 40],
              [`${-14 * drift}px 8px`, `${14 * drift}px -8px`],
              {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
                easing: Easing.linear,
              },
            ),
          }}
        >
          <CanvasImage
            src={staticFile(`images/${product.image}`)}
            fit="cover"
            style={{ width: "100%", height: "100%" }}
          />
        </AbsoluteFill>
      </Interactive.Div>

      <Interactive.Div
        name="Category"
        style={{
          fontFamily: SANS_FONT,
          fontSize: 30,
          fontWeight: 600,
          letterSpacing: "0.3em",
          textTransform: "uppercase",
          color: COLORS.accent,
          marginTop: 52,
          opacity: interpolate(frame, [4, 18], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
          translate: interpolate(frame, [4, 26], ["0px 24px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
        }}
      >
        {product.tag}
      </Interactive.Div>

      <Interactive.Div
        name="Product name"
        style={{
          fontFamily: SANS_FONT,
          fontSize: 66,
          fontWeight: 600,
          letterSpacing: "-0.025em",
          lineHeight: 1.1,
          color: COLORS.ink,
          marginTop: 16,
          maxWidth: 880,
          opacity: interpolate(frame, [7, 21], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
          translate: interpolate(frame, [7, 32], ["0px 30px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          }),
        }}
      >
        {product.name}
      </Interactive.Div>
    </AbsoluteFill>
  );
};
