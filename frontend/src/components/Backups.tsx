import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { Icon } from "./Icons";
import { Card, Dropdown, Seg, Spinner, Switch, useConfirm, useToast } from "./UI";
import { locale, t, useT, type Key } from "../i18n";
import { api } from "../lib/api";
import { bytes, dateShort, int, relTime, whenNext } from "../lib/format";
import type { Backup, BackupMode, BackupPlan, BackupSchedule, SettingsValues } from "../lib/types";

// Backups on the Settings page. Two plans: Smart Recycle (one backup a day, many recent ones and
// fewer the older they get, like Synology Hyper Backup) or Custom (every rule by hand). Right under
// the plan sits a live picture of what the rules keep; every change redraws it at once and is saved
// a moment later. The list of backups with restore, pin, download and delete comes last.

type Values = Pick<
  SettingsValues,
  | "backup_plan" | "backup_schedule" | "backup_hour" | "backup_mode" | "backup_keep" | "backup_days"
  | "backup_smart_days" | "backup_smart_weeks" | "backup_smart_months" | "backup_smart_years" | "backup_max"
>;
const KEYS: (keyof Values)[] = [
  "backup_plan", "backup_schedule", "backup_hour", "backup_mode", "backup_keep", "backup_days",
  "backup_smart_days", "backup_smart_weeks", "backup_smart_months", "backup_smart_years", "backup_max",
];
const pick = (s: SettingsValues): Values => Object.fromEntries(KEYS.map((k) => [k, s[k]])) as Values;

const DAY = 24 * 3600 * 1000;
const PER_DAY: Record<BackupSchedule, number> = { hourly: 24, "6h": 4, twice: 2, daily: 1, weekly: 1 / 7, off: 0 };

// Smart Recycle always runs once a day; Custom uses its own schedule and rule.
const effective = (v: Values): Values => (v.backup_plan === "smart" ? { ...v, backup_schedule: "daily", backup_mode: "smart" } : v);

// The "how far back" slider: each step is a full set of days, weeks, months and years.
const LEVELS: [number, number, number, number][] = [
  [3, 1, 0, 0], [7, 2, 0, 0], [7, 4, 3, 0], [7, 4, 6, 0], [7, 4, 12, 0],
  [7, 4, 12, 1], [7, 4, 12, 3], [14, 8, 12, 5], [14, 8, 24, 10], [30, 12, 24, 20],
];
const reachDays = ([d, w, m, y]: number[]) => Math.max(d, w * 7, m * 30.44, y * 365.25, 1);
const tiersOf = (v: Values) => [v.backup_smart_days, v.backup_smart_weeks, v.backup_smart_months, v.backup_smart_years];
function levelOf(v: Values) {
  const now = tiersOf(v);
  const exact = LEVELS.findIndex((l) => l.every((n, i) => n === now[i]));
  if (exact >= 0) return exact;
  const r = Math.log(reachDays(now));
  return LEVELS.reduce((best, l, i) => (Math.abs(Math.log(reachDays(l)) - r) < Math.abs(Math.log(reachDays(LEVELS[best])) - r) ? i : best), 0);
}

function span(days: number) {
  if (days < 2) return t("bk.span.day");
  if (days < 21) return t("bk.span.days", { n: Math.round(days) });
  if (days < 75) return t("bk.span.weeks", { n: Math.round(days / 7) });
  if (days < 700) return t("bk.span.months", { n: Math.round(days / 30.44) });
  return t("bk.span.years", { n: Math.round(days / 365) });
}

const KIND: Record<Backup["kind"], Key> = { auto: "bk.kind.auto", manual: "bk.kind.manual", safety: "bk.kind.safety" };

function when(b: Backup) {
  const d = new Date(b.created_at);
  return `${dateShort(b.created_at)}, ${d.toLocaleTimeString(locale(), { hour: "2-digit", minute: "2-digit" })}`;
}

