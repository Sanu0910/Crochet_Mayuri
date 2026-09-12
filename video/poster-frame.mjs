// Which frame to grab as the film's poster.
//
// The poster should show the rose bouquet, but its scene moves every time a
// product is added ahead of it, so the frame is computed rather than pinned.
import { readFileSync } from "node:fs";

const INTRO = 105, STATEMENT = 75, PRODUCT = 40, TRANSITION = 10;
const FIRST_PRODUCT_START = INTRO + STATEMENT - TRANSITION * 2;

const theme = readFileSync(new URL("./src/theme.ts", import.meta.url), "utf8");
const images = [...theme.matchAll(/image: "([^"]+)"/g)].map((m) => m[1]);

const index = images.indexOf("rose-bouquet.jpg");
const scene = index === -1 ? Math.floor(images.length / 2) : index;

// Land in the middle of the scene, clear of the cross-fades at either end.
console.log(FIRST_PRODUCT_START + (PRODUCT - TRANSITION) * scene + 18);
