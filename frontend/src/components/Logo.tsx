import { useState, type CSSProperties, type ReactNode } from "react";
import { t, useT } from "../i18n";
import { initial } from "../lib/format";
import { brand, brandCount, chooseLogo, hasChoice, logoFor, searchBrands, useLogos, type Logo } from "../lib/logos";
import { Icon } from "./Icons";
import { LogoUpload } from "./LogoUpload";
import { Modal, Spinner } from "./UI";

function Face({ logo, name }: { logo: Logo; name: string }) {
  if (logo.kind === "image") return <img src={logo.src} alt="" draggable={false} />;
  if (logo.kind === "brand")
    return logo.path ? (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d={logo.path} fill={logo.ink} />
      </svg>
    ) : null;
  return <>{initial(name)}</>;
}

const styleOf = (logo: Logo): CSSProperties | undefined => (logo.kind === "brand" ? ({ ["--b" as string]: logo.hex } as CSSProperties) : undefined);
const classOf = (logo: Logo) => (logo.kind === "brand" ? ` logo${logo.dark ? " dark" : ""}` : logo.kind === "image" ? " logo img" : " letter");

/** A merchant's round badge: its brand logo on the brand's colour, a picture of the user's, or its letter. */
export function MerchantAv({ name, big, className = "txl-av" }: { name: string; big?: boolean; className?: string }) {
  useLogos();
  const logo = logoFor(name);
  return (
    <span className={`${className}${big ? " big" : ""}${classOf(logo)}`} style={styleOf(logo)} aria-hidden="true">
      <Face logo={logo} name={name} />
    </span>
  );
}

/** The badge in a merchant's details: a click changes its logo. */
export function LogoButton({ name }: { name: string }) {
  useT();
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" className="logo-btn" onClick={() => setOpen(true)} title={t("logo.change")} aria-label={t("logo.changeFor", { merchant: name })}>
        <MerchantAv name={name} big />
        <span className="logo-pen" aria-hidden="true">
          <Icon name="pencil" size={11} />
        </span>
      </button>
      {open && <LogoEditor name={name} onClose={() => setOpen(false)} />}
    </>
  );
}

// What a merchant's name suggests before anything is typed: built-in logos named like its words.
function suggestionsFor(name: string): string[] {
  const seen = new Set<string>();
  for (const w of name.split(/[^\p{L}\p{N}]+/u).filter((x) => x.length >= 3)) for (const s of searchBrands(w, 6)) seen.add(s);
  return [...seen].slice(0, 10);
}

