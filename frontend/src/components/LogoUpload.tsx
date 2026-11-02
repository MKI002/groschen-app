import { useEffect, useRef, useState, type DragEvent, type KeyboardEvent as ReactKeyboardEvent, type PointerEvent as ReactPointerEvent } from "react";
import { t, useT } from "../i18n";
import { analyse, css, fromHex, hex, luminance, near, turnAround, type Look, type RGB } from "../lib/logoLook";
import { uploadLogoBlob } from "../lib/logos";
import { Icon } from "./Icons";
import { Spinner } from "./UI";

const STAGE = 240; // px, the round cutout fills the square stage
const OUT = 256; // px of the saved picture
const MAX_ZOOM = 5;
const MIN_ZOOM = 0.3; // below 1 the picture gets smaller than the circle and the rest is filled in
// Logos on a plain background are sized alike, as the built-in ones are: by their area (a wide
// word mark gets as much room as a square mark), and never wider than SIDE of the circle.
const AREA = 0.46;
const SIDE = 0.68;
const GLIDE = 720; // ms, how long the zoom takes to glide to that size
const MAX_FILE = 25 * 1024 * 1024;
const MAX_SIDE = 1280; // px, larger pictures are scaled down first (the saved badge is 256 px)
const WHITE: RGB = [255, 255, 255];
const BLACK: RGB = [13, 14, 17];

type Picked = {
  url: string;
  w: number;
  h: number;
  look: Look;
  glyph: { light: string; dark: string } | null; // the logo turned around: its shape in white / near-black on see-through
};
type Mode = "orig" | "disc";
type Pos = { x: number; y: number };

// A picture dragged in from another site: the browser may hand over the file itself (Chrome
// usually does), a data: address (Google's image results often are), or only a link.
// A data: address is decoded here into a file, so nothing dropped is ever used as an address.
// A link to one of Google Images' own picture servers is loaded by the browser (never by the
// Groschen server); the page's security policy allows exactly these hosts and no others.
const DATA_URL = /^data:(image\/(?:png|jpeg|jpg|webp|gif));base64,([A-Za-z0-9+/]+={0,2})$/;
const IMG_SRC = /<img\b[^>]*?\ssrc\s*=\s*["']([^"']+)["']/i;
const BROWSER_HOSTS = /^(?:encrypted-tbn[0-3]\.gstatic\.com|lh[3-6]\.googleusercontent\.com)$/;

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

/** The dropped text as a link the browser may load, rebuilt from its checked parts; null for anything else. */
function browserLink(text: string): string | null {
  let u: URL;
  try {
    u = new URL(text.trim());
  } catch {
    return null;
  }
  if (u.protocol !== "https:" || !BROWSER_HOSTS.test(u.hostname) || u.username || u.password || u.port) return null;
  return `https://${u.hostname}${u.pathname}${u.search}`;
}

function fromDrop(dt: DataTransfer): { file?: Blob; link?: string; linkOnly?: boolean } {
  const file = Array.from(dt.files).find((f) => f.type.startsWith("image/"));
  if (file) return { file };
  for (const item of Array.from(dt.items ?? [])) {
    if (item.kind === "file" && item.type.startsWith("image/")) {
      const f = item.getAsFile();
      if (f) return { file: f };
    }
  }
  const src = IMG_SRC.exec(dt.getData("text/html") || "")?.[1]?.replace(/&amp;/g, "&") ?? "";
  const moz = dt.getData("text/x-moz-url").split(/\r?\n/)[0] ?? "";
  const texts = [src, moz, ...dt.getData("text/uri-list").split(/\r?\n/), dt.getData("text/plain")].filter((x) => x && !x.startsWith("#"));
  for (const text of texts) {
    const blob = dataToBlob(text);
    if (blob) return { file: blob };
  }
  for (const text of texts) {
    const link = browserLink(text);
    if (link) return { link };
  }
  return texts.length ? { linkOnly: true } : {};
}

