import { createContext, useCallback, useContext, useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { api } from "../lib/api";
import { t, useLang } from "../i18n";
import { eur, pct } from "../lib/format";
import { Icon } from "./Icons";
import { reducedMotion } from "./Motion";

// A key number with its label and a line of context.
export function Tile({ label, value, detail, swatch, aside, className }: { label: string; value: ReactNode; detail?: ReactNode; swatch?: string; aside?: ReactNode; className?: string }) {
  return (
    <div className={className ? `tile ${className}` : "tile"}>
      <div className="tile-txt">
        <div className="l">
          {swatch && <span className="sq" style={{ background: swatch }} />}
          {label}
        </div>
        <div className="v">{value}</div>
        {detail && <div className="d">{detail}</div>}
      </div>
      {aside}
    </div>
  );
}

// A progress ring (0 to 1) that draws itself when it appears, with an optional text in the middle.
export function Ring({ value, label, tone = "good", size = 54 }: { value: number; label?: ReactNode; tone?: "good" | "accent" | "warn" | "bad"; size?: number }) {
  const share = Math.max(0, Math.min(1, isFinite(value) ? value : 0));
  return (
    <span className={`ring ${tone}`} style={{ width: size, height: size }}>
      <svg viewBox="0 0 44 44" aria-hidden="true">
        <circle cx="22" cy="22" r="18" />
        <circle cx="22" cy="22" r="18" pathLength={100} style={{ ["--p" as string]: (share * 100).toFixed(1) }} />
      </svg>
      {label !== undefined && <span className="ring-l">{label}</span>}
    </span>
  );
}

// A change as a small pill with an arrow; green when it is good news, red when it isn't.
// onFlip makes it a button with a swap mark that turns it over to another figure (the period's
// gain and the gain since the start); it does a little flip when it does.
export function ChangePill({ text, up, good, title, onFlip }: { text: string; up: boolean; good: boolean; title?: string; onFlip?: () => void }) {
  if (onFlip)
    return (
      <button
        type="button"
        className={`chg turn ${good ? "good" : "bad"}`}
        title={title}
        aria-label={title ? `${text}. ${title}` : undefined}
        onClick={(e) => {
          if (!reducedMotion()) e.currentTarget.animate([{ transform: "perspective(240px) rotateX(80deg)", opacity: 0.4 }, { transform: "none", opacity: 1 }], { duration: 320, easing: "cubic-bezier(.2,.8,.2,1)" });
          onFlip();
        }}
      >
        <Icon name={up ? "up" : "down"} size={12} />
        {text}
        <Icon name="swap" size={12} className="chg-swap" />
      </button>
    );
  return (
    <span className={`chg ${good ? "good" : "bad"}`} title={title}>
      <Icon name={up ? "up" : "down"} size={12} />
      {text}
    </span>
  );
}

// A round, softly tinted symbol in front of a line: what kind of thing it is, at a glance.
export type Tone = "good" | "bad" | "warn" | "accent" | "info" | "muted";
export function IconBadge({ name, tone = "muted", size = 34 }: { name: string; tone?: Tone; size?: number }) {
  return (
    <span className={`ibadge ${tone}`} style={{ width: size, height: size }} aria-hidden="true">
      <Icon name={name} size={Math.round(size * 0.47)} />
    </span>
  );
}

export function BarRow({ name, sub, value, base, color, share, onClick, active }: {
  name: string; sub?: string; value: number; base: number; color: string; share?: number; onClick?: () => void; active?: boolean;
}) {
  const width = base > 0 ? Math.max(0, Math.min(100, (value / base) * 100)) : 0;
  const Tag = onClick ? "button" : "div";
  return (
    <Tag className={`barrow${onClick ? " pick" : ""}${active ? " on" : ""}`} {...(onClick ? { type: "button" as const, onClick, "aria-pressed": active } : {})}>
      <span className="top">
        <span className="sq" style={{ background: color }} />
        <span className="nm">
          {name}
          {sub && <span className="grp"> · {sub}</span>}
        </span>
        <span className="amt">{eur(value)}</span>
        {share !== undefined && <span className="pct">{pct(share)}</span>}
        {onClick && <span className="go" aria-hidden="true">›</span>}
      </span>
      <span className="track">
        <span style={{ width: `${width.toFixed(1)}%`, background: color }} />
      </span>
    </Tag>
  );
}

export function Card({ title, sub, right, children, id, className }: { title?: ReactNode; sub?: ReactNode; right?: ReactNode; children: ReactNode; id?: string; className?: string }) {
  return (
    <div className={className ? `card ${className}` : "card"} id={id}>
      {(title || right) && (
        <div className="card-h">
          <div>
            {title && <h3>{title}</h3>}
            {sub && <p>{sub}</p>}
          </div>
          {right}
        </div>
      )}
      {children}
    </div>
  );
}

// A segmented control: a pill slides to the chosen option with a little spring.
export function Seg<T extends string>({ value, options, onChange, label }: {
  value: T; options: [T, ReactNode][]; onChange: (v: T) => void; label: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [pill, setPill] = useState<{ x: number; w: number } | null>(null);
  useLayoutEffect(() => {
    const el = ref.current?.querySelector<HTMLElement>("button.on");
    if (!el) return;
    const measure = () => setPill({ x: el.offsetLeft, w: el.offsetWidth });
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, [value, options.length]);
  return (
    <div
      className={`seg${pill ? " slide" : ""}`}
      role="group"
      aria-label={label}
      ref={ref}
      style={pill ? { ["--ix" as string]: `${pill.x}px`, ["--iw" as string]: `${pill.w}px` } : undefined}
    >
      {options.map(([v, text]) => (
        <button key={v} type="button" className={v === value ? "on" : ""} aria-pressed={v === value} onClick={() => onChange(v)}>
          {text}
        </button>
      ))}
    </div>
  );
}

export function Switch({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label: string }) {
  return (
    <label className="switch">
      <input type="checkbox" checked={checked} aria-label={label} onChange={(e) => onChange(e.target.checked)} />
    </label>
  );
}

// Tabs with a bar that slides to the chosen one. `ids` links each tab to its panel for screen readers.
export function Tabs<T extends string>({ value, options, onChange, label, ids }: {
  value: T; options: [T, ReactNode][]; onChange: (v: T) => void; label: string; ids?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const lang = useLang();
  const [bar, setBar] = useState<{ x: number; w: number } | null>(null);
  useLayoutEffect(() => {
    const box = ref.current;
    const el = box?.querySelector<HTMLElement>("button.on");
    if (!box || !el) return;
    const measure = () => setBar({ x: el.offsetLeft, w: el.offsetWidth });
    measure();
    // On a phone the tabs scroll sideways; keep the chosen one in view.
    if (box.scrollWidth > box.clientWidth) box.scrollTo({ left: el.offsetLeft - (box.clientWidth - el.offsetWidth) / 2, behavior: "smooth" });
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, [value, lang, options.length]);
  return (
    <div
      className="tabs"
      role="tablist"
      aria-label={label}
      ref={ref}
      style={bar ? { ["--ix" as string]: `${bar.x}px`, ["--iw" as string]: `${bar.w}px` } : undefined}
    >
      {options.map(([k, text]) => (
        <button
          key={k}
          type="button"
          role="tab"
          id={ids ? `${ids}-tab-${k}` : undefined}
          aria-selected={value === k}
          aria-controls={ids ? `${ids}-panel-${k}` : undefined}
          className={value === k ? "on" : ""}
          onClick={() => onChange(k)}
        >
          {text}
        </button>
      ))}
      {bar && <span className="tabs-bar" aria-hidden="true" />}
    </div>
  );
}

// A small menu to pick one of a few options: the button shows the choice, a click opens the list.
// Closes on a click elsewhere or Escape; the arrow keys move through the options.
export function Dropdown<T extends string>({ value, options, onChange, label, display, icon, className }: {
  value: T; options: [T, string][]; onChange: (v: T) => void; label: string; display?: ReactNode; icon?: string; className?: string;
}) {
  const [open, setOpen] = useState(false);
  const box = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const away = (e: PointerEvent) => {
      if (!box.current?.contains(e.target as Node)) setOpen(false);
    };
    const key = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      e.stopPropagation();
      setOpen(false);
      box.current?.querySelector<HTMLElement>(".dd-btn")?.focus();
    };
    document.addEventListener("pointerdown", away);
    document.addEventListener("keydown", key, true);
    box.current?.querySelector<HTMLElement>('.dd-item[aria-checked="true"], .dd-item')?.focus();
    return () => {
      document.removeEventListener("pointerdown", away);
      document.removeEventListener("keydown", key, true);
    };
  }, [open]);
  const move = (e: React.KeyboardEvent) => {
    if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
    e.preventDefault();
    const items = [...(box.current?.querySelectorAll<HTMLElement>(".dd-item") ?? [])];
    const i = items.indexOf(document.activeElement as HTMLElement);
    items[(i + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length]?.focus();
  };
  const current = options.find(([v]) => v === value)?.[1] ?? "";
  return (
    <div className={`dd${open ? " open" : ""}${className ? ` ${className}` : ""}`} ref={box}>
      <button type="button" className="dd-btn" aria-haspopup="menu" aria-expanded={open} aria-label={`${label}: ${current}`} onClick={() => setOpen(!open)}>
        {icon && <Icon name={icon} size={15} />}
        <span className="dd-txt">{display ?? current}</span>
        <Icon name="chevDown" size={14} className="dd-chev" />
      </button>
      {open && (
        <div className="dd-menu" role="menu" aria-label={label} onKeyDown={move}>
          {options.map(([v, text]) => (
            <button
              key={v}
              type="button"
              role="menuitemradio"
              aria-checked={v === value}
              className={`dd-item${v === value ? " on" : ""}`}
              onClick={() => {
                onChange(v);
                setOpen(false);
              }}
            >
              <span>{text}</span>
              {v === value && <Icon name="check" size={14} />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export const Spinner = () => <span className="spinner" aria-hidden="true" />;

export function Loading({ text }: { text?: string }) {
  useLang();
  return (
    <div className="loading">
      <span className="hstack">
        <Spinner />
        {text ?? t("common.loading")}
      </span>
    </div>
  );
}

export function Empty({ title, children, icon = "spark" }: { title: string; children?: ReactNode; icon?: string }) {
  return (
    <div className="empty">
      <span className="empty-ic" aria-hidden="true">
        <Icon name={icon} size={20} />
      </span>
      <b>{title}</b>
      {children && <span>{children}</span>}
    </div>
  );
}

export function ErrorNote({ error }: { error: string | null }) {
  if (!error) return null;
  return (
    <div className="alert" role="alert">
      <Icon name="warn" size={18} />
      <span>{error}</span>
    </div>
  );
}

export function Modal({ title, onClose, children, actions, wide }: { title: string; onClose: () => void; children: ReactNode; actions?: ReactNode; wide?: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);
  useEffect(() => {
    ref.current?.querySelector<HTMLElement>("input,select,textarea,button")?.focus();
    const before = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = before;
    };
  }, []);
  // Rendered into <body>: the page wrapper animates with a transform, which would
  // otherwise pin the overlay to the page instead of the window.
  return createPortal(
    <div className="overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className={`modal${wide ? " wide" : ""}`} role="dialog" aria-modal="true" aria-label={title} ref={ref}>
        <div className="card-h">
          <h3>{title}</h3>
          <button className="ib" type="button" aria-label={t("common.close")} onClick={onClose}>
            <Icon name="x" size={16} />
          </button>
        </div>
        {children}
        {actions && <div className="actions">{actions}</div>}
      </div>
    </div>,
    document.body,
  );
}

// --- toasts -------------------------------------------------------------------

type ToastAction = { label: string; run: () => void };
const ToastCtx = createContext<(msg: string, action?: ToastAction) => void>(() => {});
export const useToast = () => useContext(ToastCtx);

// A short note at the bottom. With an action ("Never show these") it stays a little longer.
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toast, setToast] = useState<{ msg: string; action?: ToastAction } | null>(null);
  const timer = useRef<number | undefined>(undefined);
  const show = useCallback((msg: string, action?: ToastAction) => {
    setToast({ msg, action });
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setToast(null), action ? 6500 : 3200);
  }, []);
  return (
    <ToastCtx.Provider value={show}>
      {children}
      {toast && (
        <div className="toast" role="status">
          <span>{toast.msg}</span>
          {toast.action && (
            <button
              className="linkbtn"
              onClick={() => {
                setToast(null);
                toast.action!.run();
              }}
            >
              {toast.action.label}
            </button>
          )}
        </div>
      )}
    </ToastCtx.Provider>
  );
}

// --- data loading -------------------------------------------------------------

export function useApi<T>(path: string | null, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [tick, setTick] = useState(0);
  // Some answers contain text from the server, so fetch again after a language switch.
  const lang = useLang();
  useEffect(() => {
    if (!path) return;
    let alive = true;
    setLoading(true);
    api
      .get<T>(path)
      .then((d) => {
        if (alive) {
          setData(d);
          setError(null);
        }
      })
      .catch((e: Error) => alive && setError(e.message))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path, tick, lang, ...deps]);
  const reload = useCallback(() => setTick((t) => t + 1), []);
  return { data, error, loading, reload, setData };
}

// Refresh page data after a sync finishes anywhere in the app.
export function useSyncEvents(reload: () => void) {
  useEffect(() => {
    window.addEventListener("groschen:synced", reload);
    return () => window.removeEventListener("groschen:synced", reload);
  }, [reload]);
}

// --- shared building blocks from the redesign ---------------------------------------

// Opens and closes a section in place. Used for every "show more" in the app so they all look the same.
export function Disclosure({ label, openLabel, children, defaultOpen = false }: { label: string; openLabel?: string; children: ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className={`disclosure${open ? " open" : ""}`}>
      <button type="button" className="disclosure-btn" aria-expanded={open} onClick={() => setOpen(!open)}>
        <span className="chev" aria-hidden="true">›</span>
        {open ? (openLabel ?? label) : label}
      </button>
      {open && <div className="disclosure-body">{children}</div>}
    </div>
  );
}

// Asks before something that can't be undone. The browser's own confirm() looks foreign and can be blocked.
type ConfirmAsk = { title: string; text: string; action: string };
export function useConfirm() {
  const [ask, setAsk] = useState<(ConfirmAsk & { done: (ok: boolean) => void }) | null>(null);
  const confirm = useCallback(
    (a: ConfirmAsk) =>
      new Promise<boolean>((resolve) => {
        setAsk({ ...a, done: resolve });
      }),
    [],
  );
  const close = (ok: boolean) => {
    ask?.done(ok);
    setAsk(null);
  };
  const dialog = ask ? (
    <Modal
      title={ask.title}
      onClose={() => close(false)}
      actions={
        <>
          <button className="btn ghost" onClick={() => close(false)}>
            {t("common.cancel")}
          </button>
          <button className="btn danger" onClick={() => close(true)}>
            {ask.action}
          </button>
        </>
      }
    >
      <p className="muted">{ask.text}</p>
    </Modal>
  ) : null;
  return { confirm, dialog };
}

// A number setting that saves on Enter or when the field is left, and says so. A sum in € is blurred
// while amounts are hidden, until the field is clicked.
export function NumberSetting({ value, onSave, label, unit, step, min, max, width = 90 }: {
  value: number; onSave: (v: number) => Promise<unknown> | void; label: string; unit: string; step: number; min: number; max: number; width?: number;
}) {
  const [text, setText] = useState(String(value));
  const [saved, setSaved] = useState(false);
  const timer = useRef<number | undefined>(undefined);
  useEffect(() => setText(String(value)), [value]);
  useEffect(() => () => window.clearTimeout(timer.current), []);
  async function commit() {
    const v = Number(text.replace(",", "."));
    if (!isFinite(v) || v === value) return;
    await onSave(Math.min(max, Math.max(min, v)));
    setSaved(true);
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setSaved(false), 1800);
  }
  return (
    <span className="hstack numset">
      <input
        className={unit === "€" ? "input money-in" : "input"}
        style={{ width, height: 32 }}
        aria-label={label}
        type="number"
        inputMode="decimal"
        step={step}
        min={min}
        max={max}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => e.key === "Enter" && (e.currentTarget as HTMLInputElement).blur()}
      />
      {unit}
      <span className={`saved${saved ? " on" : ""}`} role="status" aria-live="polite">
        {saved && (
          <>
            <Icon name="check" size={14} />
            {t("common.saved")}
          </>
        )}
      </span>
    </span>
  );
}
