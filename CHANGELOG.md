# Changelog

A short, dated record of updates to this site. Newest first.

## 2026-08-20 (later, part 2)

- Audited the new design against the `apple-design` skill from github.com/emilkowalski/skills and closed the gaps it surfaced:
  - **Restored press feedback on every control.** The redesign had dropped it — buttons, filter pills, chevron links and photo tiles now respond on pointer-down with a 100ms `scale(0.97)`, rather than only reacting on release (which is what makes an interface read as laggy).
  - Added `font-optical-sizing: auto`.
  - Added `prefers-reduced-transparency` support — frosted surfaces become solid instead of just less blurred.
  - Added `prefers-contrast: more` support — solid fills, darker text, defined borders in place of hairlines.
  - Added the light inner top highlight to the nav bar, per the skill's translucent-toolbar recipe.

## 2026-08-20 (later)

- **Rebuilt the whole site in an Apple-style design language.** Near-monochrome interface (white / warm off-white panels, `#1d1d1f` text) so the product photos carry all the colour; very large tight-tracked headlines; full-width alternating panels with a lot of breathing room; thin 48px blurred nav; Apple's inline chevron links instead of heavy buttons; flat product tiles with no drop shadows.
- Typography moved to the system stack (SF Pro on Apple devices) with Inter as the web fallback. The Caveat script now appears only on the "Mayuri'z" brand mark, so the handmade character survives without fighting the clean layout.
- Added two full-width feature panels — Sunflower Clips and Roses — presenting one product each at large size, the way Apple leads with a hero product.
- The brand thread-red is retained as the accent/link colour, standing in for Apple's blue.
- All existing behaviour kept intact: category filters, gallery-wide photo viewer, "Order this" prefill, EmailJS order form, mobile drawer, scroll reveals, reduced-motion support.

## 2026-08-20

- Split every gallery item so **each card shows exactly one photo** — no more multi-photo sliders hidden behind a card. The gallery went from 13 cards to 18, and shots that were previously buried (gift-tagged keychain, hanging charm, bag charm, the bow's scallop detail, the sunflower clip's clip-back) are now visible on the page.
- Reworked the photo viewer to match: opening any photo now lets you arrow through the whole gallery instead of dead-ending on one image, and it respects whichever category filter is active (e.g. filtered to Bows, you browse 1/3).

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
