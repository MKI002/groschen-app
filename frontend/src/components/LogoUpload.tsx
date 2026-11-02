import { useEffect, useRef, useState, type DragEvent, type KeyboardEvent as ReactKeyboardEvent, type PointerEvent as ReactPointerEvent } from "react";
import { t, useT } from "../i18n";
import { uploadLogoBlob } from "../lib/logos";
import { Icon } from "./Icons";
import { Spinner } from "./UI";

const STAGE = 240; // px, the round cutout fills the square stage
const OUT = 256; // px of the saved picture
const MAX_ZOOM = 5;
const MAX_FILE = 25 * 1024 * 1024;
const MAX_SIDE = 2048; // px, larger pictures are scaled down before cropping

type Picked = { url: string; w: number; h: number };

// A picture dragged in from another site: the browser may hand over the file itself (Chrome
// usually does), a data: address (Google's image results often are), or only a link. Groschen
// never loads a link itself; a picture that arrives as a link is copied and pasted instead.
// A data: address is decoded here into a file, so nothing dropped is ever used as an address.
const DATA_URL = /^data:(image\/(?:png|jpeg|jpg|webp|gif));base64,([A-Za-z0-9+/]+={0,2})$/;
const IMG_SRC = /<img\b[^>]*?\ssrc\s*=\s*["']([^"']+)["']/i;

function dataToBlob(text: string): Blob | null {
  const m = DATA_URL.exec(text.trim());
  if (!m || m[2].length > MAX_FILE * 1.4) return null;
  try {
    const bin = atob(m[2]);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new Blob([bytes], { type: m[1] === "image/jpg" ? "image/jpeg" : m[1] });
  } catch {
    return null;
  }
}

function fromDrop(dt: DataTransfer): { file?: Blob; linkOnly?: boolean } {
  const file = Array.from(dt.files).find((f) => f.type.startsWith("image/"));
  if (file) return { file };
  for (const item of Array.from(dt.items ?? [])) {
    if (item.kind === "file" && item.type.startsWith("image/")) {
      const f = item.getAsFile();
      if (f) return { file: f };
    }
  }
  const src = IMG_SRC.exec(dt.getData("text/html") || "")?.[1] ?? "";
  const texts = [src, ...dt.getData("text/uri-list").split(/\r?\n/), dt.getData("text/plain")].filter((x) => x && !x.startsWith("#"));
  for (const text of texts) {
    const blob = dataToBlob(text);
    if (blob) return { file: blob };
  }
  return texts.length ? { linkOnly: true } : {};
}

function fromClipboard(e: ClipboardEvent): Blob | null {
  for (const item of Array.from(e.clipboardData?.items ?? [])) {
    if (item.kind === "file" && item.type.startsWith("image/")) return item.getAsFile();
  }
  return null;
}

// The picture as it will look: a round badge of the given size.
function Mini({ pic, pos, scale, size }: { pic: Picked; pos: { x: number; y: number }; scale: number; size: number }) {
  const k = size / STAGE;
  return (
    <span className="lup-mini" style={{ width: size, height: size }}>
      <img
        src={pic.url}
        alt=""
        draggable={false}
        style={{ width: pic.w * scale * k, height: pic.h * scale * k, transform: `translate(-50%, -50%) translate(${pos.x * k}px, ${pos.y * k}px)` }}
      />
    </span>
  );
}

// The three ways in, each shown as a tiny move that plays once when the dialog opens and again on hover.
function Ways({ nudge }: { nudge: number }) {
  // Once the intro has played, only hovering plays a move again (leaving must not replay the intro).
  const [played, setPlayed] = useState(false);
  useEffect(() => {
    const id = window.setTimeout(() => setPlayed(true), 2600);
    return () => window.clearTimeout(id);
  }, []);
  return (
    <span className={`lup-ways${played ? " played" : ""}`} aria-label={t("logo.up.waysLabel")}>
      <span className="way w-click" style={{ ["--i" as string]: 0 }}>
        <span className="way-fx" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="20" height="20" className="fx-ptr">
            <path d="M6 3l12 7.5-5.2 1.2 3.1 6-2.6 1.3-3.1-6L6 16.5z" fill="currentColor" />
          </svg>
          <span className="fx-ripple" />
        </span>
        <span className="way-t">
          <b>{t("logo.up.click")}</b>
          <small>{t("logo.up.clickSub")}</small>
        </span>
      </span>
      <span className="way w-drag" style={{ ["--i" as string]: 1 }}>
        <span className="way-fx" aria-hidden="true">
          <span className="fx-tray" />
          <span className="fx-card">
            <svg viewBox="0 0 16 12" width="14" height="11">
              <path d="M1 11l4-5 3 3 2-2 5 4z" fill="currentColor" />
              <circle cx="11.5" cy="3" r="1.6" fill="currentColor" />
            </svg>
          </span>
        </span>
        <span className="way-t">
          <b>{t("logo.up.dragIn")}</b>
          <small>{t("logo.up.dragSub")}</small>
        </span>
      </span>
      <span key={nudge} className={`way w-paste${nudge ? " nudge" : ""}`} style={{ ["--i" as string]: 2 }}>
        <span className="way-fx keys" aria-hidden="true">
          <kbd className="k1">Ctrl</kbd>
          <kbd className="k2">V</kbd>
        </span>
        <span className="way-t">
          <b>{t("logo.up.paste")}</b>
          <small>{t("logo.up.pasteSub")}</small>
        </span>
      </span>
    </span>
  );
}

