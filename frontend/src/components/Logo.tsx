import { useState, type CSSProperties } from "react";
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

export function LogoEditor({ name, onClose }: { name: string; onClose: () => void }) {
  useT();
  useLogos();
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const found = searchBrands(q, 40);
  const current = logoFor(name);

  async function run(what: string, fn: () => Promise<void>, close = false) {
    setBusy(what);
    setError(null);
    try {
      await fn();
      if (close) onClose();
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

  return (
    <Modal title={t("logo.title", { merchant: name })} onClose={onClose}>
      <div className="logo-now">
        <MerchantAv name={name} big />
        <span>
          <b>{current.kind === "brand" ? current.title : current.kind === "image" ? t("logo.ownPicture") : t("logo.letter")}</b>
          <small className="muted">{hasChoice(name) ? t("logo.chosen") : t("logo.auto")}</small>
        </span>
      </div>
      <div className="logo-acts">
        <button type="button" className="btn" disabled={busy !== null} onClick={() => setUploading(true)}>
          <Icon name="upload" size={14} />
          {t("logo.upload")}
        </button>
        <button type="button" className="btn ghost" disabled={busy !== null || current.kind === "letter"} onClick={() => run("letter", () => chooseLogo(name, { kind: "letter" }))}>
          {busy === "letter" && <Spinner />}
          {t("logo.useLetter")}
        </button>
        {hasChoice(name) && (
          <button type="button" className="btn ghost" disabled={busy !== null} onClick={() => run("auto", () => chooseLogo(name, null))}>
            {busy === "auto" ? <Spinner /> : <Icon name="refresh" size={14} />}
            {t("logo.reset")}
          </button>
        )}
      </div>
      <div className="field">
        <label htmlFor="logo-q">{t("logo.search", { n: brandCount().toLocaleString() })}</label>
        <input className="input" id="logo-q" value={q} maxLength={60} placeholder={t("logo.searchPh")} onChange={(e) => setQ(e.target.value)} />
      </div>
      {q.trim() && (
        <div className="logo-grid">
          {found.length === 0 && <p className="muted small">{t("logo.none")}</p>}
          {found.map((slug) => {
            const b = brand(slug);
            if (!b) return null;
            return (
              <button key={slug} type="button" className="logo-pick" disabled={busy !== null} onClick={() => run(slug, () => chooseLogo(name, { kind: "brand", slug }), true)} title={b.title}>
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
      <p className="muted small logo-note">{t("logo.note")}</p>
    </Modal>
  );
}
