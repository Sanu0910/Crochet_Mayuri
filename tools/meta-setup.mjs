// One-off: turn the short-lived Graph API Explorer token in
// %USERPROFILE%\.mayuriz\meta.env into a Page token that does not expire,
// and find the Page id and linked Instagram account id. Writes them back
// into meta.env as META_PAGE_ID / META_PAGE_TOKEN / META_IG_ID.
// Never prints a token or the app secret.
//
//   node tools/meta-setup.mjs
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const FILE = path.join(os.homedir(), '.mayuriz', 'meta.env');
const G = 'https://graph.facebook.com/v23.0/';
const PAGE_NAME = process.env.META_PAGE_NAME || "Mayuri's Yarn Tales";

const text = fs.readFileSync(FILE, 'utf8');
const env = {};
for (const line of text.split(/\r?\n/)) {
  const m = line.match(/^([A-Z_]+)=(.*)$/);
  if (m) env[m[1]] = m[2].trim();
}
for (const k of ['META_APP_ID', 'META_APP_SECRET', 'META_USER_TOKEN']) {
  if (!env[k]) { console.error(`${k} is empty in ${FILE}`); process.exit(1); }
}

async function get(p, params) {
  const url = new URL(G + p);
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  const j = await (await fetch(url)).json();
  if (j.error) throw new Error(`${p}: ${j.error.message}`);
  return j;
}

// 1. short-lived user token -> long-lived user token (about 60 days)
const ll = await get('oauth/access_token', {
  grant_type: 'fb_exchange_token',
  client_id: env.META_APP_ID,
  client_secret: env.META_APP_SECRET,
  fb_exchange_token: env.META_USER_TOKEN,
});
// 2. a Page token fetched with a long-lived user token does not expire
const acc = await get('me/accounts', {
  access_token: ll.access_token,
  fields: 'id,name,access_token,instagram_business_account{id,username}',
});
const page = (acc.data || []).find(p => p.name === PAGE_NAME) || (acc.data || [])[0];
if (!page) { console.error('No Facebook Page visible to this token.'); process.exit(1); }

const ig = page.instagram_business_account;
const out = { META_PAGE_ID: page.id, META_PAGE_TOKEN: page.access_token, META_IG_ID: ig ? ig.id : '' };

let next = text;
for (const [k, v] of Object.entries(out)) {
  next = new RegExp(`^${k}=.*$`, 'm').test(next)
    ? next.replace(new RegExp(`^${k}=.*$`, 'm'), `${k}=${v}`)
    : next.replace(/\s*$/, `\n${k}=${v}\n`);
}
fs.writeFileSync(FILE, next);

// 3. confirm the Page token's expiry
const dbg = await get('debug_token', {
  input_token: page.access_token,
  access_token: `${env.META_APP_ID}|${env.META_APP_SECRET}`,
});
const exp = dbg.data.expires_at ? new Date(dbg.data.expires_at * 1000).toISOString().slice(0, 10) : 'never';
console.log(`Page: ${page.name} (id ${page.id})`);
console.log(`Page token saved; expires: ${exp}`);
console.log(ig ? `Instagram: @${ig.username} (id ${ig.id}) saved` : 'Instagram: NOT linked or no instagram_* permission - Facebook only for now');
