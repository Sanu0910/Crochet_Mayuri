import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import type { AdPlan, AdScene } from "./types";
import { BRAND, Finish, Logo, Photo, RiseWords, SANS, SCRIPT, SERIF, Thread, WebsitePill } from "./common";
import { EASE_IN, EASE_OUT, beatIndex, beatPulse, lerp, localBeats, whip } from "./fx";

/**
 * Video 2: fast, playful, gift-minded. Bold sans type that lands on the beat,
 * polaroid product cards whipping in from alternating sides, a gift collage,
 * a brand sting and a punchy red call to action.
 */
export const Creative: React.FC<AdPlan> = (plan) => (
  <AbsoluteFill style={{ backgroundColor: BRAND.rose }}>
    {plan.scenes.map((s, i) => (
      <Sequence key={i} from={s.from} durationInFrames={s.duration} name={`${s.kind} ${i}`}>
        <Scene scene={s} plan={plan} />
      </Sequence>
    ))}
    <Finish vignette={0.2} />
    {plan.music.src ? (
      <Audio
        src={staticFile(plan.music.src)}
        trimBefore={plan.music.trimBefore}
        volume={(f) =>
          plan.music.volume *
          interpolate(f, [0, 3, plan.durationInFrames - 36, plan.durationInFrames], [0, 1, 1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })
        }
      />
    ) : null}
  </AbsoluteFill>
);

type P = { scene: AdScene; plan: AdPlan };

const Scene: React.FC<P> = (props) => {
  switch (props.scene.kind) {
    case "hook":
      return <Hook {...props} />;
    case "flash":
      return <Flash {...props} />;
    case "collage":
      return <Collage {...props} />;
    case "brand":
      return <Sting {...props} />;
    case "cta":
      return <Cta {...props} />;
    default:
      return null;
  }
};

const BG = [BRAND.cream, BRAND.roseLight, "#fbe3c8", "#e3ecd9", "#f7d6dc", "#efe4f4"];
const HOOK_BG = [BRAND.cream, BRAND.rose, BRAND.red, BRAND.cream];
const HOOK_FG = [BRAND.red, BRAND.white, BRAND.cream, BRAND.ink];

