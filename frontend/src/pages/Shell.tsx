import { useState, type ReactNode } from "react";
import { TanPrompt } from "../components/BankForm";
import { confirmBankLogin, DialogHost, openDialog } from "../components/Dialogs";
import { Icon, Logo } from "../components/Icons";
import { usePointerEffects } from "../components/Motion";
import { Dropdown, Spinner, useToast } from "../components/UI";
import { locale, t, useT, type Key } from "../i18n";
import { useApp, type Period } from "../lib/app";
import { dateShort, initial, relTime } from "../lib/format";
import type { Connection } from "../lib/types";
import { hideAmounts, useHidden, useHideWanted } from "../lib/privacy";
import { decodePart, navigate, usePath } from "../lib/router";
import CashFlow from "./CashFlow";
import Drilldown from "./Drilldown";
import Fund from "./Fund";
import Investments from "./Investments";
import NetWorth from "./NetWorth";
import Recurring, { OldAddress } from "./Recurring";
import Settings from "./Settings";
import Spending from "./Spending";
import Transactions from "./Transactions";

// Five places, in the order a month is lived: where you stand, what happened, where it went,
// what comes back every month, and what you own. The depot sits under what you own, and its
// forecast, analysis and payments under the depot.
type NavItem = { to: string; icon: string; label: Key; child?: 1 | 2 };
export const MAIN_NAV: NavItem[] = [
  { to: "/", icon: "home", label: "nav.overview" },
  { to: "/transactions", icon: "list", label: "nav.transactions" },
  { to: "/spending", icon: "pie", label: "nav.spending" },
  { to: "/recurring", icon: "repeat", label: "nav.recurring", child: 1 },
  { to: "/networth", icon: "vault", label: "nav.networth" },
  { to: "/investments", icon: "etf", label: "nav.investments", child: 1 },
  { to: "/investments/forecast", icon: "trend", label: "inv.tab.forecast", child: 2 },
  { to: "/investments/analysis", icon: "spark", label: "inv.tab.analysis", child: 2 },
  { to: "/investments/payments", icon: "coin", label: "inv.tab.payments", child: 2 },
];

const isOn = (path: string, to: string) => (to === "/" ? path === "/" : path === to || path.startsWith(`${to}/`));

// The custom groups live with the spending they belong to.
function navOn(path: string, to: string) {
  if (to === "/spending") return isOn(path, to) || path.startsWith("/groups/");
  // The depot's own pages have their own entries; an ETF's page belongs to the depot.
  if (to === "/investments") return path === to || path.startsWith("/investments/etf/");
  return isOn(path, to);
}

function NavButton({ item, badge }: { item: NavItem; badge?: ReactNode }) {
  const path = usePath();
  const t = useT();
  const on = navOn(path, item.to);
  return (
    <button className={`nav${on ? " on" : ""}${item.child ? " child" : ""}${item.child === 2 ? " child2" : ""}`} aria-current={on ? "page" : undefined} onClick={() => navigate(item.to)}>
      <Icon name={item.icon} />
      <span className="nav-l">{t(item.label)}</span>
      {badge}
    </button>
  );
}

function navBadge(to: string, badges: ReturnType<typeof useApp>["badges"]): ReactNode {
  if (to === "/transactions" && badges?.review) return <span className="badge" title={t("nav.badge.review", { n: badges.review })}>{badges.review}</span>;
  if (to === "/" && badges?.alerts) return <span className="badge dot" title={t("nav.badge.alerts", { n: badges.alerts })} />;
  return null;
}

// With several banks, the one to show: one that needs attention, else the next login due.
function mostUrgent(connections: Connection[]): Connection | undefined {
  return [...connections].sort((a, b) => Number(b.status === "error") - Number(a.status === "error") || a.login_days_left - b.login_days_left)[0];
}

