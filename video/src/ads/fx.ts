import { Easing, interpolate } from "remotion";

/** Fast start, long soft landing: the "premium" ease used for most moves. */
export const EASE_OUT = Easing.bezier(0.16, 1, 0.3, 1);
/** Slow start, fast finish: for exits that whip away. */
export const EASE_IN = Easing.bezier(0.7, 0, 0.84, 0);
export const EASE_IN_OUT = Easing.bezier(0.65, 0, 0.35, 1);

/** interpolate() with clamping on both sides, which is what we want 99% of the time. */
export const lerp = (
  frame: number,
  input: readonly number[],
  output: readonly number[],
  easing: (t: number) => number = EASE_OUT,
) =>
  interpolate(frame, input as number[], output as number[], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing,
  });

/**
 * 1 on a beat, decaying to 0 over `length` frames. Drives the little "kick"
 * that makes type and the website pill breathe with the music.
 */
export const beatPulse = (frame: number, beats: readonly number[], length = 8) => {
  let last = -Infinity;
  for (const b of beats) {
    if (b <= frame) last = b;
    else break;
  }
  const since = frame - last;
  if (since < 0 || since > length) return 0;
  return Math.pow(1 - since / length, 2);
};

/** Index of the beat at or before `frame` (−1 before the first beat). */
export const beatIndex = (frame: number, beats: readonly number[]) => {
  let i = -1;
  for (let k = 0; k < beats.length; k++) {
    if (beats[k] <= frame) i = k;
    else break;
  }
  return i;
};

/** Beats that fall inside [from, from+duration), relative to `from`. */
export const localBeats = (beats: readonly number[], from: number, duration: number) =>
  beats.filter((b) => b >= from && b < from + duration).map((b) => b - from);

const OFF = 1300;

/** Offset for sliding in from / out to a side. */
export const sideOffset = (dir: "left" | "right" | "up" | "down", amount = OFF) => {
  switch (dir) {
    case "left":
      return { x: -amount, y: 0 };
    case "right":
      return { x: amount, y: 0 };
    case "up":
      return { x: 0, y: -amount };
    case "down":
      return { x: 0, y: amount };
  }
};

export const opposite = (dir: "left" | "right" | "up" | "down") =>
  ({ left: "right", right: "left", up: "down", down: "up" } as const)[dir];

/**
 * Whip move for a scene: flies in from `dir` over `inFrames`, holds with a
 * slow drift, then flies out the opposite way over the last `outFrames`.
 * Returns translation plus a blur amount tied to speed (cheap motion blur).
 */
export const whip = (
  frame: number,
  duration: number,
  dir: "left" | "right" | "up" | "down",
  inFrames = 9,
  outFrames = 6,
) => {
  const from = sideOffset(dir);
  const to = sideOffset(opposite(dir));
  const tIn = lerp(frame, [0, inFrames], [0, 1], EASE_OUT);
  const tOut = lerp(frame, [duration - outFrames, duration], [0, 1], EASE_IN);
  const x = from.x * (1 - tIn) + to.x * tOut;
  const y = from.y * (1 - tIn) + to.y * tOut;
  // Speed ≈ derivative; approximate by how far from rest we are early/late.
  const speedIn = frame < inFrames ? (1 - tIn) : 0;
  const speedOut = tOut;
  const blur = Math.max(speedIn, speedOut) * 26;
  const horizontal = dir === "left" || dir === "right";
  return { x, y, blur, horizontal };
};