/** Opening: one word-line per beat, background flips colour on each hit. */
const Hook: React.FC<P> = ({ scene, plan }) => {
  const frame = useCurrentFrame();
  const beats = localBeats(plan.beats, scene.from, scene.duration);
  const marks = [0, ...beats.filter((b) => b > 2)].slice(0, scene.text.length);
  const shown = Math.max(0, beatIndex(frame, marks));
  const p = plan.products[0];
  return (
    <AbsoluteFill style={{ backgroundColor: HOOK_BG[shown % HOOK_BG.length], justifyContent: "center", alignItems: "center" }}>
      {/* peek of a product in the corner, so the first frame already shows crochet */}
      <div
        style={{
          position: "absolute",
          right: -80,
          bottom: 240,
          width: 520,
          height: 640,
          borderRadius: 40,
          overflow: "hidden",
          transform: `rotate(${10 - frame * 0.15}deg) translateY(${lerp(frame, [0, 12], [300, 0])}px)`,
          boxShadow: "0 40px 80px rgba(0,0,0,0.22)",
          border: `12px solid ${BRAND.white}`,
        }}
      >
        <Photo src={p.image} focus={p.focus[0]} zoom={1.35} />
      </div>
      <div style={{ position: "absolute", top: 420, left: 80, right: 80, display: "flex", flexDirection: "column", gap: 4 }}>
        {scene.text.map((line, i) => {
          const at = marks[i] ?? 9999;
          const pop = lerp(frame, [at, at + 7], [0, 1], EASE_OUT);
          return (
            <div
              key={i}
              style={{
                fontFamily: SANS,
                fontWeight: 900,
                fontSize: i === 2 ? 150 : 124,
                lineHeight: 0.98,
                letterSpacing: "-0.04em",
                textTransform: "uppercase",
                color: i === shown ? HOOK_FG[shown % HOOK_FG.length] : BRAND.ink,
                opacity: pop,
                transform: `scale(${1.5 - 0.5 * pop}) rotate(${(1 - pop) * (i % 2 ? 6 : -6)}deg)`,
                transformOrigin: "left center",
                textShadow: i === shown ? "0 10px 40px rgba(0,0,0,0.12)" : "none",
                mixBlendMode: "normal",
              }}
            >
              {line}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/** One product: polaroid whips in, settles, kicks on the beat, whips out. */
const Flash: React.FC<P> = ({ scene, plan }) => {
  const frame = useCurrentFrame();
  const i = scene.product ?? 0;
  const p = plan.products[i];
  const d = scene.duration;
  const dir = scene.direction ?? (i % 2 ? "left" : "right");
  const w = whip(frame, d, dir, 8, 5);
  const beats = localBeats(plan.beats, scene.from, d);
  const kick = beatPulse(frame, beats, 7);
  const tilt = (i % 2 ? 3.5 : -3.5) * lerp(frame, [0, 10], [3, 1]);
  const bgWord = p.tag.toUpperCase();
  const total = plan.products.length;
  return (
    <AbsoluteFill style={{ backgroundColor: BG[i % BG.length], overflow: "hidden" }}>
      {/* giant outlined category word drifting behind: cheap parallax depth */}
      <div
        style={{
          position: "absolute",
          top: 180,
          whiteSpace: "nowrap",
          fontFamily: SANS,
          fontWeight: 900,
          fontSize: 300,
          letterSpacing: "-0.04em",
          color: "transparent",
          WebkitTextStroke: `3px ${BRAND.red}`,
          opacity: 0.22,
          transform: `translateX(${(i % 2 ? -1 : 1) * (200 - frame * 9)}px)`,
        }}
      >
        {bgWord} {bgWord}
      </div>
      <div
        style={{
          position: "absolute",
          top: 1420,
          whiteSpace: "nowrap",
          fontFamily: SANS,
          fontWeight: 900,
          fontSize: 220,
          color: "transparent",
          WebkitTextStroke: `3px ${BRAND.rose}`,
          opacity: 0.3,
          transform: `translateX(${(i % 2 ? 1 : -1) * (300 - frame * 6)}px)`,
        }}
      >
        HANDMADE · HANDMADE
      </div>

      <div
        style={{
          position: "absolute",
          top: 300,
          left: 150,
          width: 780,
          padding: "26px 26px 0",
          backgroundColor: BRAND.white,
          borderRadius: 18,
          boxShadow: "0 50px 100px rgba(60,20,20,0.28)",
          transform: `translate(${w.x}px, ${w.y}px) rotate(${tilt}deg) scale(${1 + kick * 0.035})`,
          filter: `blur(${w.blur}px)`,
        }}
      >
        <div style={{ width: 728, height: 900, borderRadius: 8, overflow: "hidden" }}>
          <Photo src={p.image} zoom={1.02 + frame * 0.003} />
        </div>
        <div
          style={{
            height: 150,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: SCRIPT,
            fontWeight: 700,
            fontSize: 70,
            color: BRAND.ink,
            textAlign: "center",
            lineHeight: 0.95,
            padding: "0 20px",
          }}
        >
          {scene.text[0] ?? p.name}
        </div>
      </div>

      {/* sticker with the category */}
      <div
        style={{
          position: "absolute",
          top: 250,
          right: 90,
          padding: "16px 30px",
          borderRadius: 999,
          backgroundColor: BRAND.red,
          color: BRAND.white,
          fontFamily: SANS,
          fontWeight: 800,
          fontSize: 34,
          letterSpacing: "0.06em",
          textTransform: "uppercase",
          transform: `rotate(8deg) scale(${lerp(frame, [5, 11], [0, 1], EASE_OUT) * (1 + kick * 0.08)})`,
          boxShadow: "0 12px 30px rgba(200,86,74,0.35)",
        }}
      >
        {p.tag}
      </div>
      <div
        style={{
          position: "absolute",
          top: 120,
          left: 90,
          fontFamily: SANS,
          fontWeight: 800,
          fontSize: 34,
          letterSpacing: "0.2em",
          color: BRAND.ink,
          opacity: 0.75,
        }}
      >
        {String(i + 1).padStart(2, "0")}
        <span style={{ opacity: 0.45 }}> / {String(total).padStart(2, "0")}</span>
      </div>
    </AbsoluteFill>
  );
};

/** All the week's pieces pop into a grid, then the gifting line lands on a ribbon. */
const Collage: React.FC<P> = ({ scene, plan }) => {
  const frame = useCurrentFrame();
  const beats = localBeats(plan.beats, scene.from, scene.duration);
  const half = beats.length > 1 ? (beats[1] - beats[0]) / 2 : 8;
  const items = plan.products.slice(0, 6);
  const ribbonAt = Math.round(half * items.length) + 2;
  const ribbon = lerp(frame, [ribbonAt, ribbonAt + 9], [0, 1], EASE_OUT);
  const kick = beatPulse(frame, beats, 8);
  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.cream }}>
      <div style={{ position: "absolute", top: 170, left: 60, right: 60, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 30 }}>
        {items.map((p, i) => {
          const at = Math.round(i * half);
          const s = lerp(frame, [at, at + 8], [0, 1], EASE_OUT);
          return (
            <div
              key={p.id}
              style={{
                height: 480,
                borderRadius: 24,
                overflow: "hidden",
                border: `8px solid ${BRAND.white}`,
                boxShadow: "0 24px 50px rgba(70,30,20,0.18)",
                transform: `scale(${0.4 + 0.6 * s}) rotate(${(1 - s) * (i % 2 ? 12 : -12) + (i % 2 ? 1.5 : -1.5)}deg)`,
                opacity: s,
              }}
            >
              <Photo src={p.image} focus={p.focus[0]} zoom={1.15} />
            </div>
          );
        })}
      </div>
      <div
        style={{
          position: "absolute",
          top: 760,
          left: -40,
          right: -40,
          padding: "46px 0 54px",
          backgroundColor: BRAND.red,
          transform: `rotate(-4deg) scaleX(${ribbon}) scale(${1 + kick * 0.02})`,
          boxShadow: "0 30px 70px rgba(120,30,20,0.35)",
          textAlign: "center",
          color: BRAND.white,
        }}
      >
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 92, letterSpacing: "-0.03em", textTransform: "uppercase", lineHeight: 1 }}>
          {scene.text[0]}
        </div>
        <div style={{ fontFamily: SCRIPT, fontWeight: 700, fontSize: 92, lineHeight: 1, marginTop: 6 }}>{scene.text[1]}</div>
      </div>
    </AbsoluteFill>
  );
};

/** Brand sting: the logo springs in on the accent, tagline types in below. */
const Sting: React.FC<P> = ({ scene, plan }) => {
  const frame = useCurrentFrame();
  const beats = localBeats(plan.beats, scene.from, scene.duration);
  const kick = beatPulse(frame, beats, 9);
  const pop = lerp(frame, [0, 10], [0, 1], EASE_OUT);
  const d = scene.duration;
  const exit = lerp(frame, [d - 5, d], [0, 1], EASE_IN);
  const dots = [BRAND.rose, BRAND.red, BRAND.pollen, BRAND.leaf, BRAND.roseLight];
  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.cream, justifyContent: "center", alignItems: "center" }}>
      {dots.map((c, i) => {
        const a = (i / dots.length) * Math.PI * 2 + frame * 0.03;
        const r = 420 + kick * 30;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: 540 + Math.cos(a) * r - 50,
              top: 860 + Math.sin(a) * r * 1.2 - 50,
              width: 100,
              height: 100,
              borderRadius: 50,
              backgroundColor: c,
              opacity: 0.85 * pop,
              transform: `scale(${pop * (0.8 + kick * 0.3)})`,
            }}
          />
        );
      })}
      <div style={{ transform: `scale(${(0.6 + 0.4 * pop) * (1 + kick * 0.04) * (1 - exit * 0.3)})`, opacity: 1 - exit, marginTop: -120 }}>
        <Logo kind="short" tone="light" width={760} />
      </div>
      <div style={{ marginTop: 50, opacity: 1 - exit }}>
        <RiseWords
          text={scene.text[0] ?? "Every Stitch Tells a Story."}
          start={8}
          stagger={3}
          style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 500, fontSize: 72, color: BRAND.ink }}
        />
      </div>
      <div style={{ marginTop: 10, opacity: 1 - exit }}>
        <Thread start={18} width={460} />
      </div>
      {scene.text[1] ? (
        <div
          style={{
            marginTop: 26,
            fontFamily: SANS,
            fontWeight: 700,
            fontSize: 32,
            letterSpacing: "0.2em",
            textTransform: "uppercase",
            color: BRAND.red,
            opacity: lerp(frame, [22, 32], [0, 1]) * (1 - exit),
          }}
        >
          {scene.text[1]}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

/** Red call to action: words slam in on the beats, website pill kicks, product strip scrolls. */
const Cta: React.FC<P> = ({ scene, plan }) => {
  const frame = useCurrentFrame();
  const beats = localBeats(plan.beats, scene.from, scene.duration);
  const words = (scene.text[0] ?? "Find Your Handmade Favourite!").split(" ");
  const strip = [...plan.products, ...plan.products, ...plan.products];
  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.red, alignItems: "center" }}>
      <div style={{ position: "absolute", top: 300, left: 80, right: 80, display: "flex", flexWrap: "wrap", columnGap: 26 }}>
        {words.map((w, i) => {
          const at = beats[i] !== undefined && beats[i] < 30 ? beats[i] : i * 5;
          const s = lerp(frame, [at, at + 6], [0, 1], EASE_OUT);
          return (
            <span
              key={i}
              style={{
                fontFamily: SANS,
                fontWeight: 900,
                fontSize: 128,
                lineHeight: 1.02,
                letterSpacing: "-0.04em",
                textTransform: "uppercase",
                color: i === 2 ? BRAND.cream : BRAND.white,
                fontStyle: i === 2 ? "italic" : "normal",
                opacity: s,
                transform: `translateY(${(1 - s) * 60}px) scale(${1.3 - 0.3 * s})`,
                display: "inline-block",
              }}
            >
              {w}
            </span>
          );
        })}
      </div>
      <div style={{ position: "absolute", top: 930, opacity: lerp(frame, [18, 26], [0, 1]), transform: `translateY(${lerp(frame, [18, 30], [40, 0])}px)` }}>
        <WebsitePill website={plan.website} beats={beats} size={50} bg={BRAND.white} fg={BRAND.red} style={{ boxShadow: "0 24px 60px rgba(80,10,10,0.35)" }} />
      </div>
      <div
        style={{
          position: "absolute",
          top: 1080,
          fontFamily: SANS,
          fontWeight: 700,
          fontSize: 38,
          color: BRAND.cream,
          letterSpacing: "0.04em",
          opacity: lerp(frame, [26, 34], [0, 1]),
        }}
      >
        {scene.text[1]}
      </div>
      <div style={{ position: "absolute", top: 1145, fontFamily: SANS, fontSize: 30, color: "rgba(255,255,255,0.85)", opacity: lerp(frame, [30, 38], [0, 1]) }}>
        {scene.text[2]}
      </div>
      <div
        style={{
          position: "absolute",
          top: 1250,
          left: 0,
          display: "flex",
          gap: 22,
          transform: `translateX(${-frame * 6}px)`,
          opacity: lerp(frame, [10, 20], [0, 1]),
        }}
      >
        {strip.map((p, i) => (
          <div key={i} style={{ flexShrink: 0, width: 220, height: 260, borderRadius: 20, overflow: "hidden", border: `6px solid ${BRAND.white}` }}>
            <Photo src={p.image} focus={p.focus[0]} zoom={1.2} />
          </div>
        ))}
      </div>
      <div style={{ position: "absolute", top: 150, opacity: lerp(frame, [4, 12], [0, 1]) }}>
        <Logo kind="short" tone="mono-white" width={300} />
      </div>
    </AbsoluteFill>
  );
};