// "today, 17:10" for the last two days, "3 weeks ago" further back.
function ago(iso: string) {
  const days = (Date.now() - Date.parse(iso)) / DAY;
  if (days < 2) return relTime(iso);
  if (days < 21) return t("bk.ago.days", { n: Math.round(days) });
  if (days < 75) return t("bk.ago.weeks", { n: Math.round(days / 7) });
  if (days < 700) return t("bk.ago.months", { n: Math.round(days / 30.44) });
  return t("bk.ago.years", { n: Math.round(days / 365) });
}

function contents(b: Backup) {
  if (b.transactions === undefined) return t("bk.contents.unknown");
  return b.latest ? t("bk.contents", { n: int(b.transactions), date: dateShort(b.latest) }) : t("bk.contents.empty");
}

// --- what the rules keep, as places for backups ----------------------------------------

type GroupId = "pinned" | "recent" | "day" | "week" | "month" | "year" | "last" | "window";
type Slot = { key: string; group: GroupId; age: number; idx: number; backup?: Backup; cut: boolean };
type Group = { id: GroupId; slots: Slot[]; label: string; reach: string };

const startOfDay = (d: Date) => new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
const monday = (d: Date) => startOfDay(d) - ((d.getDay() + 6) % 7) * DAY;

// Ages (in days, weeks, months, years) of the places each tier holds. A tier starts where the one
// before it ends, so a backup is only counted once.
function tierAges(v: Values) {
  const [d, w, m, y] = tiersOf(v);
  const range = (from: number, to: number) => Array.from({ length: Math.max(0, to - from) }, (_, i) => from + i);
  return {
    day: range(0, d),
    week: range(Math.ceil(d / 7), w),
    month: range(Math.ceil(Math.max(w * 7, d) / 30.44), m),
    year: range(Math.ceil(Math.max(m / 12, (w * 7) / 365.25, d / 365.25)), y),
  };
}

function buildGroups(v: Values, kept: Backup[], pinned: Backup[]): Group[] {
  const e = effective(v);
  const perDay = PER_DAY[e.backup_schedule] || 1;
  const now = new Date();
  const groups: Group[] = [];
  const add = (id: GroupId, n: number, label: string, reach: string) =>
    groups.push({ id, label, reach, slots: Array.from({ length: n }, (_, age) => ({ key: `${id}-${age}`, group: id, age, idx: 0, cut: false })) });

  if (e.backup_mode === "smart") {
    const ages = tierAges(e);
    if (perDay > 1) add("recent", Math.round(perDay) - 1, t("bk.g.recent"), t("bk.span.day"));
    if (ages.day.length) add("day", ages.day.length, t("bk.g.day"), span(e.backup_smart_days));
    if (ages.week.length) add("week", ages.week.length, t("bk.g.week"), span(e.backup_smart_weeks * 7));
    if (ages.month.length) add("month", ages.month.length, t("bk.g.month"), span(e.backup_smart_months * 30.44));
    if (ages.year.length) add("year", ages.year.length, t("bk.g.year"), span(e.backup_smart_years * 365.25));
    for (const g of groups) {
      const list = g.id === "day" ? ages.day : g.id === "week" ? ages.week : g.id === "month" ? ages.month : g.id === "year" ? ages.year : null;
      if (list) g.slots.forEach((s, i) => (s.age = list[i]));
    }
    // Each backup that stays goes into the place of its day, week, month or year.
    const today = startOfDay(now);
    const thisMonday = monday(now);
    const free = (id: GroupId, age?: number) => groups.find((g) => g.id === id)?.slots.find((s) => !s.backup && (age === undefined || s.age === age));
    for (const b of kept) {
      const d = new Date(b.created_at);
      const dayAge = Math.round((today - startOfDay(d)) / DAY);
      const weekAge = Math.round((thisMonday - monday(d)) / (7 * DAY));
      const monthAge = (now.getFullYear() - d.getFullYear()) * 12 + now.getMonth() - d.getMonth();
      const yearAge = now.getFullYear() - d.getFullYear();
      const recent = now.getTime() - d.getTime() < DAY;
      const slot = free("day", dayAge) ?? (recent ? free("recent") : undefined) ?? free("week", weekAge) ?? free("month", monthAge) ?? free("year", yearAge);
      if (slot) slot.backup = b;
    }
  } else if (e.backup_mode === "last") {
    add("last", e.backup_keep, t("bk.g.last"), "");
    kept.slice(0, e.backup_keep).forEach((b, i) => (groups[0].slots[i].backup = b));
  } else {
    const n = Math.max(1, Math.round(e.backup_days * perDay));
    add("window", n, t("bk.g.window"), span(e.backup_days));
    kept.slice(0, n).forEach((b, i) => (groups[0].slots[i].backup = b));
  }

  // Newest first: number the places and cut the oldest ones beyond the limit.
  let idx = 0;
  for (const g of groups) for (const s of g.slots) {
    s.idx = idx++;
    s.cut = e.backup_max > 0 && s.idx >= e.backup_max;
  }
  if (pinned.length)
    groups.push({ id: "pinned", label: t("bk.g.pinned"), reach: "", slots: pinned.map((b, i) => ({ key: `pin-${b.name}`, group: "pinned", age: i, idx: -1, backup: b, cut: false })) });
  return groups;
}