// The bank connection in one line, and the button that syncs it. In the sidebar on a computer,
// as a small chip in the top bar on a phone.
function SyncBox({ compact = false }: { compact?: boolean }) {
  const { connections, syncing, sync, badges } = useApp();
  const t = useT();
  const c = mostUrgent(connections);
  if (!c) {
    if (compact) return null;
    return (
      <button className="syncbox" onClick={() => openDialog({ kind: "connect" })}>
        <Icon name="bank" size={16} />
        <span className="sb-txt">
          <b>{t("shell.connectBank")}</b>
          <small>{t("shell.usingCsv")}</small>
        </span>
      </button>
    );
  }
  const left = c.login_days_left;
  // The 90-day bank login only gets a line once it is close; until then it is one more number to read.
  const due = left <= (badges?.reminder_days ?? 15);
  const state = syncing ? (syncing.state === "waiting" ? t("shell.approve") : t("shell.syncing")) : c.status === "error" ? t("shell.attention", { bank: c.label }) : connections.length > 1 ? t("shell.connectedMany", { n: connections.length }) : t("shell.connected", { bank: c.label });
  const dot = syncing ? <Spinner /> : <span className={c.status === "error" ? "dotbad" : "dotok"} />;
  if (compact) {
    return (
      <button className="syncchip" onClick={() => sync()} disabled={!!syncing} aria-label={`${state}. ${t("shell.syncNow")}`}>
        {dot}
        {syncing ? t("shell.syncingShort") : relTime(c.last_sync_at)}
      </button>
    );
  }
  return (
    <button className={`syncbox${syncing ? " busy" : ""}`} onClick={() => sync()} disabled={!!syncing} title={t("shell.syncNow")}>
      {dot}
      <span className="sb-txt">
        <b>{state}</b>
        <small>{t("shell.synced", { when: relTime(c.last_sync_at) })}</small>
        {due && <small className={left <= 3 ? "neg" : "warn"}>{left > 0 ? t("shell.loginIn", { n: left, bank: c.label }) : t("shell.loginNow", { bank: c.label })}</small>}
      </span>
      <Icon name="refresh" size={15} className="sb-go" />
    </button>
  );
}

// The eye in the corner: hides every amount for a screen someone else can see, and brings them back.
// It blinks when clicked, and a slash crosses it while amounts are hidden.
function HideToggle({ small = false }: { small?: boolean }) {
  const t = useT();
  const hidden = useHideWanted();
  const [blinks, setBlinks] = useState(0);
  const size = small ? 16 : 18;
  return (
    <button
      type="button"
      className={`ib hide-btn${small ? " sm" : ""}${hidden ? " on" : ""}`}
      aria-pressed={hidden}
      aria-label={t("hide.hide")}
      title={hidden ? t("hide.show") : t("hide.hide")}
      onClick={() => {
        hideAmounts(!hidden);
        setBlinks((n) => n + 1);
      }}
    >
      <svg key={blinks} viewBox="0 0 24 24" width={size} height={size} className={blinks ? "eye blink" : "eye"} aria-hidden="true" focusable="false">
        <g className="eye-lid">
          <path d="M2.5 12s3.4-6.5 9.5-6.5 9.5 6.5 9.5 6.5-3.4 6.5-9.5 6.5S2.5 12 2.5 12z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
          <circle cx="12" cy="12" r="2.7" fill="none" stroke="currentColor" strokeWidth="1.8" />
        </g>
        <path className="eye-slash" d="M4.5 4.5l15 15" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" pathLength={1} />
      </svg>
    </button>
  );
}

// eyebrow: a small line above the title (the date on the Overview, the parent page elsewhere).
// period: the shared period picker, always at the right end so it sits in the same place on every page.
export function PageHeader({ title, eyebrow, period, actions }: { title: ReactNode; eyebrow?: ReactNode; period?: boolean; actions?: ReactNode }) {
  return (
    <header className="ph">
      <div className="ph-t">
        {eyebrow && <div className="ph-eyebrow">{eyebrow}</div>}
        <h1>{title}</h1>
      </div>
      {(actions || period) && (
        <div className="ph-actions">
          {actions}
          {period && <PeriodPicker />}
        </div>
      )}
    </header>
  );
}

