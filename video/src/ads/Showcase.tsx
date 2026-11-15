import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import type { AdPlan, AdScene } from "./types";
import {
  BRAND,
  Backdrop,
  Finish,
  H,
  LightSweep,
  Logo,
  Photo,
  RiseWords,
  SANS,
  SERIF,
  Thread,
  WebsitePill,
} from "./common";
import { EASE_IN, EASE_IN_OUT, EASE_OUT, beatPulse, lerp, localBeats, sideOffset } from "./fx";

/**
 * Video 1: product-focused premium ad. Cream, serif, unhurried: one hero
 * piece revealed on the music's drop, then macro close-ups, what makes it
 * special, the brand, and the call to action.
 */
export const Showcase: React.FC<AdPlan> = (plan) => {
  const frame = useCurrentFrame();
  const hero = plan.products[0];
  const reveal = plan.scenes.find((s) => s.kind === "reveal");
  const brand = plan.scenes.find((s) => s.kind === "brand");
  const chromeIn = reveal ? reveal.from + 10 : 0;
  const chromeOut = brand ? brand.from : plan.durationInFrames;
  const chrome =
    lerp(frame, [chromeIn, chromeIn + 12], [0, 1]) * lerp(frame, [chromeOut - 6, chromeOut], [1, 0]);

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.cream }}>
      <Backdrop src={hero.image} />
      {plan.scenes.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={s.duration} name={`${s.kind} ${i}`}>
          <Scene scene={s} plan={plan} />
        </Sequence>
      ))}

      {/* Same logo spot and website line on every product shot. */}
      <AbsoluteFill style={{ opacity: chrome, pointerEvents: "none" }}>
        <div style={{ position: "absolute", top: 104, width: "100%", display: "flex", justifyContent: "center" }}>
          <Logo kind="short" tone="light" width={290} />
        </div>
        <div style={{ position: "absolute", top: 1520, width: "100%", display: "flex", justifyContent: "center" }}>
          <WebsitePill
            website={plan.website}
            size={32}
            bg="rgba(255,255,255,0.82)"
            fg={BRAND.ink}
            style={{ boxShadow: "0 10px 30px rgba(60,30,20,0.12)" }}
          />
        </div>
      </AbsoluteFill>

      <Finish />
      {plan.music.src ? (
        <Audio
          src={staticFile(plan.music.src)}
          trimBefore={plan.music.trimBefore}
          volume={(f) =>
            plan.music.volume *
            interpolate(f, [0, 6, plan.durationInFrames - 36, plan.durationInFrames], [0, 1, 1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })
          }
        />
      ) : null}
    </AbsoluteFill>
  );
};

const Scene: React.FC<{ scene: AdScene; plan: AdPlan }> = ({ scene, plan }) => {
  switch (scene.kind) {
    case "hook":
      return <Hook scene={scene} plan={plan} />;
    case "reveal":
      return <Reveal scene={scene} plan={plan} />;
    case "detail":
      return <Detail scene={scene} plan={plan} />;
    case "features":
      return <Features scene={scene} plan={plan} />;
    case "brand":
      return <Brand scene={scene} plan={plan} />;
    case "cta":
      return <Cta scene={scene} plan={plan} />;
    default:
      return null;
  }
};

type P = { scene: AdScene; plan: AdPlan };

/** 0–3 s: blurred macro of the stitches, the hook line, then a speed-ramp into the drop. */
const Hook: React.FC<P> = ({ scene, plan }) => {
  const frame = useCurrentFrame();
  const d = scene.duration;
  const p = plan.products[scene.product ?? 0];
  // Speed ramp: slow creep, then the zoom accelerates into the cut.
  const zoom = 2.1 + lerp(frame, [0, d - 10], [0, 0.25], (t) => t) + lerp(frame, [d - 10, d], [0, 0.9], EASE_IN);
  const blur = lerp(frame, [0, d * 0.7], [18, 6]) + lerp(frame, [d - 8, d], [0, 22], EASE_IN);
  const flash = lerp(frame, [d - 4, d], [0, 1], EASE_IN);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ filter: `blur(${blur}px) brightness(1.05)` }}>
        <Photo src={p.image} focus={p.focus[0]} zoom={zoom} />
      </AbsoluteFill>
      <AbsoluteFill style={{ backgroundColor: BRAND.cream, opacity: 0.62 }} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 90px", gap: 10 }}>
        <RiseWords
          text={scene.text[0] ?? ""}
          start={3}
          stagger={4}
          style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 104, lineHeight: 1.06, color: BRAND.ink, textAlign: "center" }}
        />
        {scene.text[1] ? (
          <RiseWords
            text={scene.text[1]}
            start={18}
            stagger={4}
            style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 500, fontSize: 104, lineHeight: 1.06, color: BRAND.red, textAlign: "center" }}
          />
        ) : null}
        <div style={{ marginTop: 26 }}>
          <Thread start={26} width={360} />
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{ backgroundColor: "#fff", opacity: flash }} />
    </AbsoluteFill>
  );
};

