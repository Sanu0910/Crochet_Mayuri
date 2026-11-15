import React from "react";
import { AbsoluteFill } from "remotion";
import type { AdPlan } from "./types";
import { BRAND, Backdrop, Finish, Logo, Photo, SANS, SCRIPT, SERIF } from "./common";

/**
 * Reel cover (1080×1920). Instagram's grid shows the middle 1080×1350, so
 * the title, photo and logo all sit inside y ≈ 285…1635.
 */
export const Cover: React.FC<AdPlan> = (plan) => {
  const p = plan.products[plan.cover.product] ?? plan.products[0];
  const showcase = plan.variant === "showcase";
  return (
    <AbsoluteFill style={{ backgroundColor: showcase ? BRAND.cream : BRAND.rose, alignItems: "center" }}>
      {showcase ? <Backdrop src={p.image} tintOpacity={0.6} /> : null}
      <div style={{ position: "absolute", top: 330 }}>
        <Logo kind="short" tone={showcase ? "light" : "mono-white"} width={260} />
      </div>
      <div
        style={{
          position: "absolute",
          top: 470,
          width: 700,
          height: 760,
          borderRadius: showcase ? 30 : 16,
          overflow: "hidden",
          border: showcase ? "none" : `16px solid ${BRAND.white}`,
          transform: showcase ? "none" : "rotate(-3deg)",
          boxShadow: "0 50px 100px rgba(70,30,20,0.3)",
        }}
      >
        <Photo src={p.image} focus={p.focus[0]} zoom={1.12} />
      </div>
      <div style={{ position: "absolute", top: 1275, left: 70, right: 70, textAlign: "center" }}>
        <div
          style={{
            fontFamily: showcase ? SANS : SCRIPT,
            fontSize: showcase ? 30 : 64,
            fontWeight: 700,
            letterSpacing: showcase ? "0.3em" : "0",
            textTransform: showcase ? "uppercase" : "none",
            color: showcase ? BRAND.red : BRAND.white,
            lineHeight: 1,
          }}
        >
          {plan.cover.kicker}
        </div>
        <div
          style={{
            marginTop: showcase ? 18 : 6,
            fontFamily: showcase ? SERIF : SANS,
            fontWeight: showcase ? 600 : 900,
            fontSize: showcase ? 92 : 104,
            letterSpacing: showcase ? "-0.01em" : "-0.04em",
            textTransform: showcase ? "none" : "uppercase",
            color: showcase ? BRAND.ink : BRAND.ink,
            lineHeight: 1,
          }}
        >
          {plan.cover.title}
        </div>
      </div>
      <Finish vignette={0.18} />
    </AbsoluteFill>
  );
};