function shift(p: Period, dir: number): Period {
  const today = new Date();
  const base = p.anchor ? new Date(`${p.anchor}T12:00:00`) : today;
  if (p.preset === "month") base.setMonth(base.getMonth() + dir, 1);
  else base.setFullYear(base.getFullYear() + dir, 0, 1);
  const iso = `${base.getFullYear()}-${String(base.getMonth() + 1).padStart(2, "0")}-01`;
  return { preset: p.preset, anchor: iso };
}

export function periodLabel(p: Period) {
  const today = new Date();
  const base = p.anchor ? new Date(`${p.anchor}T12:00:00`) : today;
  if (p.preset === "month") return base.toLocaleDateString(locale(), { month: "long", year: "numeric" });
  if (p.preset === "year") return String(base.getFullYear());
  if (p.preset === "last30") return t("period.last30");
  if (p.preset === "last12") return t("period.last12");
  if (p.preset === "all") return t("period.all");
  const short = (d: Date) => d.toLocaleDateString(locale(), { month: "short" }).replace(".", "");
  return `${short(new Date(today.getFullYear(), 0, 15))} – ${short(today)} ${today.getFullYear()}`;
}

const PRESETS: [Period["preset"], Key][] = [
  ["month", "period.month"],
  ["last30", "period.last30"],
  ["ytd", "period.ytd"],
  ["year", "period.year"],
  ["last12", "period.last12"],
  ["all", "period.all"],
];

// One control for the period every page shows: step back and forth (months and years),
// or open the menu for another kind of period.
function PeriodPicker() {
  const { period, setPeriod } = useApp();
  const t = useT();
  const steppable = period.preset === "month" || period.preset === "year";
  const now = new Date();
  const atEnd =
    !period.anchor ||
    (period.preset === "month"
      ? period.anchor.slice(0, 7) >= `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`
      : Number(period.anchor.slice(0, 4)) >= now.getFullYear());
  return (
    <div className={`period${steppable ? " steps" : ""}`}>
      {steppable && (
        <button className="ib" aria-label={t("period.prev")} onClick={() => setPeriod(shift(period, -1))}>
          <Icon name="chevRight" size={15} className="flip" />
        </button>
      )}
      <Dropdown<Period["preset"]>
        label={t("period.label")}
        value={period.preset}
        display={periodLabel(period)}
        icon="calendar"
        options={PRESETS.map(([k, label]) => [k, t(label)])}
        onChange={(preset) => setPeriod({ preset, anchor: null })}
      />
      {steppable && (
        <button className="ib" aria-label={t("period.next")} disabled={atEnd} onClick={() => setPeriod(shift(period, 1))}>
          <Icon name="chevRight" size={15} />
        </button>
      )}
    </div>
  );
}

function Page({ path }: { path: string }) {
  if (path.startsWith("/investments/etf/")) return <Fund isin={decodePart(path.slice("/investments/etf/".length)).toUpperCase()} />;
  if (path.startsWith("/groups/")) return <Drilldown custom={Number(path.split("/")[2])} />;
  if (path.startsWith("/spending/group/")) return <Drilldown group={decodePart(path.slice("/spending/group/".length))} />;
  if (path.startsWith("/spending/category/")) return <Drilldown category={Number(path.split("/")[3])} />;
  if (path.startsWith("/spending/payee/")) return <Drilldown merchant={decodePart(path.slice("/spending/payee/".length))} />;
  switch (path) {
    case "/":
      return <CashFlow />;
    case "/transactions":
      return <Transactions />;
    case "/spending":
      return <Spending />;
    case "/networth":
      return <NetWorth />;
    case "/investments":
      return <Investments page="overview" />;
    case "/investments/forecast":
      return <Investments page="forecast" />;
    case "/investments/analysis":
      return <Investments page="analysis" />;
    case "/investments/payments":
      return <Investments page="payments" />;
    case "/recurring":
      return <Recurring />;
    case "/settings":
      return <Settings />;
    // Old addresses, from bookmarks and earlier versions.
    case "/subscriptions":
      return <OldAddress to="/recurring" />;
    case "/calendar":
      return <OldAddress to="/recurring?view=calendar" />;
    default:
      return <OldAddress to="/" />;
  }
}

