import React from "react";
import { Composition, Folder } from "remotion";
import "./index.css";
import { Promo, PROMO_DURATION, FPS } from "./Promo";
import { Intro } from "./scenes/Intro";
import { Statement } from "./scenes/Statement";
import { ProductScene } from "./scenes/Product";
import { Outro } from "./scenes/Outro";

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
