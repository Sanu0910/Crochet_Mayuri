import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { TransitionSeries, springTiming } from "@remotion/transitions";
import { COLORS, SANS_FONT, SCRIPT_FONT } from "../theme";
import {
  CLAMP, CtaScene, Cue, DEEP, EASE_OUT, FPS, Flower, H, OfferScene, Photo, Sounds, W,
  WARM_SOFT, cream, rise, zoomThrough, type Crop,
} from "./kit";

/*
 * Reel 2 — "Something for everyone."
 *
 * Six frames in a grid, and one continuous camera: it dives into the first
 * frame, glides from frame to frame while each piece's details come up, then
 * pulls back out to all six. No cuts inside the grid — the zoom *is* the
 * transition, which is what keeps a 20-second product tour feeling like one
 * movement rather than a slideshow.
 *
 *   0.0s  hook over the whole grid: "which one's yours?"
 *   2.0s  dive into frame 1
 *   3.0s  six pieces, 2s each, gliding between
 *  18.0s  pull back out to all six
 *  20.0s  the offer, then where to go
 */

type Tile = { crop: Crop; tag: string; name: string; detail: string };

const TILES: Tile[] = [
  { crop: { file: "ocean-blue-scrunchie.jpg", focus: "47% 32%", zoom: 1.35 }, tag: "SCRUNCHIES",
    name: "Ocean Blue Scrunchie", detail: "Soft ruffles, in any colour you like." },
  { crop: { file: "caramel-cream-bow.jpg", focus: "60% 66%", zoom: 1.35 }, tag: "BOWS",
    name: "Caramel & Cream Bow", detail: "Chunky cream with a caramel edge." },
  { crop: { file: "red-rose-stem.jpg", focus: "52% 50%", zoom: 1.18 }, tag: "ROSES",
    name: "Red Rose Stem", detail: "A classic red rose that never wilts." },
  { crop: { file: "pink-bloom-claw-clip.jpg", focus: "70% 58%", zoom: 2.2 }, tag: "CLAW CLIPS",
    name: "Pink Bloom Claw Clip", detail: "A whole bloom, holding a twist of hair." },
  { crop: { file: "daisy-hanging-charm.jpg", focus: "52% 68%", zoom: 1.7 }, tag: "CHARMS",
    name: "Daisy Hanging Charm", detail: "A daisy on a stem, made to hang." },
  { crop: { file: "ruby-bow-handbag.jpg", focus: "47% 56%", zoom: 1.8 }, tag: "NEW IN BAGS",
    name: "The Ruby Bag", detail: "A zip that really closes." },
];

// ------------------------------------------------------------------ the grid, in its own space
const TILE_W = 470;
const TILE_H = 600;
const GAP = 30;
const GRID_W = TILE_W * 2 + GAP;
const GRID_H = TILE_H * 3 + GAP * 2;
const GRID_X = (W - GRID_W) / 2;
const GRID_Y = (H - GRID_H) / 2;

const tileCentre = (i: number) => ({
  x: GRID_X + (i % 2) * (TILE_W + GAP) + TILE_W / 2,
  y: GRID_Y + Math.floor(i / 2) * (TILE_H + GAP) + TILE_H / 2,
});

// ------------------------------------------------------------------ the camera
// A shot is "put this point of the grid at that point of the screen, at this
// scale". Moving between shots interpolates the point, the anchor and the
// *logarithm* of the scale — zooming in equal ratios per frame reads as an
// even speed, where interpolating the scale itself rushes the start.
type Shot = { fx: number; fy: number; ax: number; ay: number; s: number };

const OVERVIEW: Shot = { fx: W / 2, fy: H / 2, ax: W / 2, ay: 1176, s: 0.52 };
const CLOSE_S = 820 / TILE_W;                 // a frame 820px wide on screen
const close = (i: number): Shot => ({ fx: tileCentre(i).x, fy: tileCentre(i).y, ax: W / 2, ay: 762, s: CLOSE_S });
const FINALE: Shot = { fx: W / 2, fy: H / 2, ax: W / 2, ay: H / 2, s: 0.9 };

const INTRO = 60;      // hold on the whole grid under the hook
const DIVE = 30;       // into frame 1
const DWELL = 60;      // on each piece
const GLIDE = 18;      // frame to frame
const PULL = 30;       // back out to all six
const HOLD = 24;

