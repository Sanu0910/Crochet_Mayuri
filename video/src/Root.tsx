import React from "react";
import { Composition, Folder } from "remotion";
import "./index.css";
import { Promo, PROMO_DURATION, FPS } from "./Promo";
import { Intro } from "./scenes/Intro";
import { Statement } from "./scenes/Statement";
import { ProductScene } from "./scenes/Product";
import { Outro } from "./scenes/Outro";
import { Showcase } from "./ads/Showcase";
import { Creative } from "./ads/Creative";
import { Cover } from "./ads/Cover";
import type { AdPlan } from "./ads/types";

const WIDTH = 1080;
const HEIGHT = 1350;

/**
 * Stand-in plan so the weekly ads open in Studio. Real plans come from
 * tools/weekly_video.py via --props (after `npm run sync-assets`).
 */
const SAMPLE_PLAN: AdPlan = {
  variant: "showcase",
  durationInFrames: 300,
  website: "mayurisyarntales.online",
  email: "hello@mayurisyarntales.online",
  products: [
    {
      id: "new-piece-7",
      name: "Mini Rose Bouquet",
      tag: "Roses",
      desc: "A single red rose wrapped in cream or black and tied with a red bow.",
      image: "images/new-piece-7.jpg",
      focus: [{ x: 0.52, y: 0.52 }, { x: 0.78, y: 0.45 }],
    },
  ],
  scenes: [
    { kind: "hook", from: 0, duration: 90, text: ["Made slowly.", "Loved forever."], product: 0 },
    { kind: "reveal", from: 90, duration: 60, text: ["Mini Rose Bouquet", "Roses · Handmade"], product: 0, direction: "right" },
    { kind: "brand", from: 150, duration: 60, text: ["Every Stitch Tells a Story."] },
    { kind: "cta", from: 210, duration: 90, text: ["Find Your Handmade Favourite!", "Explore the Collection | Shop Now", "hello@mayurisyarntales.online"] },
  ],
  beats: Array.from({ length: 15 }, (_, i) => i * 21),
  accents: Array.from({ length: 4 }, (_, i) => 90 + i * 84),
  music: { src: "", trimBefore: 0, volume: 1 },
  cover: { title: "Mini Rose Bouquet", kicker: "Handmade with love", product: 0 },
};

const adMetadata = ({ props }: { props: AdPlan }) => ({ durationInFrames: props.durationInFrames });

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Folder name="Weekly-ads">
        <Composition
          id="AdShowcase"
          component={Showcase}
          defaultProps={SAMPLE_PLAN}
          calculateMetadata={adMetadata}
          durationInFrames={300}
          fps={FPS}
          width={1080}
          height={1920}
        />
        <Composition
          id="AdCreative"
          component={Creative}
          defaultProps={{ ...SAMPLE_PLAN, variant: "creative" as const }}
          calculateMetadata={adMetadata}
          durationInFrames={300}
          fps={FPS}
          width={1080}
          height={1920}
        />
        <Composition
          id="AdCover"
          component={Cover}
          defaultProps={SAMPLE_PLAN}
          durationInFrames={1}
          fps={FPS}
          width={1080}
          height={1920}
        />
      </Folder>
      <Composition
        id="Promo"
        component={Promo}
        durationInFrames={PROMO_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Folder name="Scenes">
        <Composition
          id="Intro"
          component={Intro}
          durationInFrames={105}
          fps={FPS}
          width={WIDTH}
          height={HEIGHT}
        />
        <Composition
          id="Statement"
          component={Statement}
          durationInFrames={75}
          fps={FPS}
          width={WIDTH}
          height={HEIGHT}
        />
        <Composition
          id="Product"
          component={ProductScene}
          defaultProps={{ index: 0 }}
          durationInFrames={40}
          fps={FPS}
          width={WIDTH}
          height={HEIGHT}
        />
        <Composition
          id="Outro"
          component={Outro}
          durationInFrames={105}
          fps={FPS}
          width={WIDTH}
          height={HEIGHT}
        />
      </Folder>
    </>
  );
};