/** Your browser loads the picture (as when you look at it on Google) and hands over its pixels. */
function viaBrowser(link: string): Promise<Blob> {
  return new Promise((ok, fail) => {
    const img = new Image();
    const timer = window.setTimeout(() => fail(new Error("timeout")), 15000);
    img.crossOrigin = "anonymous"; // without the site's consent the pixels stay unreadable, and this fails
    img.referrerPolicy = "no-referrer";
    img.onerror = () => {
      window.clearTimeout(timer);
      fail(new Error("load"));
    };
    img.onload = () => {
      window.clearTimeout(timer);
      try {
        const canvas = document.createElement("canvas");
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        canvas.getContext("2d")?.drawImage(img, 0, 0);
        canvas.toBlob((b) => (b ? ok(b) : fail(new Error("png"))), "image/png");
      } catch (e) {
        fail(e);
      }
    };
    img.src = link;
  });
}

function fromClipboard(e: ClipboardEvent): Blob | null {
  for (const item of Array.from(e.clipboardData?.items ?? [])) {
    if (item.kind === "file" && item.type.startsWith("image/")) return item.getAsFile();
  }
  return null;
}

const pngOf = (canvas: HTMLCanvasElement) =>
  new Promise<Blob>((ok, fail) => canvas.toBlob((b) => (b ? ok(b) : fail(new Error("png"))), "image/png"));

const COVER = { zoom: 1, pos: { x: 0, y: 0 } };
// Where a picture settles: a logo on a plain (or see-through) background is centred and sized
// like the others; anything else (a photo) fills the circle. Null: nothing to size.
function framing(w: number, h: number, look: Look): { zoom: number; pos: Pos } | null {
  const b = look.box;
  if (!look.plain || !b) return null;
  const bw = b.w * w;
  const bh = b.h * h;
  const base = STAGE / Math.min(w, h);
  const fit = Math.min((STAGE * AREA) / Math.sqrt(bw * bh), (STAGE * SIDE) / Math.max(bw, bh));
  const zoom = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, fit / base));
  const s = base * zoom;
  return { zoom, pos: { x: (w / 2 - (b.x + b.w / 2) * w) * s, y: (h / 2 - (b.y + b.h / 2) * h) * s } };
}

// Out quickly, a little past the mark, and back: the slider "snaps" into place.
const springOut = (p: number) => 1 + 2.2 * (p - 1) ** 3 + 1.2 * (p - 1) ** 2;
const calm = () => window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;

type Swatch = { key: string; c: RGB | null; auto?: boolean };
// Background suggestions: the picture's own colours first, then white, black and see-through.
function swatchesFor(pic: Picked, mode: Mode): Swatch[] {
  const { look } = pic;
  const list: Swatch[] =
    mode === "disc"
      ? [{ key: "auto", c: look.ink, auto: true }, ...look.palette.map((c, i) => ({ key: `p${i}`, c })), { key: "black", c: BLACK }, { key: "white", c: WHITE }]
      : [
          ...(look.edge ? [{ key: "auto", c: look.edge, auto: true }] : []),
          ...look.palette.map((c, i) => ({ key: `p${i}`, c })),
          { key: "white", c: WHITE },
          { key: "black", c: BLACK },
          { key: "none", c: null },
        ];
  const out: Swatch[] = [];
  for (const s of list) if (s.c === null || !out.some((o) => o.c && near(o.c, s.c, 28))) out.push(s);
  return out.slice(0, 6);
}

