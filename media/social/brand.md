# Mayuri'z: social media brand sheet

Read by the instagram-skill before making any post (Step 1). Keep it current.

## The shop
- **Name:** Mayuri's Yarn Tales ("Mayuri'z"). Handmade crochet by Mayuri, made to order in India.
- **Website:** mayurisyarntales.online (`https://mayurisyarntales.online` on Facebook, where links are clickable)
- **Email (use on every post and poster):** hello@mayurisyarntales.online
- **Instagram:** @mayurisyarntales · maker's own account: @mystery_maygh
- **Facebook Page:** Mayuri's Yarn Tales
- **Who it's for:** people in India looking for a cute, handmade, giftable accessory or decor piece
  (scrunchies, claw clips, bows, roses and bouquets, keychains, bookmarks, coasters, bags).

## Look
- Colours: yarn rose `#e58fa3`, thread red `#c8564a` (accent), ink `#1d1d1f`, warm cream backgrounds `#f9ece4`.
- Fonts: Caveat (handwritten headlines), Inter (body).
- Logo files: `media/brand/` (logo-short-light.svg on light, profile-picture-name.png as the avatar).
- Product photos are used exactly as given (many already carry Mayuri'z branding): crop to 4:5
  only when no text is cut, otherwise fit on a blurred copy of the photo.
- Last slide template: `media/social/templates/cta.html` (logo, headline, website pill, email).

## Words
- Warm, short, honest. "Handmade", "made to order", "made just for you".
- Never invent reviews, customer counts, delivery times or prices (prices aren't on the site yet).
- Mayuri'z is not GST registered: never mention GST.
- Instagram: link in bio only once the bio has the website; max 5 hashtags.

## Posting
- Daily automatic posts: `tools/social_daily.py` (one product photo poster per post, 13:00 and 20:00 IST).
- Instagram: Graph API (keys in `.mayuriz/meta.env`).
- Facebook: WoopSocial (Meta app posts stay hidden while the MayuriZ app is unpublished).
- After each post: Telegram note to the team with links and any open to-dos.