export function LogoEditor({ name, onClose }: { name: string; onClose: () => void }) {
  useT();
  useLogos();
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [done, setDone] = useState(false);
  const current = logoFor(name);
  const chosen = hasChoice(name);
  const typed = q.trim().length > 0;
  const found = typed ? searchBrands(q, 40) : suggestionsFor(name);
  const flip = current.kind === "brand" ? current.slug : current.kind === "image" ? current.src : "letter";

  // A short "saved" moment on the big badge, then the dialog closes by itself.
  function finish() {
    setDone(true);
    window.setTimeout(onClose, 650);
  }

  async function run(what: string, fn: () => Promise<void>, close = false) {
    setBusy(what);
    setError(null);
    try {
      await fn();
      if (close) finish();
    } catch {
      setError(t("logo.failed"));
    } finally {
      setBusy(null);
    }
  }

  if (uploading)
    return (
      <Modal title={t("logo.title", { merchant: name })} onClose={onClose}>
        <LogoUpload name={name} onDone={onClose} onBack={() => setUploading(false)} />
      </Modal>
    );

  const tile = (key: string, label: string, sub: string, face: ReactNode, active: boolean, onClick: () => void, disabled = false) => (
    <button type="button" className={`logo-tile${active ? " on" : ""}`} disabled={disabled || busy !== null} onClick={onClick} style={{ ["--i" as string]: ["up", "letter", "auto"].indexOf(key) }}>
      <span className="logo-tile-face">{busy === key ? <Spinner /> : face}</span>
      <b>{label}</b>
      <small>{sub}</small>
      {active && (
        <span className="logo-tile-check" aria-hidden="true">
          <Icon name="check" size={11} />
        </span>
      )}
    </button>
  );

  return (
    <Modal title={t("logo.title", { merchant: name })} onClose={onClose}>
      <div className={`logo-hero${done ? " done" : ""}`} style={current.kind === "brand" ? ({ ["--b" as string]: current.hex } as CSSProperties) : undefined}>
        <span className="logo-hero-glow" aria-hidden="true" />
        <span className="logo-hero-av" key={flip}>
          <MerchantAv name={name} big />
          {done && (
            <span className="logo-hero-ok" aria-hidden="true">
              <Icon name="check" size={16} />
            </span>
          )}
        </span>
        <span className="logo-hero-t">
          <b>{current.kind === "brand" ? current.title : current.kind === "image" ? t("logo.ownPicture") : t("logo.letter")}</b>
          <span className={`logo-badge${chosen ? " own" : ""}`}>
            <Icon name={chosen ? "pin" : "spark"} size={11} />
            {chosen ? t("logo.chosen") : t("logo.auto")}
          </span>
        </span>
      </div>

      <div className="logo-tiles">
        {tile("up", t("logo.upload"), t("logo.uploadSub"), <Icon name="upload" size={16} />, current.kind === "image", () => setUploading(true))}
        {tile(
          "letter",
          t("logo.useLetter"),
          t("logo.letterSub"),
          <span className="logo-tile-letter">{initial(name)}</span>,
          current.kind === "letter" && chosen,
          () => run("letter", () => chooseLogo(name, { kind: "letter" }), true),
          current.kind === "letter" && chosen,
        )}
        {tile("auto", t("logo.reset"), t("logo.autoSub"), <Icon name="spark" size={16} />, !chosen, () => run("auto", () => chooseLogo(name, null), true), !chosen)}
      </div>

      <div className="logo-search">
        <span className="logo-search-ic" aria-hidden="true">
          <Icon name="search" size={15} />
        </span>
        <input
          className="input"
          id="logo-q"
          value={q}
          maxLength={60}
          placeholder={t("logo.search", { n: brandCount().toLocaleString() })}
          aria-label={t("logo.search", { n: brandCount().toLocaleString() })}
          onChange={(e) => setQ(e.target.value)}
        />
      </div>
      {found.length > 0 && !typed && <span className="logo-sec">{t("logo.suggested")}</span>}
      {(typed || found.length > 0) && (
        <div className="logo-grid" key={typed ? q.trim().toLowerCase() : "suggest"}>
          {typed && found.length === 0 && (
            <p className="logo-none">
              {t("logo.none")}{" "}
              <button type="button" className="linkish" onClick={() => setUploading(true)}>
                {t("logo.upload")}
              </button>
            </p>
          )}
          {found.map((slug, i) => {
            const b = brand(slug);
            if (!b) return null;
            const on = current.kind === "brand" && current.slug === slug;
            return (
              <button
                key={slug}
                type="button"
                className={`logo-pick${on ? " on" : ""}`}
                style={{ ["--i" as string]: Math.min(i, 20), ["--b" as string]: b.hex } as CSSProperties}
                disabled={busy !== null}
                onClick={() => run(slug, () => chooseLogo(name, { kind: "brand", slug }), true)}
                title={b.title}
              >
                <span className={`txl-av${classOf(b)}`} style={styleOf(b)} aria-hidden="true">
                  {busy === slug ? <Spinner /> : <Face logo={b} name={b.title} />}
                </span>
                <small>{b.title}</small>
              </button>
            );
          })}
        </div>
      )}
      {error && <p className="err">{error}</p>}
      <p className="logo-note">
        <Icon name="lock" size={12} />
        {t("logo.note")}
      </p>
    </Modal>
  );
}