// The picture: groups from oldest (left) to now (right), a place per backup the rules keep.
// Filled places are backups that exist, hollow ones fill up as time goes on, hatched ones are cut by
// the limit. The limit marker can be dragged.
function Picture({ groups, max, onMax, onPick, picked }: {
  groups: Group[]; max: number; onMax: (n: number) => void; onPick: (b: Backup) => void; picked: string | null;
}) {
  const [hover, setHover] = useState<Slot | null>(null);
  const strip = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);
  const total = groups.reduce((s, g) => s + (g.id === "pinned" ? 0 : g.slots.length), 0);
  // On a narrow screen the picture scrolls sideways; start at "now".
  useEffect(() => {
    const el = strip.current;
    if (el && el.scrollWidth > el.clientWidth) el.scrollLeft = el.scrollWidth;
  }, []);

  function dragTo(x: number, y: number) {
    const el = (document.elementFromPoint(x, y) as HTMLElement | null)?.closest<HTMLElement>("[data-idx]");
    if (!el || !strip.current?.contains(el)) return;
    const idx = Number(el.dataset.idx);
    if (idx >= 0) onMax(Math.max(1, idx + 1));
  }

  const caption = (s: Slot | null): ReactNode => {
    if (!s) return t("bk.pic.hint");
    const g = groups.find((x) => x.id === s.group);
    if (s.backup)
      return (
        <>
          <b>{when(s.backup)}</b> · {t(KIND[s.backup.kind])} · {contents(s.backup)}
          {s.cut ? <span className="neg"> · {t("bk.pic.cutShort")}</span> : null}
        </>
      );
    if (s.cut) return t("bk.pic.cut", { n: max });
    return t("bk.pic.empty", { what: g?.label ?? "" });
  };

  return (
    <div className="bk-pic">
      <div className="bk-strip" ref={strip}>
        {[...groups].reverse().map((g) => {
          const n = g.slots.length;
          const dense = n > 60;
          return (
            <div key={g.id} className={`bk-grp g-${g.id}${dense ? " dense" : ""}`} style={{ flexGrow: g.id === "pinned" ? 0 : Math.min(n, 40) + 2, minWidth: g.id === "pinned" ? undefined : Math.min(n, 40) * 11 + 40 }}>
              <div className="bk-cells" style={dense ? undefined : { gridTemplateColumns: `repeat(${n}, minmax(0, 26px))` }}>
                {dense ? (
                  <span className="bk-dense" style={{ ["--f" as string]: `${(g.slots.filter((s) => s.backup).length / n) * 100}%` }}>
                    <b>{int(n)}</b>
                  </span>
                ) : (
                  [...g.slots].reverse().map((s) => {
                    const cls = `bk-cell${s.backup ? ` on k-${s.backup.kind}` : ""}${s.cut ? " cut" : ""}${picked && s.backup?.name === picked ? " sel" : ""}`;
                    const limitHere = max > 0 && s.idx === max - 1 && max < total;
                    const common = {
                      className: cls,
                      "data-idx": s.idx,
                      onMouseEnter: () => setHover(s),
                      onMouseLeave: () => setHover((h) => (h === s ? null : h)),
                    };
                    return s.backup ? (
                      <button key={s.key} type="button" {...common} aria-label={`${when(s.backup)}, ${t(KIND[s.backup.kind])}`} onFocus={() => setHover(s)} onClick={() => onPick(s.backup!)}>
                        {g.id === "pinned" && <Icon name="pin" size={11} />}
                        {limitHere && <Limit max={max} dragging={dragging} dragTo={dragTo} />}
                      </button>
                    ) : (
                      <span key={s.key} {...common}>
                        {limitHere && <Limit max={max} dragging={dragging} dragTo={dragTo} />}
                      </span>
                    );
                  })
                )}
              </div>
              <div className="bk-glabel">
                <small>{g.label}</small>
                {g.reach && <em>{g.reach}</em>}
              </div>
            </div>
          );
        })}
        <div className="bk-nowmark" aria-hidden="true">
          <small>{t("bk.tick.now")}</small>
        </div>
      </div>
      <p className="bk-caption" aria-live="polite">{caption(hover)}</p>
    </div>
  );
}

