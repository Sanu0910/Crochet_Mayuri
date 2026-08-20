import React from "react";
import { AbsoluteFill } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { Intro } from "./scenes/Intro";
import { Statement } from "./scenes/Statement";
import { ProductScene } from "./scenes/Product";
import { Outro } from "./scenes/Outro";
import { COLORS, PRODUCTS } from "./theme";

export const FPS = 30;
export const INTRO_FRAMES = 105;
export const STATEMENT_FRAMES = 75;
export const PRODUCT_FRAMES = 40;
export const OUTRO_FRAMES = 105;
export const TRANSITION_FRAMES = 10;

/** Every scene, minus the overlap each cross-fade eats. */
export const PROMO_DURATION =
  INTRO_FRAMES +
  STATEMENT_FRAMES +
  PRODUCT_FRAMES * PRODUCTS.length +
  OUTRO_FRAMES -
  TRANSITION_FRAMES * (PRODUCTS.length + 2);

const crossFade = (key: string) => (
  <TransitionSeries.Transition
    key={key}
    presentation={fade()}
    timing={linearTiming({ durationInFrames: 10 })}
  />
);

export const Promo: React.FC = () => {
  // TransitionSeries requires a flat sequence/transition alternation, so the
  // per-product scenes are pushed into one list rather than nested.
  const scenes: React.ReactNode[] = [
    <TransitionSeries.Sequence key="intro" durationInFrames={105} name="Intro">
      <Intro />
    </TransitionSeries.Sequence>,
    crossFade("t-intro"),
    <TransitionSeries.Sequence
      key="statement"
      durationInFrames={75}
      name="Handmade."
    >
      <Statement />
    </TransitionSeries.Sequence>,
  ];

  PRODUCTS.forEach((product, index) => {
    scenes.push(crossFade(`t-${product.image}`));
    scenes.push(
      <TransitionSeries.Sequence
        key={product.image}
        durationInFrames={40}
        name={product.name}
      >
        <ProductScene index={index} />
      </TransitionSeries.Sequence>,
    );
  });

  scenes.push(crossFade("t-outro"));
  scenes.push(
    <TransitionSeries.Sequence key="outro" durationInFrames={105} name="Outro">
      <Outro />
    </TransitionSeries.Sequence>,
  );

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.surfaceAlt }}>
      <TransitionSeries>{scenes}</TransitionSeries>
    </AbsoluteFill>
  );
};
