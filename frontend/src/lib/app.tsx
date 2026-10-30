import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { celebrate } from "../components/Motion";
import { useToast } from "../components/UI";
import { t } from "../i18n";
import { api } from "./api";
import type { Badges, Connection, Job, Status, UserGroup } from "./types";

export type Period = { preset: "ytd" | "last30" | "month" | "year" | "last12" | "all"; anchor: string | null };

type AppState = {
  status: Status;
  connections: Connection[];
  badges: Badges | null;
  groups: UserGroup[];
  period: Period;
  setPeriod: (p: Period) => void;
  syncing: Job | null;
  sync: (full?: boolean) => void;
  refresh: () => void;
  logout: () => void;
};

const Ctx = createContext<AppState | null>(null);
export const useApp = () => {
  const v = useContext(Ctx);
  if (!v) throw new Error("useApp outside AppProvider");
  return v;
};

export async function pollJob<R>(job: Job<R>, onUpdate: (j: Job<R>) => void): Promise<Job<R>> {
  let current = job;
  onUpdate(current);
  while (current.state === "running" || current.state === "waiting") {
    await new Promise((r) => setTimeout(r, 1200));
    current = await api.get<Job<R>>(`/jobs/${current.id}`);
    onUpdate(current);
  }
  return current;
}

function loadPeriod(): Period {
  try {
    const raw = localStorage.getItem("groschen.period");
    if (raw) {
      const p = JSON.parse(raw) as Period;
      if (["ytd", "last30", "month", "year", "last12", "all"].includes(p.preset)) return { preset: p.preset, anchor: null };
    }
  } catch {
    /* private window or blocked storage: use the default */
  }
  return { preset: "ytd", anchor: null };
}

export function AppProvider({ status, onLogout, children }: { status: Status; onLogout: () => void; children: ReactNode }) {
  const toast = useToast();
  const [connections, setConnections] = useState<Connection[]>([]);
  const [badges, setBadges] = useState<Badges | null>(null);
  const [groups, setGroups] = useState<UserGroup[]>([]);
  const [period, setPeriodState] = useState<Period>(loadPeriod);
  const [syncing, setSyncing] = useState<Job | null>(null);
  const busy = useRef(false);

  const refresh = useCallback(() => {
    api.get<Connection[]>("/connections").then(setConnections).catch(() => {});
    api.get<Badges>("/badges").then(setBadges).catch(() => {});
    api.get<UserGroup[]>("/groups").then(setGroups).catch(() => {});
  }, []);

  useEffect(() => {
    refresh();
    const id = window.setInterval(refresh, 5 * 60 * 1000);
    return () => window.clearInterval(id);
  }, [refresh]);

  const setPeriod = useCallback((p: Period) => {
    setPeriodState(p);
    try {
      localStorage.setItem("groschen.period", JSON.stringify({ preset: p.preset }));
    } catch {
      /* ignore */
    }
  }, []);

  const sync = useCallback(
    async (full = false) => {
      if (busy.current) return;
      busy.current = true;
      try {
        const job = await api.post<Job>(`/sync${full ? "?full=true" : ""}`);
        let told = false;
        const done = await pollJob(job, (j) => {
          setSyncing(j);
          if (j.state === "waiting" && !told) {
            told = true;
            toast(j.message || t("sync.approve"));
          }
        });
        if (done.state === "done") {
          const n = Number(done.result?.transactions ?? 0);
          toast(n ? t("sync.done", { n }) : t("sync.nothingNew"));
          if (n) celebrate(document.querySelector(".side-sync") ?? document.querySelector(".ph-actions"), Math.min(8 + n, 24));
          window.dispatchEvent(new Event("groschen:synced"));
        } else {
          toast(done.error || t("sync.failed"));
        }
      } catch (e) {
        toast((e as Error).message);
      } finally {
        busy.current = false;
        setSyncing(null);
        refresh();
      }
    },
    [refresh, toast],
  );

  const logout = useCallback(() => {
    api.post("/logout").finally(onLogout);
  }, [onLogout]);

  return (
    <Ctx.Provider value={{ status, connections, badges, groups, period, setPeriod, syncing, sync, refresh, logout }}>
      {children}
    </Ctx.Provider>
  );
}

export function periodQuery(p: Period) {
  return { preset: p.preset, anchor: p.anchor ?? undefined };
}

const isoDay = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

// First and last day of a period, the same way the server resolves it (analytics/common.py).
export function periodBounds(p: Period, today = new Date()): { start: string; end: string } {
  const now = isoDay(today);
  const a = p.anchor ? new Date(`${p.anchor}T12:00:00`) : today;
  const upTo = (e: string) => (e < now ? e : now);
  if (p.preset === "month") return { start: isoDay(new Date(a.getFullYear(), a.getMonth(), 1)), end: upTo(isoDay(new Date(a.getFullYear(), a.getMonth() + 1, 0))) };
  if (p.preset === "year") return { start: `${a.getFullYear()}-01-01`, end: upTo(`${a.getFullYear()}-12-31`) };
  if (p.preset === "last30") return { start: isoDay(new Date(today.getFullYear(), today.getMonth(), today.getDate() - 29)), end: now };
  if (p.preset === "last12") return { start: isoDay(new Date(today.getFullYear(), today.getMonth() - 11, 1)), end: now };
  if (p.preset === "all") return { start: "1900-01-01", end: now };
  return { start: `${today.getFullYear()}-01-01`, end: now };
}

// The monthly points of a series that fall in the period, led by the month before it, so a line
// starts where the period starts (a single month still draws from its opening to its closing value).
// Same as clipMonths for a series by day; the point just before the period keeps the line joined.
export function clipDays<T extends { date: string }>(series: T[], p: Period): T[] {
  const { start, end } = periodBounds(p);
  const inside = series.filter((x) => x.date >= start && x.date <= end);
  if (!inside.length) return [];
  const before = series.filter((x) => x.date < start);
  return before.length ? [before[before.length - 1], ...inside] : inside;
}

export function clipMonths<T extends { month: string }>(series: T[], p: Period): T[] {
  const { start, end } = periodBounds(p);
  const s = start.slice(0, 7), e = end.slice(0, 7);
  const inside = series.filter((x) => x.month >= s && x.month <= e);
  if (!inside.length) return [];
  const before = series.filter((x) => x.month < s);
  return before.length ? [before[before.length - 1], ...inside] : inside;
}
