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
  { image: "yellow-white-daisy-claw-clip.jpg", name: "Yellow & White Daisy Claw Clip", tag: "Claw Clips" },
  { image: "red-white-bloom-claw-clip.jpg", name: "Red & White Bloom Claw Clip", tag: "Claw Clips" },
  { image: "lilac-white-bloom-claw-clip.jpg", name: "Lilac & White Bloom Claw Clip", tag: "Claw Clips" },
  { image: "maroon-cream-bloom-claw-clip.jpg", name: "Maroon & Cream Bloom Claw Clip", tag: "Claw Clips" },
  { image: "pink-sage-bloom-claw-clip.jpg", name: "Pink & Sage Bloom Claw Clip", tag: "Claw Clips" },
  { image: "lime-white-bloom-claw-clip.jpg", name: "Lime & White Bloom Claw Clip", tag: "Claw Clips" },
  { image: "green-bloom-claw-clip.jpg", name: "Green Bloom Claw Clip", tag: "Claw Clips" },
  { image: "periwinkle-bloom-claw-clip.jpg", name: "Periwinkle Bloom Claw Clip", tag: "Claw Clips" },
  { image: "purple-bloom-hair-clip.jpg", name: "Purple Bloom Hair Clip", tag: "Hair Clips" },
  { image: "red-cream-heart-clips.jpg", name: "Red & Cream Heart Clips", tag: "Hair Clips" },
  { image: "pearl-heart-clips.jpg", name: "Pearl Heart Clips", tag: "Hair Clips" },
  { image: "pink-maroon-ruffle-scrunchie.jpg", name: "Pink & Maroon Ruffle Scrunchie", tag: "Scrunchies" },
  { image: "marigold-ruffle-scrunchie.jpg", name: "Marigold Ruffle Scrunchie", tag: "Scrunchies" },
  { image: "lavender-white-scrunchie.jpg", name: "Lavender & White Scrunchie", tag: "Scrunchies" },
  { image: "peach-puff-scrunchie.jpg", name: "Peach Puff Scrunchie", tag: "Scrunchies" },
  { image: "pink-frost-scrunchie.jpg", name: "Pink Frost Scrunchie", tag: "Scrunchies" },
  { image: "sunshine-scrunchie.jpg", name: "Sunshine Scrunchie", tag: "Scrunchies" },
  { image: "sky-blue-cream-scrunchie.jpg", name: "Sky Blue & Cream Scrunchie", tag: "Scrunchies" },
  { image: "caramel-chocolate-scrunchie.jpg", name: "Caramel & Chocolate Scrunchie", tag: "Scrunchies" },
  { image: "royal-blue-ruffle-scrunchie.jpg", name: "Royal Blue Ruffle Scrunchie", tag: "Scrunchies" },
  { image: "cream-maroon-scrunchie.jpg", name: "Cream & Maroon Scrunchie", tag: "Scrunchies" },
  { image: "red-white-ruffle-scrunchie.jpg", name: "Red & White Ruffle Scrunchie", tag: "Scrunchies" },
  { image: "cherry-red-frill-scrunchie.jpg", name: "Cherry Red Frill Scrunchie", tag: "Scrunchies" },
  { image: "classic-red-bow.jpg", name: "Classic Red Bow", tag: "Bows" },
  { image: "mixed-rose-bouquet.jpg", name: "Mixed Rose Bouquet", tag: "Roses" },
  { image: "red-rose-bloom.jpg", name: "Red Rose Bloom", tag: "Roses" },
  { image: "white-rose-stem.jpg", name: "White Rose Stem", tag: "Roses" },
  { image: "mini-rose-trio.jpg", name: "Mini Rose Trio", tag: "Roses" },
  { image: "violet-puff-daisy.jpg", name: "Violet Puff Daisy", tag: "Flowers" },
  { image: "evil-eye-hanging-charm.jpg", name: "Evil Eye Hanging Charm", tag: "Charms" },
  { image: "red-rose-hanging-charm.jpg", name: "Red Rose Hanging Charm", tag: "Charms" },
  { image: "sunflower-square-keychain.jpg", name: "Sunflower Square Keychain", tag: "Keychains" },
  { image: "heart-keychain-pair.jpg", name: "Heart Keychain Pair", tag: "Keychains" },
  { image: "pearl-flower-keychains.jpg", name: "Pearl Flower Keychains", tag: "Keychains" },
  { image: "sunflower-hair-clips.jpg", name: "Sunflower Hair Clip Pair", tag: "Hair Clips" },
  { image: "sunflower-hair-clips-alt.jpg", name: "Sunflower Clips — Clip Detail", tag: "Hair Clips" },
  { image: "daisy-snap-clips.jpg", name: "Daisy Snap Clip Pair", tag: "Hair Clips" },
  { image: "pink-bloom-claw-clip.jpg", name: "Pink Bloom Claw Clip", tag: "Hair Clips" },
  { image: "rose-claw-clip.jpg", name: "Blush Rose Claw Clip", tag: "Claw Clips" },
  { image: "sunflower-keychain.jpg", name: "Sunflower Bloom Keychain", tag: "Keychains" },
  { image: "sunflower-keychain-alt.jpg", name: "Sunflower Keychain, Gift Tagged", tag: "Keychains" },
  { image: "daisy-hanging-charm.jpg", name: "Daisy Hanging Charm", tag: "Charms" },
  { image: "sunflower-hanging-charm.jpg", name: "Sunflower Hanging Charm", tag: "Charms" },
  { image: "sunflower-bag-charm.jpg", name: "Sunflower Bag Charm", tag: "Charms" },
  { image: "rose-keychain.jpg", name: "Rose Keychain", tag: "Keychains" },
  { image: "peach-blossom-scrunchie.jpg", name: "Peach Blossom Scrunchie", tag: "Scrunchies" },
  { image: "cocoa-cream-scrunchie.jpg", name: "Cocoa & Cream Scrunchie", tag: "Scrunchies" },
  { image: "ocean-blue-scrunchie.jpg", name: "Ocean Blue Ruffle Scrunchie", tag: "Scrunchies" },
  { image: "blue-blossom-scrunchie.jpg", name: "Blue Blossom Scrunchie", tag: "Scrunchies" },
  { image: "tricolour-scrunchie.jpg", name: "Tricolour Ruffle Scrunchie", tag: "Scrunchies" },
  { image: "sage-cream-scrunchie.jpg", name: "Sage Bloom Scrunchie", tag: "Scrunchies" },
  { image: "ruby-rose-scrunchie.jpg", name: "Ruby Rose Scrunchie", tag: "Scrunchies" },
  { image: "golden-sunflower.jpg", name: "Golden Sunflower", tag: "Flowers" },
  { image: "rose-duo-red-pink.jpg", name: "Red & Pink Rose Duo", tag: "Roses" },
  { image: "coral-rose-stem.jpg", name: "Coral Rose Stem", tag: "Roses" },
  { image: "red-rose-stem.jpg", name: "Red Rose Stem", tag: "Roses" },
  { image: "rose-bouquet.jpg", name: "Red Rose Bouquet", tag: "Roses" },
  { image: "caramel-cream-bow.jpg", name: "Caramel & Cream Bow", tag: "Bows" },
  { image: "classic-maroon-bow.jpg", name: "Classic Maroon & Cream Bow", tag: "Bows" },
  { image: "classic-maroon-bow-alt.jpg", name: "Maroon Scallop Bow", tag: "Bows" },
  { image: "cream-bow.jpg", name: "Simple Cream Bow", tag: "Bows" },
  { image: "ruby-bow-handbag.jpg", name: "Ruby Bow Handbag", tag: "Bags" },
  { image: "flower-vine-garland.jpg", name: "Yellow Flower Vine Set", tag: "Garlands" },
  { image: "mini-hearts-set.jpg", name: "Sweetheart Mini Set", tag: "Hearts" },
  /* PRODUCTS:END */
];
