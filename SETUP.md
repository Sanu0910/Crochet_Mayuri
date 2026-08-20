# Getting order & enquiry emails into both inboxes

This site has no server, so sending an automatic email when someone submits
the order/enquiry form needs a small free service called **EmailJS**. It
lets the page send an email straight from the visitor's browser, without
you running any backend.

Until you finish this setup, the form still works — it opens the visitor's
own email app pre-addressed to both `mayurighoshblg@gmail.com` and
`sanuroybhs@gmail.com`. Once EmailJS is configured, submissions send
automatically and silently to both addresses instead.

## One-time setup (~10 minutes)

1. **Create a free account** at [emailjs.com](https://www.emailjs.com/) using `mayurighoshblg@gmail.com`.

2. **Add an Email Service** (Email Services → Add New Service → Gmail) and
   connect the `mayurighoshblg@gmail.com` Gmail account. Note the **Service ID**
   it gives you.

3. **Create an Email Template** (Email Templates → Create New Template).
   - Set the **"To email"** field to:
     ```text
     mayurighoshblg@gmail.com, sanuroybhs@gmail.com
     ```
   - Set the **"Reply To"** field to `{{from_email}}` so that hitting "Reply"
     on the notification email replies straight to the customer, not to the
     Gmail account the notification was sent from.
   - In the template body, use these variables (they match what the site sends):
     `{{from_name}}`, `{{from_email}}`, `{{phone}}`, `{{category}}`,
     `{{order_type}}`, `{{product}}`, `{{details}}`
   - A simple template body works well:
     ```text
     New {{order_type}} from the website!

     Name: {{from_name}}
     Email: {{from_email}}
     Phone: {{phone}}
     Item / project type: {{category}}
     Product: {{product}}

     Details:
     {{details}}
     ```
   - Note the **Template ID**.

4. **Get your Public Key** (Account → General → Public Key).

5. Open `index.html`, find this block near the bottom of the `<script>` tag:
   ```js
   const EMAILJS_PUBLIC_KEY  = "YOUR_EMAILJS_PUBLIC_KEY";
   const EMAILJS_SERVICE_ID  = "YOUR_EMAILJS_SERVICE_ID";
   const EMAILJS_TEMPLATE_ID = "YOUR_EMAILJS_TEMPLATE_ID";
   ```
   Replace the three placeholder strings with the real Public Key, Service ID
   and Template ID from steps 2–4, save, and re-publish the site.

6. Submit a test order on the live site and confirm the email lands in both
   `mayurighoshblg@gmail.com` and `sanuroybhs@gmail.com`.

That's it — every future order or custom enquiry will email both addresses
automatically. The free EmailJS plan covers 200 emails/month, which is
comfortably enough for a small shop; you can upgrade later if needed.

### Optional: block spam submissions

The form already turns on EmailJS's free `blockHeadless` and `limitRate`
protections (blocks scripted/headless-browser submissions and throttles
rapid repeat sends), so no setup is needed for that baseline protection.

If you start seeing spam anyway, EmailJS also supports a Google reCAPTCHA
checkbox on the form. That needs its own free reCAPTCHA v2 site key from
[google.com/recaptcha](https://www.google.com/recaptcha/about/) plus a
small code change here — ask for that to be wired in if/when it's needed.

## Adding more product photos

In `index.html`, each gallery item lives in the `PRODUCTS` array inside the
`<script>` tag, for example:

```js
{
  id: 'sage-scrunchie',
  name: 'Sage Bloom Scrunchie',
  cat: 'scrunchies',
  tag: 'Scrunchies',
  desc: 'A soft moss-green and cream scrunchie with a ruffled petal edge...',
  image: 'images/sage-cream-scrunchie.jpg'
}
```

**One photo per entry.** Every photo gets its own card on the page, so a
second angle of the same item is a second entry with its own `id`, name and
description — not an extra path on the first one. The photo viewer then lets
visitors arrow across the whole gallery.

To add a photo: drop the file into the `images/` folder, copy one of the
objects above, give it a unique `id`, and pick `cat` from: `scrunchies`,
`bows`, `flowers`, `clips`, `keychains`, `hearts` (or ask for a new category
to be added to the filter row). An optional `badge: 'New'` puts a small label
on the card — keep those factual (a count, or genuinely new), not marketing
claims.

## Keeping the film in step

The promo film in the "The Film" panel is generated from the same photos.
After adding a product, add it to `video/src/theme.ts` too and re-render —
`video/README.md` has the exact commands. The site keeps working with the
old film until you do; it just won't show the new piece.
