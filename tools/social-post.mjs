// Publish one post from an instagram-skill plan.json to Instagram AND the
// Facebook Page, straight through Meta's Graph API.
//
//   node tools/social-post.mjs <plan.json> <post-id> <public-base-url> [--dry-run]
//
// <public-base-url> is where the plan's media files are reachable on the web,
// e.g. https://mayurisyarntales.online/media/social/2026-11-14-intro/ (Meta
// downloads images from a URL; it cannot take local files). Each media path's
// file name is appended to it.
//
// Keys come from %USERPROFILE%\.mayuriz\meta.env (META_PAGE_ID, META_PAGE_TOKEN,
// META_IG_ID, META_IG_TOKEN); nothing secret is printed. Results are appended
// to posted.json next to the plan.
// Formats: image, carousel (2-10 images). A target may set "facebook_caption".
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const [planPath, postId, base, flag] = process.argv.slice(2);
if (!planPath || !postId || !base) {
  console.error('usage: node tools/social-post.mjs <plan.json> <post-id> <public-base-url> [--dry-run]');
  process.exit(2);
}
const DRY = flag === '--dry-run';
const G = 'https://graph.facebook.com/v23.0/';

const env = {};
for (const line of fs.readFileSync(path.join(os.homedir(), '.mayuriz', 'meta.env'), 'utf8').split(/\r?\n/)) {
  const m = line.match(/^([A-Z_]+)=(.*)$/);
  if (m) env[m[1]] = m[2].trim();
}
for (const k of ['META_PAGE_ID', 'META_PAGE_TOKEN', 'META_IG_ID', 'META_IG_TOKEN']) {
  if (!env[k]) { console.error(`${k} missing in meta.env`); process.exit(1); }
}

const plan = JSON.parse(fs.readFileSync(planPath, 'utf8'));
const post = plan.posts.find(p => p.id === postId);
if (!post) { console.error(`no post "${postId}" in plan`); process.exit(1); }
if (!['image', 'carousel'].includes(post.format)) { console.error(`format ${post.format} not supported yet`); process.exit(1); }
const urls = post.media.map(m => new URL(path.basename(m), base.endsWith('/') ? base : base + '/').href);
if (post.format === 'carousel' && (urls.length < 2 || urls.length > 10)) {
  console.error('carousel needs 2-10 images (Facebook multi-photo and Instagram API limit)'); process.exit(1);
}
const igCaption = post.caption || '';
const fbCaption = (post.targets || []).find(t => t.facebook_caption)?.facebook_caption || igCaption;

async function call(method, p, params, token) {
  const r = await fetch(G + p, {
    method, headers: { 'content-type': 'application/json' },
    body: method === 'GET' ? undefined : JSON.stringify({ ...params, access_token: token }),
  });
  const j = await r.json();
  if (j.error) throw new Error(`${p}: ${j.error.message}`);
  return j;
}
const get = async (p, token) => {
  const j = await (await fetch(`${G}${p}${p.includes('?') ? '&' : '?'}access_token=${encodeURIComponent(token)}`)).json();
  if (j.error) throw new Error(`${p}: ${j.error.message}`);
  return j;
};
const sleep = ms => new Promise(r => setTimeout(r, ms));

// every image must be reachable before Meta tries to fetch it
for (const u of urls) {
  const r = await fetch(u, { method: 'HEAD' });
  if (!r.ok || !(r.headers.get('content-type') || '').startsWith('image/')) {
    console.error(`not reachable as an image yet: ${u} (${r.status})`); process.exit(1);
  }
}
console.log(`${urls.length} image(s) reachable`);
if (DRY) { console.log('dry run: nothing posted'); process.exit(0); }

const result = { post: postId, at: new Date().toISOString() };

// Instagram
try {
  const IG = env.META_IG_ID, T = env.META_IG_TOKEN;
  let creation;
  if (urls.length === 1) {
    creation = (await call('POST', `${IG}/media`, { image_url: urls[0], caption: igCaption }, T)).id;
  } else {
    const kids = [];
    for (const u of urls) kids.push((await call('POST', `${IG}/media`, { image_url: u, is_carousel_item: true }, T)).id);
    creation = (await call('POST', `${IG}/media`, { media_type: 'CAROUSEL', children: kids.join(','), caption: igCaption }, T)).id;
  }
  for (let i = 0; i < 20; i++) {
    const s = await get(`${creation}?fields=status_code`, T);
    if (s.status_code === 'FINISHED') break;
    if (s.status_code === 'ERROR') throw new Error('Instagram could not process the media');
    await sleep(3000);
  }
  const pub = await call('POST', `${IG}/media_publish`, { creation_id: creation }, T);
  const link = (await get(`${pub.id}?fields=permalink`, T)).permalink;
  result.instagram = { id: pub.id, link };
  console.log(`Instagram: posted ${link}`);
} catch (e) { result.instagramError = e.message; console.log(`Instagram FAILED: ${e.message}`); }

// Facebook Page
try {
  const P = env.META_PAGE_ID, T = env.META_PAGE_TOKEN;
  let id;
  if (urls.length === 1) {
    id = (await call('POST', `${P}/photos`, { url: urls[0], message: fbCaption }, T)).post_id;
  } else {
    const media = [];
    for (const u of urls) media.push({ media_fbid: (await call('POST', `${P}/photos`, { url: u, published: false }, T)).id });
    id = (await call('POST', `${P}/feed`, { message: fbCaption, attached_media: media }, T)).id;
  }
  const link = `https://www.facebook.com/${id}`;
  result.facebook = { id, link };
  console.log(`Facebook: posted ${link}`);
} catch (e) { result.facebookError = e.message; console.log(`Facebook FAILED: ${e.message}`); }

const logFile = path.join(path.dirname(planPath), 'posted.json');
const log = fs.existsSync(logFile) ? JSON.parse(fs.readFileSync(logFile, 'utf8')) : [];
log.push(result);
fs.writeFileSync(logFile, JSON.stringify(log, null, 2) + '\n');
process.exit(result.instagram && result.facebook ? 0 : 1);
