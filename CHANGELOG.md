# Changelog

A short, dated record of updates to this site. Newest first.

## 2026-08-19

- Added a new product: **Sunflower Hair Clip Pair** (2 photos) — two golden sunflowers with maroon centres on alligator clips, filed under Claw Clips.
- Gave the gallery a more promotional look: product cards now carry factual badges ("New", "Set of 2", "Bouquet of 5", "Set of 4"), a "Made to order" note, and a stronger "Order this →" button. Card footers now line up across the row regardless of description length.
- Added a value-prop strip under the hero: Handmade to order · Any colour you like · Gift-ready · A personal reply.

## 2026-08-06

- Added yarn-thread flourish animations that draw in above the "Mayuri'z" name and the tagline, tying them into the flower animation below.
- Replaced the static hero heart with a new animation: two yarn threads sweep in from left/right, curl into a 6-petal flower, then the "Mayuri'z" name and tagline rise in. Fixed a bug where 5 of 6 petals were rendering on top of each other (CSS transform was overriding the SVG rotate positioning).
- Merged the full mobile redesign (see 2026-07-11 below) live to the main site.
- Added 8 new products from a fresh photo batch: Ruby Rose Scrunchie, Red Rose Stem, Red Rose Bouquet, Simple Cream Bow, Blush Rose Claw Clip, Rose Keychain, Sweetheart Mini Hearts Set — plus extra angle photos for the Sunflower Keychain and Classic Bow. Catalog is now 12 products across 6 categories (Scrunchies, Bows, Flowers & Roses, Claw Clips, Keychains, Hearts).
- Replaced the placeholder gallery photos with 5 new branded product photos (sunflower keychain, sage scrunchie, rose duo, coral rose, maroon bow) and updated the About section photo.

## 2026-07-11

- Rebuilt the gallery to render from a single product data list in code, so adding new items/photos no longer requires touching the page layout.
- Added a full-screen photo lightbox with next/prev navigation, swipe support, keyboard controls, and support for multiple photos per product.
- Added "Order this" buttons on each product that pre-fill the custom-order form with that item's details.
- Wired the order/enquiry form to email both mayurighoshblg@gmail.com and sanuroybhs@gmail.com automatically via EmailJS (falls back to opening the visitor's email app until EmailJS is configured — see SETUP.md).
- Redesigned the mobile experience: slide-in navigation drawer, floating "Order Now" button, fixed a bug where the drawer and its backdrop were being clipped by the header's blur effect.
- Added sitewide motion polish: staggered entrance animations, spring-style tap feedback on buttons, scroll-triggered gallery reveals, and a small celebration animation on successful order submission.
- Fixed several accessibility issues found in code review: keyboard access to the photo lightbox, focus trapping in the lightbox and mobile menu, and hiding decorative animations from screen readers.
- Added `SETUP.md` with EmailJS setup instructions and notes on adding new products/photos.

## 2026-06-21

- Original site created (static single-page layout with placeholder gallery content).