/** 3–8 s: the drop. Card whips in from the side, lands, sheen, name rises. */
const Reveal: React.FC<P> = ({ scene, plan }) => {
  const frame = useCurrentFrame();
  const p = plan.products[scene.product ?? 0];
  const dir = scene.direction ?? "right";
  const off = sideOffset(dir, 1250);
  const t = lerp(frame, [0, 14], [0, 1], EASE_OUT);
  const flash = lerp(frame, [0, 6], [0.9, 0]);
  const beats = localBeats(plan.accents, scene.from, scene.duration);
  const kick = beatPulse(frame, beats, 10);
  const d = scene.duration;
  const exit = lerp(frame, [d - 7, d], [0, 1], EASE_IN);
  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <div
        style={{
          position: "absolute",
          top: 300,
          width: 840,
          height: 1050,
          borderRadius: 34,
          overflow: "hidden",
          boxShadow: "0 60px 120px rgba(70,30,20,0.28), 0 18px 40px rgba(70,30,20,0.18)",
          transform: `translate(${off.x * (1 - t)}px, ${off.y * (1 - t) - exit * 140}px) rotate(${(1 - t) * (dir === "left" ? -9 : 9)}deg) scale(${1.08 - 0.08 * t + kick * 0.025 - exit * 0.08})`,
          filter: `blur(${(1 - t) * 24 + exit * 10}px)`,
          opacity: 1 - exit,
        }}
      >
        <AbsoluteFill style={{ transform: `scale(${1.04 + frame * 0.0012})` }}>
          <Photo src={p.image} />
        </AbsoluteFill>
        <LightSweep at={16} length={26} />
      </div>
      <div style={{ position: "absolute", top: 1380, width: "100%", textAlign: "center", opacity: 1 - exit }}>
        <div
          style={{
            fontFamily: SANS,
            fontSize: 28,
            fontWeight: 650,
            letterSpacing: "0.32em",
            textTransform: "uppercase",
            color: BRAND.red,
            opacity: lerp(frame, [12, 22], [0, 1]),
            transform: `translateY(${lerp(frame, [12, 26], [20, 0])}px)`,
          }}
        >
          {scene.text[1]}
        </div>
        <RiseWords
          text={scene.text[0] ?? p.name}
          start={14}
          stagger={3}
          style={{ marginTop: 10, fontFamily: SERIF, fontWeight: 600, fontSize: 78, color: BRAND.ink, padding: "0 80px", lineHeight: 1.08 }}
        />
      </div>
      <AbsoluteFill style={{ backgroundColor: "#fff", opacity: flash }} />
    </AbsoluteFill>
  );
};