// The picture as it will look: a round badge of the given size.
function Mini({ src, pic, pos, scale, size, bg }: { src: string; pic: Picked; pos: Pos; scale: number; size: number; bg: RGB | null }) {
  const k = size / STAGE;
  return (
    <span className={`lup-mini${bg ? "" : " clear"}`} style={{ width: size, height: size, background: bg ? css(bg) : undefined }}>
      <img
        src={src}
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
  const [info, setInfo] = useState<string | null>(null);
  const [nudge, setNudge] = useState(0); // bumps to point at the Paste chip when a site keeps its picture to itself
  const [fetching, setFetching] = useState(false);
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [pos, setPos] = useState<Pos>({ x: 0, y: 0 });
  const [mode, setMode] = useState<Mode>("orig");
  const [bgOrig, setBgOrig] = useState<RGB | null>(null);
  const [bgDisc, setBgDisc] = useState<RGB>(BLACK);
  const [burst, setBurst] = useState(0); // bumps when Groschen turns a logo around by itself
  const [washes, setWashes] = useState<{ id: number; bg: RGB | null }[]>([]);
  const file = useRef<HTMLInputElement>(null);
  const stage = useRef<HTMLDivElement>(null);
  const drag = useRef<{ id: number; x: number; y: number; px: number; py: number } | null>(null);
  const depth = useRef(0);
  const live = useRef(false); // the colour wheel is moving: recolour in place instead of a new wash per step
  const suggest = useRef<number | undefined>(undefined);
  const timers = useRef<number[]>([]);
  const anim = useRef(0);
  const [gliding, setGliding] = useState(false);
  const [reading, setReading] = useState(false);

  const later = (ms: number, fn: () => void) => timers.current.push(window.setTimeout(fn, ms));
  function stopAll() {
    timers.current.forEach((id) => window.clearTimeout(id));
    timers.current = [];
    window.clearTimeout(suggest.current);
    cancelAnimationFrame(anim.current);
    setGliding(false);
  }
  // The zoom (and the slider with it) glides to where the logo is the same size as the others.
  function glide(to: { zoom: number; pos: Pos }, from: { zoom: number; pos: Pos }) {
    cancelAnimationFrame(anim.current);
    if (calm()) {
      setZoom(to.zoom);
      setPos(to.pos);
      return;
    }
    const t0 = performance.now();
    setGliding(true);
    const step = (now: number) => {
      const p = Math.min(1, (now - t0) / GLIDE);
      const e = springOut(p);
      setZoom(Math.max(MIN_ZOOM * 0.9, from.zoom + (to.zoom - from.zoom) * e));
      setPos({ x: from.pos.x + (to.pos.x - from.pos.x) * e, y: from.pos.y + (to.pos.y - from.pos.y) * e });
      if (p < 1) anim.current = requestAnimationFrame(step);
      else setGliding(false);
    };
    anim.current = requestAnimationFrame(step);
  }

  // The picture is decoded and drawn onto a canvas first, and only those pixels are shown and
  // saved: whatever came in (a file, a paste, a drop from another site) never reaches the page
  // itself. Very large pictures are scaled down on the way.
  async function open(src: Blob): Promise<boolean> {
    setNote(null);
    setInfo(null);
    if (src.size > MAX_FILE || !/^image\/(png|jpe?g|webp|gif)$/.test(src.type)) {
      setNote(t(src.size > MAX_FILE ? "logo.up.tooBig" : "logo.up.unreadable"));
      return false;
    }
    setReading(true);
    try {
      const bitmap = await createImageBitmap(src);
      const k = Math.min(1, MAX_SIDE / Math.max(bitmap.width, bitmap.height));
      const canvas = document.createElement("canvas");
      const w = (canvas.width = Math.max(1, Math.round(bitmap.width * k)));
      const h = (canvas.height = Math.max(1, Math.round(bitmap.height * k)));
      const ctx = canvas.getContext("2d", { willReadFrequently: true });
      if (!ctx) throw new Error("canvas");
      ctx.drawImage(bitmap, 0, 0, w, h);
      bitmap.close();

      // A small copy is enough to read its colours and find where the logo sits.
      const small = document.createElement("canvas");
      const sk = Math.min(1, 160 / Math.max(w, h));
      small.width = Math.max(1, Math.round(w * sk));
      small.height = Math.max(1, Math.round(h * sk));
      const sctx = small.getContext("2d", { willReadFrequently: true });
      if (!sctx) throw new Error("canvas");
      sctx.drawImage(canvas, 0, 0, small.width, small.height);
      const look = analyse(sctx.getImageData(0, 0, small.width, small.height).data, small.width, small.height);

      let glyph: Picked["glyph"] = null;
      if (look.ink) {
        const ink = look.ink;
        const pixels = ctx.getImageData(0, 0, w, h).data;
        const turned = async (g: RGB) => {
          const c = document.createElement("canvas");
          c.width = w;
          c.height = h;
          c.getContext("2d")?.putImageData(new ImageData(turnAround(pixels, look.edge, ink, g), w, h), 0, 0);
          return URL.createObjectURL(await pngOf(c));
        };
        glyph = { light: await turned(WHITE), dark: await turned([17, 18, 20]) };
      }
      const url = URL.createObjectURL(await pngOf(canvas));
      const f = framing(w, h, look);
      const main = look.palette[0];
      stopAll();
      live.current = false;
      setWashes([]);
      setPic({ url, w, h, look, glyph });
      setZoom(COVER.zoom);
      setPos(COVER.pos);
      setMode("orig");
      // See-through with a dark logo: white behind it, or it would vanish on the dark list.
      setBgOrig(look.edge ?? (main && luminance(main) < 0.15 ? WHITE : null));
      setBgDisc(look.ink ?? main ?? BLACK);
      // It shows as it came for a moment, then the zoom glides to the shared logo size. A
      // one-coloured logo on white or see-through then turns around by itself, like the
      // built-in brand discs. Either step is one click to undo.
      if (f) later(320, () => glide(f, COVER));
      if (glyph)
        suggest.current = window.setTimeout(
          () => {
            setMode("disc");
            setBurst((b) => b + 1);
          },
          f ? 320 + GLIDE + 120 : 700,
        );
      return true;
    } catch {
      setNote(t("logo.up.unreadable"));
      return false;
    } finally {
      setReading(false);
    }
  }

  function refused() {
    setNote(t("logo.up.linkOnly"));
    setNudge((n) => n + 1);
  }

  async function fetchLink(link: string) {
    setNote(null);
    setInfo(null);
    setFetching(true);
    try {
      const blob = await viaBrowser(link);
      if (await open(blob)) setInfo(t("logo.up.viaBrowser", { host: new URL(link).hostname }));
    } catch {
      refused();
    } finally {
      setFetching(false);
    }
  }

  // Ctrl+V anywhere while the dialog is open: a copied picture, or a copied Google Images address.
  useEffect(() => {
    const onPaste = (e: ClipboardEvent) => {
      const blob = fromClipboard(e);
      const text = e.clipboardData?.getData("text/plain") ?? "";
      if (blob) {
        e.preventDefault();
        void open(blob);
      } else if (text) {
        const asData = dataToBlob(text);
        const link = browserLink(text);
        if (asData) void open(asData);
        else if (link) void fetchLink(link);
        else refused();
      }
    };
    window.addEventListener("paste", onPaste);
    return () => window.removeEventListener("paste", onPaste);
  }, []);
  useEffect(
    () => () => {
      if (!pic) return;
      URL.revokeObjectURL(pic.url);
      if (pic.glyph) [pic.glyph.light, pic.glyph.dark].forEach((u) => URL.revokeObjectURL(u));
    },
    [pic],
  );
  useEffect(() => stopAll, []);

  const bg = mode === "disc" ? bgDisc : bgOrig;
  const bgKey = `${mode}|${bg ? hex(bg) : "none"}`;
  const discSrc = pic?.glyph ? (luminance(bgDisc) > 0.45 ? pic.glyph.dark : pic.glyph.light) : "";
  const src = pic ? (mode === "disc" && pic.glyph ? discSrc : pic.url) : "";

  // Each new background washes in from the middle over the one before.
  useEffect(() => {
    if (!pic) return;
    setWashes((w) => {
      const last = w[w.length - 1];
      if (live.current && last) return [...w.slice(0, -1), { ...last, bg }];
      return [...w.slice(-1), { id: (last?.id ?? 0) + 1, bg }];
    });
  }, [bgKey, pic]);

  const setBg = (c: RGB | null, fromWheel = false) => {
    live.current = fromWheel;
    if (mode === "disc") setBgDisc(c ?? BLACK);
    else setBgOrig(c);
  };
  const pickMode = (m: Mode) => {
    window.clearTimeout(suggest.current);
    live.current = false;
    setMode(m);
  };

  const base = pic ? STAGE / Math.min(pic.w, pic.h) : 1;
  const scale = base * zoom;
  const clamp = (p: Pos, s = scale) => {
    if (!pic) return p;
    // Larger than the circle: it may move until an edge reaches the circle. Smaller: anywhere
    // inside. A plain background is extended seamlessly, so the logo may go further.
    const room = pic.look.plain ? STAGE / 2 : 0;
    const mx = Math.abs(pic.w * s - STAGE) / 2 + room;
    const my = Math.abs(pic.h * s - STAGE) / 2 + room;
    return { x: Math.min(mx, Math.max(-mx, p.x)), y: Math.min(my, Math.max(-my, p.y)) };
  };
  const setZoomKeep = (z: number) => {
    cancelAnimationFrame(anim.current);
    setGliding(false);
    const next = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, z));
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
    cancelAnimationFrame(anim.current);
    setGliding(false);
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
    else if (got.link) void fetchLink(got.link);
    else if (got.linkOnly) refused();
    else setNote(t("logo.up.unreadable"));
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
      img.src = src;
      await img.decode();
      const canvas = document.createElement("canvas");
      canvas.width = canvas.height = OUT;
      const ctx = canvas.getContext("2d");
      if (!ctx) throw new Error("canvas");
      // The stage scaled to the saved size: the background first, then the picture where it sits.
      const k = OUT / STAGE;
      if (bg) {
        ctx.fillStyle = css(bg);
        ctx.fillRect(0, 0, OUT, OUT);
      }
      const dw = pic.w * scale * k;
      const dh = pic.h * scale * k;
      ctx.imageSmoothingQuality = "high";
      ctx.drawImage(img, OUT / 2 + pos.x * k - dw / 2, OUT / 2 + pos.y * k - dh / 2, dw, dh);
      await uploadLogoBlob(name, await pngOf(canvas));
      setSaved(true);
      window.setTimeout(onDone, 700);
    } catch {
      setNote(t("logo.failed"));
      setBusy(false);
    }
  }

  const fitTo = pic ? framing(pic.w, pic.h, pic.look) : null;
  const fitted = !!fitTo && Math.abs(fitTo.zoom - zoom) < 0.01 && Math.abs(fitTo.pos.x - pos.x) < 1 && Math.abs(fitTo.pos.y - pos.y) < 1;

  function another() {
    stopAll();
    setPic(null);
    setInfo(null);
  }

  const swatches = pic ? swatchesFor(pic, mode) : [];
  const custom = !swatches.some((s) => near(s.c, bg));

  return (
    <div className="lup" {...dragProps}>
      {!pic ? (
        <button type="button" className={`lup-drop${over ? " over" : ""}${fetching ? " fetching" : ""}`} onClick={() => file.current?.click()} disabled={fetching}>
          <span className="lup-orb" aria-hidden="true">
            <span className="lup-orb-ring" />
            {fetching || reading ? <Spinner /> : <Icon name="upload" size={22} />}
          </span>
          <b>{fetching ? t("logo.up.fetching") : over ? t("logo.up.release") : t("logo.up.drop")}</b>
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
            {washes.map((w) => (
              <span key={w.id} className={`lup-wash${w.bg ? "" : " clear"}`} style={{ background: w.bg ? css(w.bg) : undefined }} aria-hidden="true" />
            ))}
            <img
              key={src}
              src={src}
              alt=""
              draggable={false}
              style={{ width: pic.w * scale, height: pic.h * scale, transform: `translate(-50%, -50%) translate(${pos.x}px, ${pos.y}px)` }}
            />
            {burst > 0 && mode === "disc" && (
              <span key={burst} className="lup-burst" aria-hidden="true">
                {Array.from({ length: 10 }, (_, i) => (
                  <i key={i} style={{ ["--a" as string]: `${i * 36 + 8}deg`, ["--d" as string]: `${86 + (i % 3) * 12}px`, ["--t" as string]: `${(i % 4) * 40}ms` }} />
                ))}
              </span>
            )}
            <span className="lup-ring" aria-hidden="true" />
            {saved && (
              <span className="lup-ok" aria-hidden="true">
                <Icon name="check" size={28} />
              </span>
            )}
          </div>
          <div className="lup-side">
            {pic.glyph ? (
              <div className="lup-looks" role="radiogroup" aria-label={t("logo.up.look")}>
                {(["orig", "disc"] as Mode[]).map((m) => (
                  <button key={m} type="button" role="radio" aria-checked={mode === m} className={`lup-look${mode === m ? " on" : ""}`} onClick={() => pickMode(m)}>
                    <Mini src={m === "disc" ? discSrc : pic.url} pic={pic} pos={pos} scale={scale} size={44} bg={m === "disc" ? bgDisc : bgOrig} />
                    <span className="lup-look-t">
                      <b>{t(`logo.up.look.${m}`)}</b>
                      {m === "disc" && (
                        <small key={burst} className={`lup-sugg${burst ? " pop" : ""}`}>
                          <Icon name="spark" size={10} />
                          {t("logo.up.suggested")}
                        </small>
                      )}
                    </span>
                  </button>
                ))}
              </div>
            ) : (
              <span className="lup-preview" aria-hidden="true">
                <Mini src={src} pic={pic} pos={pos} scale={scale} size={64} bg={bg} />
              </span>
            )}
            <span className="lup-row" aria-hidden="true">
              <Mini src={src} pic={pic} pos={pos} scale={scale} size={34} bg={bg} />
              <span className="lup-row-t">
                <b>{name}</b>
                <small>{t("logo.up.today")}</small>
              </span>
            </span>
            <div className={`lup-zoom${gliding ? " gliding" : ""}`}>
              <Icon name="zoomOut" size={14} />
              <input
                type="range"
                min={MIN_ZOOM}
                max={MAX_ZOOM}
                step={0.01}
                value={zoom}
                style={{ ["--p" as string]: `${((zoom - MIN_ZOOM) / (MAX_ZOOM - MIN_ZOOM)) * 100}%` }}
                aria-label={t("logo.up.zoom")}
                onChange={(e) => setZoomKeep(Number(e.target.value))}
              />
              <Icon name="zoomIn" size={14} />
              {fitTo && (
                <button
                  type="button"
                  className={`lup-fit${fitted ? " on" : ""}`}
                  title={t("logo.up.fit")}
                  aria-label={t("logo.up.fit")}
                  onClick={() => glide(fitTo, { zoom, pos })}
                  disabled={fitted || gliding}
                >
                  <Icon name="spark" size={12} />
                </button>
              )}
            </div>
            <div className="lup-bg" role="radiogroup" aria-label={t("logo.up.bg")}>
              <small className="muted">{t("logo.up.bg")}</small>
              <span className="lup-sws" key={mode}>
                {swatches.map((s, i) => {
                  const on = near(s.c, bg);
                  const label = s.auto ? t(mode === "disc" ? "logo.up.bg.logo" : "logo.up.bg.auto") : t(s.key === "white" ? "logo.up.bg.white" : s.key === "black" ? "logo.up.bg.black" : s.key === "none" ? "logo.up.bg.none" : "logo.up.bg.picture");
                  return (
                    <button
                      key={s.key}
                      type="button"
                      role="radio"
                      aria-checked={on}
                      className={`lup-sw${on ? " on" : ""}${s.c ? "" : " clear"}`}
                      style={{ ["--i" as string]: i, background: s.c ? css(s.c) : undefined, color: s.c && luminance(s.c) > 0.45 ? "#111214" : "#fff" }}
                      title={label}
                      aria-label={label}
                      onClick={() => setBg(s.c)}
                    >
                      {on ? <Icon name="check" size={11} /> : s.auto ? <Icon name="spark" size={10} /> : null}
                    </button>
                  );
                })}
                <label
                  className={`lup-sw wheel${custom ? " on" : ""}`}
                  style={{ ["--i" as string]: swatches.length, ...(custom && bg ? { background: css(bg), color: luminance(bg) > 0.45 ? "#111214" : "#fff" } : {}) }}
                  title={t("logo.up.bg.custom")}
                >
                  <input type="color" value={hex(bg ?? WHITE)} aria-label={t("logo.up.bg.custom")} onChange={(e) => setBg(fromHex(e.target.value), true)} />
                  {custom ? <Icon name="check" size={11} /> : <Icon name="plus" size={11} />}
                </label>
              </span>
            </div>
            <small className="muted">{t("logo.up.moveHint")}</small>
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
      {info && !note && (
        <p className="lup-info">
          <Icon name="lock" size={12} />
          {info}
        </p>
      )}
      <div className="lup-acts">
        <button type="button" className="btn ghost" onClick={pic ? another : onBack} disabled={busy}>
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