/** "Drop a picture or click": then move and zoom it behind the round cutout and save it. */
export function LogoUpload({ name, onDone, onBack }: { name: string; onDone: () => void; onBack: () => void }) {
  useT();
  const [pic, setPic] = useState<Picked | null>(null);
  const [over, setOver] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [nudge, setNudge] = useState(0); // bumps to point at the Paste chip when a site only gave a link
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const file = useRef<HTMLInputElement>(null);
  const stage = useRef<HTMLDivElement>(null);
  const drag = useRef<{ id: number; x: number; y: number; px: number; py: number } | null>(null);
  const depth = useRef(0);

  // The picture is decoded and drawn onto a canvas first, and only those pixels are shown and
  // saved: whatever came in (a file, a paste, a drop from another site) never reaches the page
  // itself. Very large pictures are scaled down on the way.
  async function open(src: Blob) {
    setNote(null);
    if (src.size > MAX_FILE) return setNote(t("logo.up.tooBig"));
    if (!/^image\/(png|jpe?g|webp|gif)$/.test(src.type)) return setNote(t("logo.up.unreadable"));
    try {
      const bitmap = await createImageBitmap(src);
      const k = Math.min(1, MAX_SIDE / Math.max(bitmap.width, bitmap.height));
      const canvas = document.createElement("canvas");
      canvas.width = Math.max(1, Math.round(bitmap.width * k));
      canvas.height = Math.max(1, Math.round(bitmap.height * k));
      canvas.getContext("2d")?.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
      bitmap.close();
      const clean = await new Promise<Blob | null>((ok) => canvas.toBlob(ok, "image/png"));
      if (!clean) throw new Error("png");
      setPic({ url: URL.createObjectURL(clean), w: canvas.width, h: canvas.height });
      setZoom(1);
      setPos({ x: 0, y: 0 });
    } catch {
      setNote(t("logo.up.unreadable"));
    }
  }

  // Ctrl+V anywhere while the dialog is open.
  useEffect(() => {
    const onPaste = (e: ClipboardEvent) => {
      const blob = fromClipboard(e);
      if (blob) {
        e.preventDefault();
        void open(blob);
      } else if (e.clipboardData?.getData("text/plain")) {
        setNote(t("logo.up.linkOnly"));
        setNudge((n) => n + 1);
      }
    };
    window.addEventListener("paste", onPaste);
    return () => window.removeEventListener("paste", onPaste);
  }, []);
  useEffect(
    () => () => {
      if (pic) URL.revokeObjectURL(pic.url);
    },
    [pic],
  );

  const base = pic ? STAGE / Math.min(pic.w, pic.h) : 1;
  const scale = base * zoom;
  const clamp = (p: { x: number; y: number }, s = scale) => {
    if (!pic) return p;
    const mx = Math.max(0, (pic.w * s - STAGE) / 2);
    const my = Math.max(0, (pic.h * s - STAGE) / 2);
    return { x: Math.min(mx, Math.max(-mx, p.x)), y: Math.min(my, Math.max(-my, p.y)) };
  };
  const setZoomKeep = (z: number) => {
    const next = Math.min(MAX_ZOOM, Math.max(1, z));
    setPos((p) => clamp({ x: (p.x * next) / zoom, y: (p.y * next) / zoom }, base * next));
    setZoom(next);
  };

  // Wheel zoom needs a non-passive listener to keep the page from scrolling.
  useEffect(() => {
    const el = stage.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      setZoomKeep(zoom * (e.deltaY < 0 ? 1.08 : 1 / 1.08));
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  });

  function down(e: ReactPointerEvent<HTMLDivElement>) {
    e.currentTarget.setPointerCapture(e.pointerId);
    drag.current = { id: e.pointerId, x: e.clientX, y: e.clientY, px: pos.x, py: pos.y };
  }
  function move(e: ReactPointerEvent<HTMLDivElement>) {
    const d = drag.current;
    if (!d || d.id !== e.pointerId) return;
    setPos(clamp({ x: d.px + e.clientX - d.x, y: d.py + e.clientY - d.y }));
  }
  const up = () => (drag.current = null);

  function onKey(e: ReactKeyboardEvent) {
    const step = e.shiftKey ? 20 : 6;
    const moves: Record<string, [number, number]> = { ArrowLeft: [step, 0], ArrowRight: [-step, 0], ArrowUp: [0, step], ArrowDown: [0, -step] };
    if (moves[e.key]) {
      e.preventDefault();
      setPos((p) => clamp({ x: p.x + moves[e.key][0], y: p.y + moves[e.key][1] }));
    } else if (e.key === "+" || e.key === "=") setZoomKeep(zoom * 1.1);
    else if (e.key === "-") setZoomKeep(zoom / 1.1);
  }

  function dropped(e: DragEvent) {
    e.preventDefault();
    depth.current = 0;
    setOver(false);
    const got = fromDrop(e.dataTransfer);
    if (got.file) void open(got.file);
    else if (got.linkOnly) {
      setNote(t("logo.up.linkOnly"));
      setNudge((n) => n + 1);
    } else setNote(t("logo.up.unreadable"));
  }
  const dragProps = {
    onDragEnter: (e: DragEvent) => {
      e.preventDefault();
      depth.current++;
      setOver(true);
    },
    onDragOver: (e: DragEvent) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = "copy";
    },
    onDragLeave: () => {
      depth.current = Math.max(0, depth.current - 1);
      if (!depth.current) setOver(false);
    },
    onDrop: dropped,
  };

  async function save() {
    if (!pic) return;
    setBusy(true);
    setNote(null);
    try {
      const img = new Image();
      img.src = pic.url;
      await img.decode();
      const canvas = document.createElement("canvas");
      canvas.width = canvas.height = OUT;
      const ctx = canvas.getContext("2d");
      if (!ctx) throw new Error("canvas");
      const side = STAGE / scale;
      const sx = pic.w / 2 - pos.x / scale - side / 2;
      const sy = pic.h / 2 - pos.y / scale - side / 2;
      ctx.imageSmoothingQuality = "high";
      ctx.drawImage(img, sx, sy, side, side, 0, 0, OUT, OUT);
      const blob = await new Promise<Blob | null>((ok) => canvas.toBlob(ok, "image/png"));
      if (!blob) throw new Error("png");
      await uploadLogoBlob(name, blob);
      setSaved(true);
      window.setTimeout(onDone, 700);
    } catch {
      setNote(t("logo.failed"));
      setBusy(false);
    }
  }

  return (
    <div className="lup" {...dragProps}>
      {!pic ? (
        <button type="button" className={`lup-drop${over ? " over" : ""}`} onClick={() => file.current?.click()}>
          <span className="lup-orb" aria-hidden="true">
            <span className="lup-orb-ring" />
            <Icon name="upload" size={22} />
          </span>
          <b>{over ? t("logo.up.release") : t("logo.up.drop")}</b>
          <Ways nudge={nudge} />
        </button>
      ) : (
        <div className={`lup-crop${over ? " over" : ""}`}>
          <div
            key={pic.url}
            className={`lup-stage${saved ? " saved" : ""}`}
            ref={stage}
            tabIndex={0}
            role="img"
            aria-label={t("logo.up.moveHint")}
            onPointerDown={down}
            onPointerMove={move}
            onPointerUp={up}
            onPointerCancel={up}
            onKeyDown={onKey}
            style={{ width: STAGE, height: STAGE }}
          >
            <img
              src={pic.url}
              alt=""
              draggable={false}
              style={{ width: pic.w * scale, height: pic.h * scale, transform: `translate(-50%, -50%) translate(${pos.x}px, ${pos.y}px)` }}
            />
            <span className="lup-ring" aria-hidden="true" />
            {saved && (
              <span className="lup-ok" aria-hidden="true">
                <Icon name="check" size={28} />
              </span>
            )}
          </div>
          <div className="lup-side">
            <span className="lup-preview" aria-hidden="true">
              <Mini pic={pic} pos={pos} scale={scale} size={64} />
              <span className="lup-row">
                <Mini pic={pic} pos={pos} scale={scale} size={34} />
                <span className="lup-row-t">
                  <b>{name}</b>
                  <small>{t("logo.up.today")}</small>
                </span>
              </span>
            </span>
            <small className="muted">{t("logo.up.moveHint")}</small>
            <label className="lup-zoom">
              <Icon name="zoomOut" size={14} />
              <input
                type="range"
                min={1}
                max={MAX_ZOOM}
                step={0.01}
                value={zoom}
                style={{ ["--p" as string]: `${((zoom - 1) / (MAX_ZOOM - 1)) * 100}%` }} aria-label={t("logo.up.zoom")} onChange={(e) => setZoomKeep(Number(e.target.value))} />
              <Icon name="zoomIn" size={14} />
            </label>
          </div>
        </div>
      )}
      <input
        ref={file}
        type="file"
        accept="image/png,image/jpeg,image/webp,image/gif"
        hidden
        onChange={(e) => {
          const f = e.target.files?.[0];
          e.target.value = "";
          if (f) void open(f);
        }}
      />
      {note && <p className="lup-note">{note}</p>}
      <div className="lup-acts">
        <button type="button" className="btn ghost" onClick={pic ? () => setPic(null) : onBack} disabled={busy}>
          {pic ? t("logo.up.other") : t("common.back")}
        </button>
        <span className="grow" />
        {pic && (
          <button type="button" className="btn primary" onClick={save} disabled={busy || saved}>
            {busy && <Spinner />}
            {t("common.save")}
          </button>
        )}
      </div>
    </div>
  );
}