function Limit({ max, dragging, dragTo }: { max: number; dragging: React.MutableRefObject<boolean>; dragTo: (x: number, y: number) => void }) {
  return (
    <span
      className="bk-limit"
      role="slider"
      tabIndex={0}
      aria-label={t("bk.max")}
      aria-valuenow={max}
      title={t("bk.pic.drag")}
      onClick={(e) => e.stopPropagation()}
      onPointerDown={(e) => {
        e.preventDefault();
        e.stopPropagation();
        dragging.current = true;
        const move = (ev: PointerEvent) => dragging.current && dragTo(ev.clientX, ev.clientY);
        const up = () => {
          dragging.current = false;
          window.removeEventListener("pointermove", move);
          window.removeEventListener("pointerup", up);
        };
        window.addEventListener("pointermove", move);
        window.addEventListener("pointerup", up);
      }}
    >
      <b>{t("bk.pic.limit", { n: max })}</b>
    </span>
  );
}

// A number with − and + buttons; every change applies at once.
function Stepper({ label, unit, value, min, max, onChange }: { label: string; unit: string; value: number; min: number; max: number; onChange: (n: number) => void }) {
  const [text, setText] = useState(String(value));
  useEffect(() => setText(String(value)), [value]);
  const set = (n: number) => onChange(Math.min(max, Math.max(min, Math.round(n))));
  return (
    <div className={`bk-step${value ? "" : " zero"}`}>
      <small>{label}</small>
      <div className="bk-stepper">
        <button type="button" className="ib" aria-label={`${label} −`} disabled={value <= min} onClick={() => set(value - 1)}>
          <Icon name="minus" size={14} />
        </button>
        <input
          className="input"
          type="number"
          inputMode="numeric"
          aria-label={label}
          min={min}
          max={max}
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            const n = Number(e.target.value);
            if (e.target.value !== "" && isFinite(n)) set(n);
          }}
          onBlur={() => setText(String(value))}
        />
        <button type="button" className="ib" aria-label={`${label} +`} disabled={value >= max} onClick={() => set(value + 1)}>
          <Icon name="plus" size={14} />
        </button>
        <span className="unit">{unit}</span>
      </div>
    </div>
  );
}

