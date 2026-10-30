import { useEffect, useRef, useState } from "react";
import { splashEgg } from "../components/Eggs";
import { Logo } from "../components/Icons";
import { celebrate } from "../components/Motion";
import { isLang, setLang, t, useT } from "../i18n";
import type { Status } from "../lib/types";

const reduce = typeof matchMedia !== "undefined" && matchMedia("(prefers-reduced-motion: reduce)").matches;
const wait = (ms: number) => new Promise((r) => setTimeout(r, reduce ? Math.min(ms, 80) : ms));

// Snowflakes or stars for the splash easter eggs. Positions are fixed per load.
function Sky({ kind }: { kind: "snow" | "stars" }) {
  const [flakes] = useState(() =>
    Array.from({ length: kind === "snow" ? 40 : 60 }, () => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
      z: 2 + Math.random() * 4,
      t: kind === "snow" ? 6 + Math.random() * 6 : 1.5 + Math.random() * 3,
      d: -Math.random() * 10,
      w: (Math.random() - 0.5) * 80,
    })),
  );
  return (
    <div className={`sp-sky ${kind}`} aria-hidden="true">
      {flakes.map((f, i) => (
        <i
          key={i}
          style={{
            left: `${f.x}%`,
            ["--y" as string]: `${f.y}%`,
            ["--z" as string]: `${f.z}px`,
            ["--t" as string]: `${f.t}s`,
            ["--d" as string]: `${f.d}s`,
            ["--w" as string]: `${f.w}px`,
          }}
        />
      ))}
    </div>
  );
}

export default function Splash({ load, onDone }: { load: () => Promise<Status>; onDone: (s: Status) => void }) {
  useT();
  const [msg, setMsg] = useState(() => t("splash.starting"));
  const [progress, setProgress] = useState(0);
  const [out, setOut] = useState(false);
  const [version, setVersion] = useState("");
  const [failed, setFailed] = useState<string | null>(null);
  const started = useRef(false);
  const [egg] = useState(() => splashEgg());

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    (async () => {
      await wait(500);
      setMsg(t("splash.database"));
      setProgress(25);
      let status: Status | null = null;
      for (let attempt = 0; attempt < 30 && !status; attempt++) {
        try {
          status = await load();
        } catch {
          setMsg(t("splash.waiting"));
          await wait(2000);
        }
      }
      if (!status) {
        setFailed(t("splash.failed"));
        return;
      }
      setVersion(status.version);
      // The language saved in Settings wins over the browser language.
      if (isLang(status.language)) setLang(status.language);
      setMsg(t("splash.settings"));
      setProgress(55);
      await wait(450);
      if (!status.has_user) setMsg(t("splash.firstRun"));
      else if (!status.user) setMsg(t("splash.login"));
      else setMsg(t("splash.accounts"));
      setProgress(100);
      if (egg.kind === "newyear") celebrate(document.querySelector(".sp-logo"), 40);
      await wait(550);
      setOut(true);
      await wait(350);
      onDone(status);
    })();
  }, [load, onDone, egg.kind]);

  return (
    <div id="splash" className={out ? "out" : ""} aria-live="polite">
      {(egg.kind === "snow" || egg.kind === "stars") && <Sky kind={egg.kind} />}
      <div className="sp-inner">
        <Logo className="sp-logo" />
        <div className="sp-name">Groschen</div>
        <div className="sp-tag">{egg.tagline ?? t("splash.tagline")}</div>
        <div className="sp-bar">
          <span style={{ width: `${progress}%` }} />
        </div>
        <div className="sp-status">{failed ?? msg}</div>
      </div>
      <div className="sp-foot">{version ? `${t("splash.version", { v: version })} · ` : ""}
        {t("splash.offline")}</div>
    </div>
  );
}
