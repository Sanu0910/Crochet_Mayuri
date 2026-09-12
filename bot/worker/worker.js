/**
 * The always-awake half of the uploader.
 *
 * GitHub Actions only exists in bursts, so a bot built on it alone can't
 * answer until the next burst. This Worker does sit there permanently: it
 * takes the message from Telegram, answers straight away, and hands the slow
 * work (resize, edit, commit, push) to GitHub.
 *
 *   photo → Worker: 👀 + "Got it" in under a second
 *                 → GitHub: the actual publishing, ~30 seconds
 *
 * Deploy this in the Cloudflare dashboard and give it three secrets:
 *   TELEGRAM_TOKEN   from @BotFather
 *   GITHUB_TOKEN     fine-grained PAT, Contents: read and write, this repo
 *   WEBHOOK_SECRET   any long random string; Telegram sends it back so we
 *                    know a request really came from Telegram
 * and two plain variables:
 *   GITHUB_REPO      Sanu0910/Crochet_Mayuri
 *   ALLOWED_USER_IDS 924868395,5770732970
 *
 * See bot/README.md for the four setup steps.
 */

const TELEGRAM = "https://api.telegram.org";

async function telegram(env, method, body) {
  try {
    const response = await fetch(`${TELEGRAM}/bot${env.TELEGRAM_TOKEN}/${method}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    return await response.json();
  } catch (err) {
    // Telling someone something went wrong is never worth failing the
    // request over — Telegram would just redeliver the whole update.
    console.error(`${method} failed`, err);
    return null;
  }
}

/** Ask GitHub to run the uploader now, carrying this one update with it. */
async function dispatch(env, update) {
  const response = await fetch(
    `https://api.github.com/repos/${env.GITHUB_REPO}/dispatches`,
    {
      method: "POST",
      headers: {
        authorization: `Bearer ${env.GITHUB_TOKEN}`,
        accept: "application/vnd.github+json",
        "content-type": "application/json",
        "user-agent": "mayuriz-uploader",
      },
      body: JSON.stringify({
        event_type: "telegram",
        client_payload: { update },
      }),
    },
  );
  if (!response.ok) {
    console.error("dispatch failed", response.status, await response.text());
  }
  return response.ok;
}

export default {
  async fetch(request, env, ctx) {
    if (request.method !== "POST") {
      return new Response("Mayuri'z uploader is listening.", { status: 200 });
    }
    // Telegram echoes this header back on every delivery. Without the check,
    // anyone who found the URL could publish to the shop.
    if (
      env.WEBHOOK_SECRET &&
      request.headers.get("X-Telegram-Bot-Api-Secret-Token") !== env.WEBHOOK_SECRET
    ) {
      return new Response("no", { status: 401 });
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response("ok");
    }

    const message = update.message || update.channel_post;
    if (!message) return new Response("ok");

    const allowed = (env.ALLOWED_USER_IDS || "")
      .split(",")
      .map((id) => id.trim())
      .filter(Boolean);
    const from = String(message.from?.id ?? "");

    if (allowed.length && !allowed.includes(from)) {
      await telegram(env, "sendMessage", {
        chat_id: message.chat.id,
        text:
          "You're not on this bot's list, so I can't publish for you.\n" +
          `Your user ID: ${from}`,
        reply_to_message_id: message.message_id,
        allow_sending_without_reply: true,
      });
      return new Response("ok");
    }

    // The whole point: say something immediately, before the slow half starts.
    if (message.photo) {
      ctx.waitUntil(
        telegram(env, "setMessageReaction", {
          chat_id: message.chat.id,
          message_id: message.message_id,
          reaction: [{ type: "emoji", emoji: "👀" }],
        }),
      );
    }

    const started = await dispatch(env, update);
    if (!started) {
      await telegram(env, "sendMessage", {
        chat_id: message.chat.id,
        text:
          "⚠️ I couldn't reach GitHub to publish that. The message is safe — " +
          "try again in a minute.",
        reply_to_message_id: message.message_id,
        allow_sending_without_reply: true,
      });
    }

    // Always 200: a non-200 makes Telegram redeliver the same update forever.
    return new Response("ok");
  },
};