// The 90-day login reminder, on every page but Settings once it is due.
function LoginBanner() {
  const { connections, badges, refresh } = useApp();
  const toast = useToast();
  const t = useT();
  const path = usePath();
  const c = mostUrgent(connections);
  if (!c || c.login_days_left > (badges?.reminder_days ?? 15) || path === "/settings") return null;
  return (
    <div className="banner" role="status">
      <Icon name="lock" size={17} />
      <span>
        <b>{t("shell.loginBanner", { bank: c.label, date: dateShort(c.login_due) })}</b> {t("shell.loginBanner.why")}
      </span>
      <button className="btn sm" onClick={() => confirmBankLogin(c, toast, refresh)}>
        <Icon name="check" size={15} />
        {t("set.loggedIn")}
      </button>
    </div>
  );
}

export default function Shell() {
  const { badges, status, logout, syncing } = useApp();
  const t = useT();
  const path = usePath();
  // Every page draws its amounts again when they are hidden or shown.
  useHidden();
  const name = status.user?.name || status.user?.username || "";
  usePointerEffects();
  return (
    <div className="app">
      <aside className="side">
        <div className="side-top">
          <div className="brand">
            <Logo />
            <span>Groschen</span>
          </div>
          <HideToggle small />
        </div>
        <nav className="side-nav" aria-label={t("nav.main")}>
          {MAIN_NAV.map((item) => (
            <NavButton key={item.to} item={item} badge={navBadge(item.to, badges)} />
          ))}
        </nav>
        <div className="side-foot">
          <SyncBox />
          <NavButton item={{ to: "/settings", icon: "gear", label: "nav.settings" }} />
          <div className="side-user">
            <span className="av" aria-hidden="true">
              {initial(name)}
            </span>
            <span className="nm">{name}</span>
            <button className="ib sm" aria-label={t("nav.logout")} title={t("nav.logout")} onClick={logout}>
              <Icon name="logout" size={15} />
            </button>
          </div>
        </div>
      </aside>
      <div className="topbar">
        <div className="brand">
          <Logo />
          <span>Groschen</span>
        </div>
        <SyncBox compact />
        <HideToggle />
        <button className={`ib${path === "/settings" ? " on" : ""}`} aria-label={t("nav.settings")} onClick={() => navigate("/settings")}>
          <Icon name="gear" size={17} />
        </button>
      </div>
      <main className="main">
        <LoginBanner />
        <div className="page" key={path}>
          <Page path={path} />
        </div>
      </main>
      <nav className="tabbar" aria-label={t("nav.main")}>
        {MAIN_NAV.filter((i) => !i.child).map((item) => {
          const on = navOn(path, item.to) || (item.to === "/networth" && path.startsWith("/investments")) || (item.to === "/spending" && path.startsWith("/recurring"));
          return (
            <button key={item.to} className={on ? "on" : ""} aria-current={on ? "page" : undefined} onClick={() => navigate(item.to)}>
              <span className="tb-ic">
                <Icon name={item.icon} />
                {item.to === "/transactions" && badges?.review ? <span className="tb-badge" /> : null}
              </span>
              {t(item.label)}
            </button>
          );
        })}
      </nav>
      <DialogHost />
      <TanPrompt job={syncing} />
    </div>
  );
}
