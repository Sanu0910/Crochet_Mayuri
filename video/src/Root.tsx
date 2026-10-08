import React from "react";
import { Composition, Folder } from "remotion";
import "./index.css";
import { Promo, PROMO_DURATION, FPS } from "./Promo";
import { Intro } from "./scenes/Intro";
import { Statement } from "./scenes/Statement";
import { ProductScene } from "./scenes/Product";
import { Outro } from "./scenes/Outro";
import { LAUNCH_DURATION, ReelLaunch } from "./reels/ReelLaunch";
import { RANGE_DURATION, ReelRange } from "./reels/ReelRange";
import { GIFTS_DURATION, ReelGifts } from "./reels/ReelGifts";
import { LAST_CHANCE_DURATION, ReelLastChance } from "./reels/ReelLastChance";

const WIDTH = 1080;
const HEIGHT = 1350;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Promo"
        component={Promo}
        durationInFrames={PROMO_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Folder name="LaunchWeekReels">
        <Composition id="ReelLaunch" component={ReelLaunch} durationInFrames={LAUNCH_DURATION}
          fps={30} width={1080} height={1920} />
        <Composition id="ReelRange" component={ReelRange} durationInFrames={RANGE_DURATION}
          fps={30} width={1080} height={1920} />
        <Composition id="ReelGifts" component={ReelGifts} durationInFrames={GIFTS_DURATION}
          fps={30} width={1080} height={1920} />
        <Composition id="ReelLastChance" component={ReelLastChance} durationInFrames={LAST_CHANCE_DURATION}
          fps={30} width={1080} height={1920} />
      </Folder>
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