const dwellStart = (i: number) => INTRO + DIVE + i * (DWELL + GLIDE);
const GRID_SCENE = dwellStart(TILES.length - 1) + DWELL + PULL + HOLD;

const KEYS: { at: number; shot: Shot }[] = [
  { at: 0, shot: OVERVIEW },
  { at: INTRO, shot: OVERVIEW },
  ...TILES.flatMap((_, i) => [
    { at: dwellStart(i), shot: close(i) },
    { at: dwellStart(i) + DWELL, shot: close(i) },
  ]),
  { at: dwellStart(TILES.length - 1) + DWELL + PULL, shot: FINALE },
  { at: GRID_SCENE, shot: FINALE },
];

const MOVE = Easing.bezier(0.65, 0, 0.35, 1);

const cameraAt = (frame: number): Shot => {
  for (let k = 0; k < KEYS.length - 1; k++) {
    const a = KEYS[k], b = KEYS[k + 1];
    if (frame <= b.at) {
      const t = b.at === a.at ? 1 : MOVE(Math.min(1, Math.max(0, (frame - a.at) / (b.at - a.at))));
      const mix = (x: number, y: number) => x + (y - x) * t;
      return {
        fx: mix(a.shot.fx, b.shot.fx), fy: mix(a.shot.fy, b.shot.fy),
        ax: mix(a.shot.ax, b.shot.ax), ay: mix(a.shot.ay, b.shot.ay),
        s: Math.exp(mix(Math.log(a.shot.s), Math.log(b.shot.s))),
      };
    }
  }
  return KEYS[KEYS.length - 1].shot;
};

// ------------------------------------------------------------------ the scene
const GridScene: React.FC = () => {
  const frame = useCurrentFrame();
  const cam = cameraAt(frame);
  // Category labels belong to the overview; close up, the caption below says it.
  const labels = interpolate(cam.s, [0.6, 1.1], [1, 0], CLAMP);
  const hook = 1 - rise(frame, INTRO - 4, 14);
  const finale = rise(frame, dwellStart(TILES.length - 1) + DWELL + PULL - 6, 14);

  return (
    <AbsoluteFill style={cream}>
      <div style={{ position: "absolute", left: 0, top: 0, width: W, height: H, transformOrigin: "0 0",
        // translate-then-scale is order-sensitive, so this one stays a transform string
        transform: `translate(${cam.ax - cam.s * cam.fx}px, ${cam.ay - cam.s * cam.fy}px) scale(${cam.s})` }}>
        {TILES.map((tile, i) => {
          const { x, y } = tileCentre(i);
          const pop = rise(frame, 4 + i * 4, 14);
          return (
            <div key={tile.name} style={{ position: "absolute", left: x - TILE_W / 2, top: y - TILE_H / 2,
              width: TILE_W, height: TILE_H, borderRadius: 30, overflow: "hidden", background: "#fff",
              boxShadow: "0 18px 40px rgba(60,35,25,.18)", opacity: pop,
              scale: interpolate(pop, [0, 1], [0.9, 1]) }}>
              <Photo crop={tile.crop} />
              <span style={{ position: "absolute", left: 18, bottom: 18, background: "rgba(255,255,255,.94)",
                borderRadius: 999, padding: "10px 20px", fontSize: 26, fontWeight: 700, opacity: labels }}>
                {tile.tag === "NEW IN BAGS" ? "Bags" : tile.tag.charAt(0) + tile.tag.slice(1).toLowerCase()}
              </span>
            </div>
          );
        })}
      </div>

      {/* Close up, the next row of frames sits right where the caption goes.
          A cream panel rises behind the words so they never sit on a photo. */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 1262, bottom: 0, opacity: 1 - labels,
        background: "linear-gradient(to bottom, rgba(247,241,232,0) 0px, #f7f1e8 46px)" }} />

      {/* hook, over the whole grid */}
      <div style={{ position: "absolute", top: 268, left: 0, right: 0, textAlign: "center", opacity: hook }}>
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 12, opacity: rise(frame, 0, 10) }}>
          <Flower size={46} />
          <span style={{ fontFamily: SCRIPT_FONT, fontWeight: 700, fontSize: 58, lineHeight: 1 }}>Mayuri&rsquo;z</span>
        </div>
        <div style={{ marginTop: 18, fontSize: 88, fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1,
          opacity: rise(frame, 4, 12) }}>
          Something for<br />everyone.
        </div>
        <div style={{ marginTop: 12, fontFamily: SCRIPT_FONT, fontWeight: 700, fontSize: 70, color: DEEP,
          opacity: rise(frame, 14, 12) }}>
          which one&rsquo;s yours?
        </div>
      </div>

      {/* each piece's details, while the camera rests on it */}
      {TILES.map((tile, i) => {
        const a = dwellStart(i);
        const o = interpolate(frame, [a - 2, a + 8, a + DWELL - 6, a + DWELL + 4], [0, 1, 1, 0], CLAMP);
        const lift = interpolate(frame, [a - 2, a + 12], [24, 0], { ...CLAMP, easing: EASE_OUT });
        return (
          <div key={tile.name} style={{ position: "absolute", top: 1300, left: 60, right: 60, textAlign: "center",
            opacity: o, translate: `0px ${lift}px` }}>
            <div style={{ fontSize: 26, fontWeight: 700, letterSpacing: "0.24em", color: COLORS.accent }}>
              {tile.tag} &middot; {i + 1}/{TILES.length}
            </div>
            <div style={{ marginTop: 12, fontSize: 70, fontWeight: 800, letterSpacing: "-0.035em", lineHeight: 1 }}>
              {tile.name}
            </div>
            <div style={{ marginTop: 14, fontSize: 32, color: WARM_SOFT }}>{tile.detail}</div>
          </div>
        );
      })}

      {/* the pull-back: name the whole range */}
      <div style={{ position: "absolute", top: 120, left: 0, right: 0, textAlign: "center", opacity: finale }}>
        <span style={{ display: "inline-block", marginTop: 130, background: COLORS.accent, color: "#fff",
          fontSize: 34, fontWeight: 800, letterSpacing: "0.04em", padding: "16px 32px", borderRadius: 999,
          boxShadow: "0 14px 30px rgba(200,86,74,.35)" }}>
          All handmade. All 20% off.
        </span>
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ timeline
const OFFER = 150;
const CTA = 110;
const T = 12;
export const RANGE_DURATION = GRID_SCENE + OFFER + CTA - 2 * T;