// --- the page section -----------------------------------------------------------------

export function Backups({ values, backups, nextRun, reload }: { values: SettingsValues; backups: Backup[]; nextRun?: string; reload: () => void }) {
  useT();
  const toast = useToast();
  const { confirm, dialog } = useConfirm();
  const [v, setV] = useState<Values>(() => pick(values));
  const [doomed, setDoomed] = useState<Set<string>>(new Set());
  const [selected, setSelected] = useState<string | null>(null);
  const [all, setAll] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const pending = useRef<Partial<Values>>({});
  const timer = useRef<number | undefined>(undefined);

  // Take what the server says, unless a change is still on its way there.
  useEffect(() => {
    if (!Object.keys(pending.current).length) setV(pick(values));
  }, [values]);
  useEffect(() => () => window.clearTimeout(timer.current), []);

  // Which backups the rules on screen would remove at the next backup (asked as you change them).
  const policyKey = JSON.stringify(v) + backups.map((b) => b.name + b.pinned).join();
  useEffect(() => {
    let live = true;
    const id = window.setTimeout(() => {
      api
        .post<{ remove: string[] }>("/backups/preview", v)
        .then((r) => live && setDoomed(new Set(r.remove)))
        .catch(() => live && setDoomed(new Set()));
    }, 150);
    return () => {
      live = false;
      window.clearTimeout(id);
    };
  }, [policyKey]);

  // Changes show at once and are saved a moment after the last one.
  function change(patch: Partial<Values>) {
    setV((cur) => ({ ...cur, ...patch }));
    pending.current = { ...pending.current, ...patch };
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(flush, 600);
  }
  async function flush() {
    const patch = pending.current;
    if (!Object.keys(patch).length) return;
    try {
      await api.patch("/settings", patch);
    } catch (e) {
      toast((e as Error).message);
    }
    if (pending.current === patch) pending.current = {};
    else pending.current = Object.fromEntries(Object.entries(pending.current).filter(([k, x]) => patch[k as keyof Values] !== x));
    if ("backup_plan" in patch || "backup_schedule" in patch || "backup_hour" in patch) reload();
  }

  async function backupNow() {
    setBusy("new");
    try {
      const b = await api.post<Backup>("/backups");
      toast(t("bk.saved", { size: bytes(b.size) }));
      setSelected(b.name);
      reload();
    } catch (e) {
      toast((e as Error).message);
    }
    setBusy(null);
  }

  async function pin(b: Backup) {
    await api.patch(`/backups/${encodeURIComponent(b.name)}`, { pinned: !b.pinned });
    toast(b.pinned ? t("bk.unpinnedToast") : t("bk.pinnedToast"));
    reload();
  }

  async function remove(b: Backup) {
    const ok = await confirm({ title: t("bk.delete.title"), text: t("bk.delete.text", { when: when(b) }), action: t("common.delete") });
    if (!ok) return;
    await api.del(`/backups/${encodeURIComponent(b.name)}`);
    if (selected === b.name) setSelected(null);
    reload();
  }

  async function restore(b: Backup) {
    const ok = await confirm({
      title: t("bk.restore.title", { when: when(b) }),
      text: t("bk.restore.text", { contents: contents(b) }),
      action: t("bk.restore"),
    });
    if (!ok) return;
    setBusy(b.name);
    try {
      await api.post(`/backups/${encodeURIComponent(b.name)}/restore`);
      toast(t("bk.restored"));
      window.setTimeout(() => location.reload(), 900);
    } catch (e) {
      toast((e as Error).message);
      setBusy(null);
    }
  }

  // A backup picked in the picture is shown in the list below.
  function show(b: Backup) {
    setSelected(b.name);
    if (backups.findIndex((x) => x.name === b.name) >= 6) setAll(true);
    window.requestAnimationFrame(() => listRef.current?.querySelector(`[data-name="${b.name}"]`)?.scrollIntoView({ block: "center", behavior: "smooth" }));
  }

  const e = effective(v);
  const off = e.backup_schedule === "off";
  const kept = backups.filter((b) => !b.pinned && !doomed.has(b.name));
  const pinned = backups.filter((b) => b.pinned);
  const groups = useMemo(() => buildGroups(v, kept, pinned), [JSON.stringify(v), backups, doomed]);
  const places = groups.filter((g) => g.id !== "pinned").reduce((s, g) => s + g.slots.length, 0);
  const keeps = e.backup_max > 0 ? Math.min(places, e.backup_max) : places;
  const total = backups.reduce((s, b) => s + b.size, 0);
  const reach =
    e.backup_mode === "smart"
      ? reachDays(tiersOf(e))
      : e.backup_mode === "days"
        ? e.backup_days
        : e.backup_keep / Math.max(PER_DAY[e.backup_schedule], 1 / 7);
  // With a limit, the picture reaches only as far back as the last place inside it.
  const lastIn = e.backup_max > 0 && places > e.backup_max ? groups.flatMap((g) => g.slots).find((s) => s.idx === e.backup_max - 1) : undefined;
  const reachShown = !lastIn
    ? reach
    : lastIn.group === "week"
      ? (lastIn.age + 1) * 7
      : lastIn.group === "month"
        ? (lastIn.age + 1) * 30.44
        : lastIn.group === "year"
          ? (lastIn.age + 1) * 365.25
          : lastIn.group === "day"
            ? lastIn.age + 1
            : reach * (e.backup_max / places);
  const nDoomed = backups.filter((b) => doomed.has(b.name)).length;
  const shown = all ? backups : backups.slice(0, 6);
  const level = levelOf(e);
  const hourOptions = Array.from({ length: 24 }, (_, h) => [String(h), `${String(h).padStart(2, "0")}:00`] as [string, string]);

  const tierSteppers = (
    <div className="bk-steps">
      <Stepper label={t("bk.l.days")} unit={t("bk.unit.days")} value={v.backup_smart_days} min={0} max={365} onChange={(n) => change({ backup_smart_days: n })} />
      <Stepper label={t("bk.l.weeks")} unit={t("bk.unit.weeks")} value={v.backup_smart_weeks} min={0} max={520} onChange={(n) => change({ backup_smart_weeks: n })} />
      <Stepper label={t("bk.l.months")} unit={t("bk.unit.months")} value={v.backup_smart_months} min={0} max={240} onChange={(n) => change({ backup_smart_months: n })} />
      <Stepper label={t("bk.l.years")} unit={t("bk.unit.years")} value={v.backup_smart_years} min={0} max={50} onChange={(n) => change({ backup_smart_years: n })} />
    </div>
  );
  const depthSlider = (
    <label className="bk-depth">
      <span>
        {t("bk.depth")} <b>{span(reachDays(LEVELS[level]))}</b>
      </span>
      <input
        type="range"
        min={0}
        max={LEVELS.length - 1}
        step={1}
        value={level}
        style={{ ["--p" as string]: `${(level / (LEVELS.length - 1)) * 100}%` }}
        onChange={(ev) => {
          const [d, w, m, y] = LEVELS[Number(ev.target.value)];
          change({ backup_smart_days: d, backup_smart_weeks: w, backup_smart_months: m, backup_smart_years: y });
        }}
      />
      <span className="bk-depth-ends">
        <small>{t("bk.depth.short")}</small>
        <small>{t("bk.depth.long")}</small>
      </span>
    </label>
  );
  const limitRow = (
    <div className="srow">
      <div className="t">
        <b>{t("bk.max")}</b>
        <small>{t("bk.max.sub")}</small>
      </div>
      <span className="hstack">
        {e.backup_max > 0 && <Stepper label={t("bk.max")} unit={t("bk.unit.backups")} value={e.backup_max} min={1} max={1000} onChange={(n) => change({ backup_max: n })} />}
        <Switch label={t("bk.max")} checked={e.backup_max > 0} onChange={(on) => change({ backup_max: on ? Math.max(1, Math.min(60, places - 1)) : 0 })} />
      </span>
    </div>
  );

  return (
    <>
      <Card
        className="span-all bk-main"
        title={t("bk.backups")}
        sub={backups.length ? t("bk.summary", { n: backups.length, size: bytes(total), when: relTime(backups[0].created_at) }) : t("bk.none")}
        right={
          <span className="hstack">
            {nextRun && !off && <span className="muted small">{t("bk.next", { when: whenNext(nextRun) })}</span>}
            <button className="btn sm primary" onClick={backupNow} disabled={busy !== null}>
              {busy === "new" ? <Spinner /> : <Icon name="plus" size={15} />}
              {t("bk.now")}
            </button>
          </span>
        }
      >
        <div className="bk-plans" role="radiogroup" aria-label={t("bk.plan")}>
          {(["smart", "custom"] as BackupPlan[]).map((p) => (
            <button key={p} type="button" role="radio" aria-checked={v.backup_plan === p} className={`bk-planbtn${v.backup_plan === p ? " on" : ""}`} onClick={() => change({ backup_plan: p })}>
              <span className="bk-planhead">
                <b>{t(p === "smart" ? "bk.p.smart" : "bk.p.custom")}</b>
                {p === "smart" && <span className="tag">{t("bk.p.recommended")}</span>}
              </span>
              <small>{t(p === "smart" ? "bk.p.smart.sub" : "bk.p.custom.sub")}</small>
            </button>
          ))}
        </div>

        <div className="bk-sentence">
          {off ? (
            t("bk.outcome.off")
          ) : (
            <>
              {t("bk.s1")} <b>{t("bk.s1.n", { n: keeps })}</b> {t("bk.s2")} <b>{span(reachShown)}</b>
              {t("bk.s2b") && ` ${t("bk.s2b")}`}
              {total > 0 && backups[0] && (
                <span className="muted"> · {t("bk.s3", { size: bytes(keeps * backups[0].size) })}</span>
              )}
              {e.backup_max > 0 && e.backup_max >= places && <span className="muted"> · {t("bk.s4", { n: e.backup_max })}</span>}
            </>
          )}
        </div>

        {!off && <Picture groups={groups} max={e.backup_max} onMax={(n) => change({ backup_max: n })} onPick={show} picked={selected} />}
        {nDoomed > 0 && <p className="bk-doomed">{t("bk.outcome.doomed", { n: nDoomed })}</p>}

        {v.backup_plan === "smart" ? (
          <div className="bk-controls">
            {depthSlider}
            {tierSteppers}
            <div className="srow">
              <div className="t">
                <b>{t("bk.time")}</b>
                <small>{t("bk.time.sub")}</small>
              </div>
              <Dropdown label={t("bk.hour")} value={String(v.backup_hour)} options={hourOptions} onChange={(h) => change({ backup_hour: Number(h) })} />
            </div>
            {limitRow}
          </div>
        ) : (
          <div className="bk-controls">
            <div className="srow">
              <div className="t">
                <b>{t("bk.schedule")}</b>
                <small>{off ? t("bk.schedule.off") : t("bk.schedule.sub")}</small>
              </div>
              <span className="hstack">
                <Seg<BackupSchedule>
                  label={t("bk.schedule")}
                  value={v.backup_schedule}
                  onChange={(x) => change({ backup_schedule: x })}
                  options={[
                    ["off", t("bk.s.off")],
                    ["hourly", t("bk.s.hourly")],
                    ["6h", t("bk.s.6h")],
                    ["twice", t("bk.s.twice")],
                    ["daily", t("bk.s.daily")],
                    ["weekly", t("bk.s.weekly")],
                  ]}
                />
                {!off && v.backup_schedule !== "hourly" && (
                  <Dropdown label={t("bk.hour")} value={String(v.backup_hour)} options={hourOptions} onChange={(h) => change({ backup_hour: Number(h) })} />
                )}
              </span>
            </div>
            <div className="srow">
              <div className="t">
                <b>{t("bk.keep")}</b>
                <small>{t(`bk.m.${v.backup_mode}.sub` as Key)}</small>
              </div>
              <Seg<BackupMode>
                label={t("bk.keep")}
                value={v.backup_mode}
                onChange={(x) => change({ backup_mode: x })}
                options={[
                  ["last", t("bk.m.last")],
                  ["days", t("bk.m.days")],
                  ["smart", t("bk.m.smart")],
                ]}
              />
            </div>
            {v.backup_mode === "last" && (
              <div className="bk-steps one">
                <Stepper label={t("bk.keepLast")} unit={t("bk.unit.backups")} value={v.backup_keep} min={1} max={365} onChange={(n) => change({ backup_keep: n })} />
              </div>
            )}
            {v.backup_mode === "days" && (
              <div className="bk-steps one">
                <Stepper label={t("bk.keepDays")} unit={t("bk.unit.days")} value={v.backup_days} min={1} max={3650} onChange={(n) => change({ backup_days: n })} />
              </div>
            )}
            {v.backup_mode === "smart" && (
              <>
                {depthSlider}
                {tierSteppers}
              </>
            )}
            {!off && limitRow}
          </div>
        )}
      </Card>

      <Card className="span-all bk-listcard" title={t("bk.list")} sub={t("bk.list.sub")}>
        <div className="bk-list" ref={listRef}>
          {shown.map((b) => (
            <div key={b.name} data-name={b.name} className={`bk-row${selected === b.name ? " sel" : ""}${doomed.has(b.name) ? " doomed" : ""}`}>
              <i className={`bk-kind k-${b.kind}${b.pinned ? " pinned" : ""}`} />
              <div className="bk-when">
                <b>{when(b)}</b>
                <small>{ago(b.created_at)}</small>
              </div>
              <div className="bk-what">
                <span>{contents(b)}</span>
                <small>
                  {t(KIND[b.kind])} · {bytes(b.size)}
                </small>
              </div>
              <div className="bk-tags">
                {b.pinned && <span className="tag good">{t("bk.pinned")}</span>}
                {doomed.has(b.name) && <span className="tag bad">{t("bk.doomedShort")}</span>}
              </div>
              <div className="bk-acts">
                <button className="btn sm" onClick={() => restore(b)} disabled={busy !== null}>
                  {busy === b.name ? <Spinner /> : <Icon name="rewind" size={15} />}
                  {t("bk.restore")}
                </button>
                <button className={`ib${b.pinned ? " on" : ""}`} aria-pressed={b.pinned} aria-label={b.pinned ? t("bk.unpin") : t("bk.pin")} title={b.pinned ? t("bk.unpin") : t("bk.pin")} onClick={() => pin(b)}>
                  <Icon name="pin" size={15} />
                </button>
                <a className="ib" href={`/api/backups/${encodeURIComponent(b.name)}`} download aria-label={t("bk.download")} title={t("bk.download")}>
                  <Icon name="download" size={15} />
                </a>
                <button className="ib" aria-label={t("common.delete")} title={t("common.delete")} onClick={() => remove(b)}>
                  <Icon name="trash" size={15} />
                </button>
              </div>
            </div>
          ))}
          {!backups.length && <p className="txsum">{t("bk.none")}</p>}
        </div>
        {backups.length > 6 && (
          <button className="btn sm ghost" onClick={() => setAll(!all)}>
            {all ? t("bk.showLess") : t("bk.showAll", { n: backups.length })}
          </button>
        )}
        <p className="txsum">{t("bk.note")}</p>
      </Card>
      {dialog}
    </>
  );
}