/** Macro close-up on the stitches. Full-bleed, slow push, kick on the strong beat. */
const Detail: React.FC<P> = ({ scene, plan }) => {
  const frame = useCurrentFrame();
  const p = plan.products[scene.product ?? 0];
  const focus = p.focus[scene.focus ?? 0] ?? p.focus[0];
  const d = scene.duration;
  const dir = scene.direction ?? "up";
  const off = sideOffset(dir, 1920);
  const tIn = lerp(frame, [0, 10], [0, 1], EASE_OUT);
  const beats = localBeats(plan.accents, scene.from, d);
  const kick = beatPulse(frame, beats, 10);
  // Tight enough that poster-style photos show crochet, not their lettering.
  const zoom = lerp(frame, [0, d], [1.85, 2.1], EASE_IN_OUT) + kick * 0.04;
  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.cream }}>
      <AbsoluteFill
        style={{
          transform: `translate(${off.x * (1 - tIn)}px, ${off.y * (1 - tIn)}px)`,
          filter: `blur(${(1 - tIn) * 20}px)`,
        }}
      >
        <Photo src={p.image} focus={focus} zoom={zoom} />
        <AbsoluteFill
          style={{ background: "linear-gradient(180deg, rgba(249,236,228,0.0) 55%, rgba(40,20,15,0.55) 100%)" }}
        />
      </AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: 80,
          right: 80,
          top: 1180,
          color: "#fff",
          textShadow: "0 4px 24px rgba(0,0,0,0.35)",
        }}
      >
        <div
          style={{
            display: "inline-block",
            fontFamily: SANS,
            fontSize: 26,
            fontWeight: 650,
            letterSpacing: "0.3em",
            textTransform: "uppercase",
            padding: "12px 22px",
            borderRadius: 999,
            background: "rgba(255,255,255,0.18)",
            border: "1.5px solid rgba(255,255,255,0.5)",
            backdropFilter: "blur(10px)",
            opacity: lerp(frame, [6, 14], [0, 1]),
          }}
        >
          {scene.text[0]}
        </div>
        <div
          style={{
            marginTop: 22,
            fontFamily: SERIF,
            fontStyle: "italic",
            fontWeight: 500,
            fontSize: 70,
            lineHeight: 1.1,
            opacity: lerp(frame, [9, 19], [0, 1]),
            transform: `translateX(${lerp(frame, [9, 24], [-40, 0])}px)`,
          }}
        >
          {scene.text[1]}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** What it is and why it's special: card up top, three lines landing on the beats. */
