/**
 * The weekly ads are planned in Python (tools/weekly_video.py): it picks the
 * products and the music, finds the beats and snaps every scene to them. The
 * plan arrives here as props, so these components only draw what they're told.
 * All times are in frames at 30 fps, counted from the start of the video.
 */

export type AdProduct = {
  readonly id: string;
  readonly name: string;
  readonly tag: string;
  readonly desc: string;
  /** Path under public/, e.g. "weekly/new-piece-7.jpg". */
  readonly image: string;
  /** Where the piece itself sits in the photo (0..1), for close-ups. */
  readonly focus: readonly { x: number; y: number }[];
};

export type SceneKind =
  | "hook"
  | "reveal"
  | "detail"
  | "features"
  | "brand"
  | "cta"
  | "flash"
  | "collage";

export type AdScene = {
  readonly kind: SceneKind;
  readonly from: number;
  readonly duration: number;
  /** Lines of on-screen text, already final (no templating here). */
  readonly text: readonly string[];
  /** Index into plan.products. */
  readonly product?: number;
  /** For "detail": which focus point of the product to zoom into. */
  readonly focus?: number;
  readonly direction?: "left" | "right" | "up" | "down";
};

export type AdPlan = {
  readonly variant: "showcase" | "creative";
  readonly durationInFrames: number;
  readonly website: string;
  readonly email: string;
  readonly products: readonly AdProduct[];
  readonly scenes: readonly AdScene[];
  /** Every beat, in frames from the video start. */
  readonly beats: readonly number[];
  /** Strong beats (bar starts / the drop), a subset of beats. */
  readonly accents: readonly number[];
  readonly music: {
    /** Path under public/, e.g. "music/life-of-riley.mp3". Empty = silent. */
    readonly src: string;
    /** Frames to skip at the start of the track. */
    readonly trimBefore: number;
    readonly volume: number;
  };
  /** Text for the cover still (AdCover composition). */
  readonly cover: { readonly title: string; readonly kicker: string; readonly product: number };
};
