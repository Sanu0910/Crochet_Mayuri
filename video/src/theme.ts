import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Caveat and Inter are bundled into public/fonts as variable woff2 files so
// the render never depends on fetching from Google at build time.
await Promise.all([
  loadFont({
    family: "Caveat",
    url: staticFile("fonts/Caveat.woff2"),
    weight: "400 700",
    format: "woff2",
  }),
  loadFont({
    family: "Inter",
    url: staticFile("fonts/Inter.woff2"),
    weight: "100 900",
    format: "woff2",
  }),
]);

/** Brand fonts — Caveat for the "Mayuri'z" mark, Inter for everything else. */
export const SCRIPT_FONT = "Caveat, cursive";
export const SANS_FONT = "Inter, -apple-system, sans-serif";

/** Same palette as the website, so the film and the page feel like one thing. */
export const COLORS = {
  ink: "#1d1d1f",
  inkSoft: "#6e6e73",
  inkFaint: "#86868b",
  surface: "#ffffff",
  surfaceAlt: "#f6f4f1",
  accent: "#c8564a",
  petalLight: "#f2b8c6",
  petalDark: "#e58fa3",
  pollen: "#e8b23d",
  leaf: "#7d9b6a",
} as const;

export type Product = {
  readonly image: string;
  readonly name: string;
  readonly tag: string;
};

/** Mirrors the PRODUCTS list in index.html — every photo gets its own scene. */
export const PRODUCTS: readonly Product[] = [
  /* PRODUCTS:START */
  { image: "sunflower-hair-clips.jpg", name: "Sunflower Hair Clip Pair", tag: "Hair Clips" },
  { image: "sunflower-hair-clips-alt.jpg", name: "Sunflower Clips — Clip Detail", tag: "Hair Clips" },
  { image: "rose-claw-clip.jpg", name: "Blush Rose Claw Clip", tag: "Claw Clips" },
  { image: "sunflower-keychain.jpg", name: "Sunflower Bloom Keychain", tag: "Keychains" },
  { image: "sunflower-keychain-alt.jpg", name: "Sunflower Keychain, Gift Tagged", tag: "Keychains" },
  { image: "sunflower-hanging-charm.jpg", name: "Sunflower Hanging Charm", tag: "Charms" },
  { image: "sunflower-bag-charm.jpg", name: "Sunflower Bag Charm", tag: "Charms" },
  { image: "rose-keychain.jpg", name: "Rose Keychain", tag: "Keychains" },
  { image: "ocean-blue-scrunchie.jpg", name: "Ocean Blue Ruffle Scrunchie", tag: "Scrunchies" },
  { image: "blue-blossom-scrunchie.jpg", name: "Blue Blossom Scrunchie", tag: "Scrunchies" },
  { image: "tricolour-scrunchie.jpg", name: "Tricolour Ruffle Scrunchie", tag: "Scrunchies" },
  { image: "sage-cream-scrunchie.jpg", name: "Sage Bloom Scrunchie", tag: "Scrunchies" },
  { image: "ruby-rose-scrunchie.jpg", name: "Ruby Rose Scrunchie", tag: "Scrunchies" },
  { image: "rose-duo-red-pink.jpg", name: "Red & Pink Rose Duo", tag: "Roses" },
  { image: "coral-rose-stem.jpg", name: "Coral Rose Stem", tag: "Roses" },
  { image: "red-rose-stem.jpg", name: "Red Rose Stem", tag: "Roses" },
  { image: "rose-bouquet.jpg", name: "Red Rose Bouquet", tag: "Roses" },
  { image: "caramel-cream-bow.jpg", name: "Caramel & Cream Bow", tag: "Bows" },
  { image: "classic-maroon-bow.jpg", name: "Classic Maroon & Cream Bow", tag: "Bows" },
  { image: "classic-maroon-bow-alt.jpg", name: "Maroon Scallop Bow", tag: "Bows" },
  { image: "cream-bow.jpg", name: "Simple Cream Bow", tag: "Bows" },
  { image: "flower-vine-garland.jpg", name: "Yellow Flower Vine Set", tag: "Garlands" },
  { image: "mini-hearts-set.jpg", name: "Sweetheart Mini Set", tag: "Hearts" },
  /* PRODUCTS:END */
];