const Features: React.FC<P> = ({ scene, plan }) => {
  const frame = useCurrentFrame();
  const p = plan.products[scene.product ?? 0];
  const beats = localBeats(plan.beats, scene.from, scene.duration);
  const t = lerp(frame, [0, 12], [0, 1]);
  const d = scene.duration;
  const exit = lerp(frame, [d - 6, d], [0, 1], EASE_IN);
  const ICONS = [
    "M12 21s-7.5-4.6-9.6-9.2C.9 8.4 3 4.5 6.6 4.5c2.1 0 3.6 1.2 5.4 3.2 1.8-2 3.3-3.2 5.4-3.2 3.6 0 5.7 3.9 4.2 7.3C19.5 16.4 12 21 12 21z",
    "M4 20l7-7M15.5 4.5a4 4 0 1 1-5.7 5.7 4 4 0 0 1 5.7-5.7zM13 13l7 7",
    "M3 11h18v10H3zM12 11v10M2 7h20v4H2zM12 7c-2-4-6-4-6-1.5S10 7 12 7zm0 0c2-4 6-4 6-1.5S14 7 12 7z",
  ];
  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.cream, opacity: 1 - exit }}>
      <div
        style={{
          position: "absolute",
          top: 260,
          left: 140,
          width: 800,
          height: 640,
          borderRadius: 30,
          overflow: "hidden",
          boxShadow: "0 40px 90px rgba(70,30,20,0.22)",
          transform: `translateY(${(1 - t) * -60}px) scale(${0.94 + 0.06 * t})`,
          opacity: t,
        }}
      >
        <Photo src={p.image} focus={p.focus[0]} zoom={1.25 + frame * 0.002} />
      </div>
      <div style={{ position: "absolute", top: 960, left: 110, right: 90, display: "flex", flexDirection: "column", gap: 34 }}>
        {scene.text.map((line, i) => {
          const at = beats[i] ?? 4 + i * 8;
          const s = lerp(frame, [at, at + 12], [0, 1]);
          return (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 30,
                opacity: s,
                transform: `translateX(${(1 - s) * -90}px)`,
                filter: `blur(${(1 - s) * 8}px)`,
              }}
            >
              <div
                style={{
                  flexShrink: 0,
                  width: 88,
                  height: 88,
                  borderRadius: 44,
                  backgroundColor: BRAND.white,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: "0 10px 26px rgba(200,86,74,0.18)",
                }}
              >
                <svg width={44} height={44} viewBox="0 0 24 24" fill="none" stroke={BRAND.red} strokeWidth={1.8} strokeLinejoin="round" strokeLinecap="round">
                  <path d={ICONS[i % ICONS.length]} />
                </svg>
              </div>
              <div style={{ fontFamily: SANS, fontSize: i === 2 ? 38 : 46, fontWeight: i === 2 ? 450 : 600, color: BRAND.ink, lineHeight: 1.25 }}>
                {line}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/** Brand moment: full logo draws on, tagline in italic serif, thread underline. */
const Brand: React.FC<P> = ({ scene }) => {
  const frame = useCurrentFrame();
  const reveal = lerp(frame, [0, 16], [8, 100], EASE_OUT);
  const d = scene.duration;
  const exit = lerp(frame, [d - 6, d], [0, 1], EASE_IN);
  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.cream, justifyContent: "center", alignItems: "center", opacity: 1 - exit }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% 46%, ${BRAND.white} 0%, ${BRAND.cream} 55%, ${BRAND.creamDeep} 100%)`,
        }}
      />
      <div
        style={{
          clipPath: `inset(0 ${100 - reveal}% 0 0)`,
          transform: `scale(${1.04 - 0.04 * (reveal / 100)})`,
        }}
      >
        <Logo kind="full" tone="light" width={900} />
      </div>
      <div style={{ marginTop: 70 }}>
        <RiseWords
          text={scene.text[0] ?? "Every Stitch Tells a Story."}
          start={24}
          stagger={4}
          style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 500, fontSize: 76, color: BRAND.ink }}
        />
      </div>
      <div style={{ marginTop: 18 }}>
        <Thread start={40} width={520} color={BRAND.rose} />
      </div>
      {scene.text[1] ? (
        <div
          style={{
            marginTop: 40,
            fontFamily: SANS,
            fontSize: 30,
            fontWeight: 550,
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            color: BRAND.inkSoft,
            opacity: lerp(frame, [52, 66], [0, 1]),
          }}
        >
          {scene.text[1]}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

/** Final call to action. Website pill breathes on every beat. */
const Cta: React.FC<P> = ({ scene, plan }) => {
  const frame = useCurrentFrame();
  const p = plan.products[0];
  const beats = localBeats(plan.beats, scene.from, scene.duration);
  const t = lerp(frame, [0, 14], [0, 1]);
  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.cream, alignItems: "center" }}>
      <Backdrop src={p.image} tintOpacity={0.72} />
      <div
        style={{
          position: "absolute",
          top: 250,
          width: 330,
          height: 330,
          borderRadius: 165,
          overflow: "hidden",
          border: `10px solid ${BRAND.white}`,
          boxShadow: "0 30px 70px rgba(70,30,20,0.25)",
          transform: `scale(${0.7 + 0.3 * t})`,
          opacity: t,
        }}
      >
        <Photo src={p.image} focus={p.focus[0]} zoom={1.6} />
      </div>
      <div style={{ position: "absolute", top: 660, width: "100%", display: "flex", flexDirection: "column", alignItems: "center" }}>
        <RiseWords
          text={scene.text[0] ?? "Find Your Handmade Favourite!"}
          start={4}
          stagger={3}
          style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 96, lineHeight: 1.05, color: BRAND.ink, padding: "0 80px", textAlign: "center" }}
        />
        <div style={{ marginTop: 64, opacity: lerp(frame, [16, 26], [0, 1]), transform: `translateY(${lerp(frame, [16, 30], [30, 0])}px)` }}>
          <WebsitePill website={plan.website} beats={beats} size={50} />
        </div>
        <div
          style={{
            marginTop: 54,
            fontFamily: SANS,
            fontSize: 38,
            fontWeight: 600,
            letterSpacing: "0.04em",
            color: BRAND.red,
            opacity: lerp(frame, [26, 36], [0, 1]),
          }}
        >
          {scene.text[1]}
        </div>
        <div style={{ marginTop: 22, fontFamily: SANS, fontSize: 30, color: BRAND.inkSoft, opacity: lerp(frame, [32, 42], [0, 1]) }}>
          {scene.text[2]}
        </div>
      </div>
      <div style={{ position: "absolute", top: H - 560, opacity: lerp(frame, [36, 48], [0, 1]) }}>
        <Logo kind="short" tone="light" width={330} />
      </div>
    </AbsoluteFill>
  );
};