const OFFER_START = GRID_SCENE - T;
const CTA_START = OFFER_START + OFFER - T;

const CUES: Cue[] = [
  { at: INTRO - 2, sound: "whoosh", volume: 0.36 },                               // the dive
  ...TILES.slice(1).map((_, i) => ({ at: dwellStart(i) + DWELL - 2, sound: "whoosh" as const, volume: 0.26 })),
  { at: dwellStart(TILES.length - 1) + DWELL - 2, sound: "whoosh", volume: 0.34 }, // pull back
  { at: OFFER_START - 3, sound: "whoosh", volume: 0.38 },
  { at: OFFER_START + 30, sound: "ding", volume: 0.55 },
  { at: OFFER_START + 66, sound: "pop", volume: 0.45 },
  { at: CTA_START - 3, sound: "whoosh", volume: 0.3 },
];

const cut = (key: string) => (
  <TransitionSeries.Transition key={key} presentation={zoomThrough()}
    timing={springTiming({ config: { damping: 200 }, durationInFrames: T })} />
);

export const ReelRange: React.FC = () => (
  <AbsoluteFill style={{ background: "#f7f1e8", fontFamily: SANS_FONT }}>
    <TransitionSeries>
      {[
        <TransitionSeries.Sequence key="grid" durationInFrames={GRID_SCENE} premountFor={FPS} name="Grid">
          <GridScene />
        </TransitionSeries.Sequence>,
        cut("t-offer"),
        <TransitionSeries.Sequence key="offer" durationInFrames={OFFER} premountFor={FPS} name="Offer">
          <OfferScene />
        </TransitionSeries.Sequence>,
        cut("t-cta"),
        <TransitionSeries.Sequence key="cta" durationInFrames={CTA} premountFor={FPS} name="Where">
          <CtaScene />
        </TransitionSeries.Sequence>,
      ]}
    </TransitionSeries>
    <Sounds cues={CUES} />
  </AbsoluteFill>
);
