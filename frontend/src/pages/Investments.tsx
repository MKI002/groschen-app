import { useMemo, useState } from "react";
import { DrawdownChart, Heatmap, Sparkline } from "../components/Charts";
import { extremes, HighTag, MonthsUp, ReturnCard, SwingCard } from "../components/Analysis";
import { DepotChart } from "../components/DepotChart";
import { Forecast } from "../components/Forecast";
import { InvestPayments } from "../components/InvestPayments";
import { PayoutTag } from "../components/Payout";
import { Icon } from "../components/Icons";
import { Odometer } from "../components/Motion";
import { Card, ChangePill, Dropdown, Empty, ErrorNote, Loading, Spinner, Tabs, useApi, useSyncEvents, useToast } from "../components/UI";
import { useZoom } from "../components/Zoom";
import { getRegion, t as tr, useT } from "../i18n";
import { germanTax } from "../lib/regions";
import { api } from "../lib/api";
import { clipMonths, periodBounds, useApp, type Period } from "../lib/app";
import { gainBetween, monthlyReturns, performance, periodSpan, thin, timeOf, xirrBetween, type DayPoint } from "../lib/depot";
import { dateShort, dayMonth, eur, eur0, fundName, monthLabel, monthLong, pct, pctS } from "../lib/format";
import { navigate, redirect, useSearch } from "../lib/router";
import { OldAddress } from "./Recurring";
import type { Holding, Investments as Inv } from "../lib/types";
import { PageHeader, periodLabel } from "./Shell";

export const FUND_COLORS = ["var(--accent)", "var(--c-teal)", "var(--c-blue)", "var(--c-violet)", "var(--c-pink)", "var(--c-amber)"];

// Prices from before the first sync come from a file; the button sits with the payments that use them.
function PriceImport() {
  useT();
  const toast = useToast();
  const [busy, setBusy] = useState(false);
  async function upload(files: FileList | null) {
    const f = files?.[0];
    if (!f) return;
    setBusy(true);
    const form = new FormData();
    form.append("file", f);
    try {
      const r = await api.upload<{ imported: number }>("/import/prices", form);
      toast(tr("set.importedPrices", { n: r.imported }));
      window.dispatchEvent(new Event("groschen:synced"));
    } catch (e) {
      toast(`${f.name}: ${(e as Error).message}`);
    }
    setBusy(false);
  }
  return (
    <>
      <label className="btn sm ghost" htmlFor="inv-prices" title={tr("set.priceHistory.sub")}>
        {busy ? <Spinner /> : <Icon name="upload" size={15} />}
        {tr("inv.importPrices")}
      </label>
      <input id="inv-prices" type="file" accept=".csv,.txt,text/csv" hidden onChange={(e) => upload(e.target.files)} />
    </>
  );
}

type SortKey = "value" | "gain" | "name";

// What a card shows for one ETF: since it was bought, or over the stretch of time the page looks at.
type HoldView = { value: number; gain: number | null; rate: number | null; spark?: number[]; share: number };
const sinceBought = (h: Holding): HoldView => ({
  value: h.value,
  gain: h.cost !== null ? h.value - h.cost : null,
  rate: h.cost ? (h.value - h.cost) / h.cost : null,
  spark: h.spark,
  share: h.share,
});

// One ETF as a card: name, value, what it gained, its line and its share of the depot.
// Everything else is one click away on the ETF's own page.
function HoldingCard({ h, v, color, i }: { h: Holding; v: HoldView; color: string; i: number }) {
  const t = useT();
  return (
    <button type="button" className="hold stagger" style={{ ["--i" as string]: i, ["--c" as string]: color }} onClick={() => navigate(`/investments/etf/${h.isin}`)}>
      <span className="hold-top">
        <span className="hold-name">
          <b>{fundName(h.name)}</b>
          <small>{h.isin}</small>
        </span>
        <Icon name="chevRight" size={15} className="hold-go" />
      </span>
      <span className="hold-v">{eur(v.value)}</span>
      <span className="hold-mid">
        {v.gain !== null && <ChangePill up={v.gain >= 0} good={v.gain >= 0} text={`${pctS(v.rate)} · ${eur0(Math.abs(v.gain))}`} />}
        {v.spark && v.spark.length > 2 && <Sparkline values={v.spark} width={110} height={30} />}
      </span>
      <span className="hold-foot">
        <span className="meter" aria-hidden="true">
          <span style={{ ["--p" as string]: `${(v.share * 100).toFixed(1)}%` }} />
        </span>
        <small>{t("inv.ofDepot", { p: pct(v.share, 0) })}</small>
        {h.plan ? <span className="tag accent">{t("inv.planShort", { amount: eur0(h.plan) })}</span> : null}
        <PayoutTag policy={h.payout?.policy} frequency={h.payout?.frequency} />
      </span>
    </button>
  );
}

// views: each ETF over the stretch of time in view (ETFs not held then are left out); null shows
// them since they were bought.
function Holdings({ holdings, views, when }: { holdings: Holding[]; views: Map<string, HoldView> | null; when: string | null }) {
  const t = useT();
  const [sort, setSort] = useState<SortKey>("value");
  const colors = useMemo(() => new Map(holdings.map((h, i) => [h.isin, FUND_COLORS[i % FUND_COLORS.length]])), [holdings]);
  const rows = useMemo(() => {
    const list = holdings.flatMap((h) => {
      const v = views ? views.get(h.isin) : sinceBought(h);
      return v ? [{ h, v }] : [];
    });
    return list.sort((a, b) =>
      sort === "name" ? fundName(a.h.name).localeCompare(fundName(b.h.name)) : sort === "gain" ? (b.v.rate ?? -Infinity) - (a.v.rate ?? -Infinity) : b.v.value - a.v.value,
    );
  }, [holdings, views, sort]);
  return (
    <Card
      title={t("inv.holdings")}
      sub={when ? `${t("inv.holdings.sub", { n: rows.length })} · ${when}` : t("inv.holdings.sub", { n: rows.length })}
      right={
        rows.length > 3 && (
          <Dropdown<SortKey>
            label={t("tx.sort")}
            icon="sort"
            value={sort}
            onChange={setSort}
            options={[
              ["value", t("inv.sort.value")],
              ["gain", t("inv.sort.gain")],
              ["name", t("inv.sort.name")],
            ]}
          />
        )
      }
    >
      <div className="alloc" aria-hidden="true">
        {rows.map(({ h, v }) => (
          <span key={h.isin} style={{ flexGrow: v.share, background: colors.get(h.isin) }} title={fundName(h.name)} />
        ))}
      </div>
      <div className="holdgrid">
        {rows.map(({ h, v }, i) => (
          <HoldingCard key={h.isin} h={h} v={v} color={colors.get(h.isin) ?? "var(--accent)"} i={i} />
        ))}
      </div>
    </Card>
  );
}

// The depot's days, or its months for data from before daily values existed.
function depotDays(data: Inv): DayPoint[] {
  const daily = data.daily ?? [];
  return daily.length > 1 ? daily : data.series.map((p) => ({ date: p.month, value: p.value, paid_in: p.paid_in }));
}

// Each ETF from one day to another (indexes into the depot's days): its value at the end, what it
// earned in between and its line. null without the server's ETF-by-day values.
function useHoldingViews(data: Inv, all: DayPoint[], win: [number, number] | null): Map<string, HoldView> | null {
  const series = useMemo(() => {
    const hd = data.holding_daily;
    if (!hd || !data.daily || data.daily.length !== all.length) return null;
    const out = new Map<string, DayPoint[]>();
    for (const h of data.holdings) {
      const s = hd[h.isin];
      // The same ETF in two depots shares one line: those show since they were bought.
      if (!s || s.length !== all.length || out.has(h.isin)) return null;
      out.set(h.isin, all.map((d, i) => ({ date: d.date, value: s[i][0], paid_in: s[i][1] })));
    }
    return out;
  }, [data, all]);
  const w0 = win ? win[0] : -1, w1 = win ? win[1] : -1;
  return useMemo(() => {
    if (!series || w0 < 0 || w1 <= w0) return null;
    const views = new Map<string, HoldView>();
    let sum = 0;
    for (const [isin, days] of series) {
      const g = gainBetween(days, w0, w1);
      const value = days[w1].value;
      if (value < 0.5 && Math.abs(g.paid) < 0.5) continue;
      views.set(isin, { value, gain: g.gain, rate: g.rate, spark: thin(performance(days, w0, w1)), share: 0 });
      sum += value;
    }
    for (const v of views.values()) v.share = sum ? v.value / sum : 0;
    return views;
  }, [series, w0, w1]);
}

const dayName = (d: string) => (d.length === 7 ? monthLong(d) : dateShort(d));
const dayShort = (d: string) => (d.length === 7 ? monthLabel(d) : dayMonth(d));

// What a stretch of the depot's days is called: its month or year when it is exactly one (from the
// last day before it to its last day), otherwise its first and last day.
function stretchName(all: DayPoint[], w0: number, w1: number) {
  for (const len of [7, 4]) {
    const key = all[w1].date.slice(0, len);
    const exact = all[w0].date.slice(0, len) < key && all[w0 + 1]?.date.slice(0, len) === key && (w1 === all.length - 1 || all[w1 + 1].date.slice(0, len) !== key);
    if (exact) return len === 7 ? monthLong(key) : key;
  }
  return `${dayShort(all[w0].date)} – ${dayName(all[w1].date)}`;
}

// Whether the figures show the period (and zoom) or everything since the start: one click on the
// change under the depot value turns it over, and this browser keeps the choice.
const SINCE = "groschen.invSince";
function useSinceStart(): [boolean, () => void] {
  const [since, setSince] = useState(() => {
    try {
      return localStorage.getItem(SINCE) === "1";
    } catch {
      return false;
    }
  });
  const flip = () => {
    setSince(!since);
    try {
      if (since) localStorage.removeItem(SINCE);
      else localStorage.setItem(SINCE, "1");
    } catch {
      /* storage blocked: the choice lasts until the page is left */
    }
  };
  return [since, flip];
}

// The overview: the depot's value at the end of what the chart shows, what it earned over that time
// without counting the money paid in, the chart, and every ETF over the same time. All of it follows
// the period at the top and the chart's zoom.
function DepotOverview({ data }: { data: Inv }) {
  const t = useT();
  const { period } = useApp();
  const [since, flip] = useSinceStart();
  const all = useMemo(() => depotDays(data), [data]);
  const span = useMemo(() => periodSpan(all, period), [all, period]);
  const shown = useMemo(() => (span ? all.slice(span[0], span[1] + 1) : []), [all, span]);
  const dates = useMemo(() => shown.map((d) => d.date), [shown]);
  const zoom = useZoom("depot", `${period.preset}|${period.anchor ?? ""}`, dates);
  const win: [number, number] | null = span && shown.length > 1 ? [span[0] + zoom.to[0], span[0] + zoom.to[1]] : null;
  // The whole history unzoomed is the same as "since the start".
  const whole = period.preset === "all" && !zoom.zoomed;
  const windowed = !!win && win[1] > win[0] && !whole && !since;
  const atEnd = !win || win[1] >= all.length - 1;
  const value = windowed && !atEnd ? all[win[1]].value : data.value;
  const valueDate = windowed && !atEnd ? all[win[1]].date : data.price_date;
  const g = win && win[1] > win[0] ? gainBetween(all, win[0], win[1], atEnd ? data.value : undefined) : null;
  const when = !win ? null : zoom.zoomed ? stretchName(all, win[0], win[1]) : periodLabel(period);
  const views = useHoldingViews(data, all, windowed ? win : null);
  const gainShare = data.gain !== null && data.paid_in ? data.gain / data.paid_in : null;
  const allowanceShare = data.allowance.limit ? Math.min(data.allowance.used / data.allowance.limit, 1) : 0;
  const canFlip = !!win && win[1] > win[0] && !whole;

  let pill = null, line = "";
  if (windowed && g) {
    pill = <ChangePill up={g.gain >= 0} good={g.gain >= 0} text={`${eur(Math.abs(g.gain))} · ${pctS(g.rate)}`} onFlip={flip} title={t("inv.flip.start")} />;
    const paid = g.paid > 0.5 ? t("inv.win.paid", { amount: eur(g.paid) }) : g.paid < -0.5 ? t("inv.win.out", { amount: eur(-g.paid) }) : t("inv.win.none");
    line = `${when}, ${paid}`;
  } else {
    if (data.gain !== null)
      pill = <ChangePill up={data.gain >= 0} good={data.gain >= 0} text={`${eur(Math.abs(data.gain))} · ${pctS(gainShare)}`} onFlip={canFlip ? flip : undefined} title={canFlip ? t("inv.flip.window", { when: when ?? "" }) : undefined} />;
    line = canFlip ? `${t("inv.sinceStart")}, ${t("inv.paidInLine", { amount: eur(data.paid_in) })}` : t("inv.paidInLine", { amount: eur(data.paid_in) });
  }

  return (
    <>
      <section className="card invhero">
        <div className="hero-body">
          <div className="eyebrow">{valueDate ? t("inv.valueOn", { date: dayName(valueDate) }) : t("inv.value")}</div>
          <div className="hero-v">
            <Odometer value={value} />
          </div>
          <p className="hero-sub">
            {pill}
            <span>{line}</span>
          </p>
          {data.monthly_plan ? <p className="hero-note">{t("inv.planPerMonth", { amount: eur(data.monthly_plan) })}</p> : null}
        </div>
        <div className="invchart">
          {shown.length > 1 ? (
            <DepotChart days={shown} zoom={zoom} />
          ) : all.length > 1 ? (
            <Empty title={t("period.noData")}>{t("period.noData.text")}</Empty>
          ) : (
            <Empty title={t("inv.onePoint")} icon="trend">
              {t("inv.onePoint.text")}
            </Empty>
          )}
        </div>
      </section>
      {data.days_recorded < 30 && data.series.length < 3 && (
        <div className="note">
          <Icon name="clock" size={16} />
          <span>
            <b>{t("inv.fillIn")}</b> {t("inv.fillIn.text")}
          </span>
        </div>
      )}
      <Holdings holdings={data.holdings} views={windowed ? views : null} when={windowed && views ? when : null} />
      {germanTax(getRegion().country) && (
      <div className="allowance">
        <span className="al-txt">
          <b>{t("inv.allowance", { year: data.allowance.year })}</b>
          <small>{t("inv.allowance.of", { used: eur(data.allowance.used), limit: eur(data.allowance.limit) })}</small>
        </span>
        <span className="meter" aria-hidden="true">
          <span className={allowanceShare > 0.9 ? "warn" : ""} style={{ ["--p" as string]: `${(allowanceShare * 100).toFixed(1)}%` }} />
        </span>
        <button className="linkbtn" onClick={() => navigate("/settings#depot")}>
          {t("inv.allowance.adjust")}
        </button>
      </div>
      )}
      {!data.online_prices && <OnlinePricesOffer compact />}
    </>
  );
}

// Online prices are off until the user turns them on; this says what that would send and does it in one click.
export function OnlinePricesOffer({ compact = false }: { compact?: boolean }) {
  const t = useT();
  const toast = useToast();
  const [busy, setBusy] = useState(false);
  async function turnOn() {
    setBusy(true);
    try {
      await api.patch("/settings", { online_prices: true });
      toast(t("inv.online.on"));
      // The first fetch runs in the background; reload once it had time to finish.
      setTimeout(() => window.dispatchEvent(new Event("groschen:synced")), 6000);
      setTimeout(() => window.dispatchEvent(new Event("groschen:synced")), 20000);
    } catch (e) {
      toast((e as Error).message);
    }
    setBusy(false);
  }
  return (
    <div className={`note online-offer${compact ? " compact" : ""}`}>
      <Icon name="globe" size={16} />
      <span>
        <b>{t("inv.online.title")}</b> {t("inv.online.text")}
      </span>
      <button className="btn sm" disabled={busy} onClick={turnOn}>
        {busy ? <Spinner /> : null}
        {t("inv.online.button")}
      </button>
    </div>
  );
}

// The depot's return over a period: per year once the period covers one, for the period as a whole
// before that. "You" counts when the money went in (money-weighted), "the funds" don't (time-weighted).
function periodReturns(all: DayPoint[], p: Period) {
  const span = periodSpan(all, p);
  if (!span || span[1] <= span[0]) return null;
  const [i0, i1] = span;
  const days = (timeOf(all[i1].date) - timeOf(all[i0].date)) / 864e5;
  const perf = performance(all, i0, i1);
  const twr = perf[perf.length - 1] - 1;
  if (days >= 360) return { you: xirrBetween(all, i0, i1), funds: Math.pow(1 + twr, 365 / days) - 1, perYear: true };
  return { you: gainBetween(all, i0, i1).rate, funds: twr, perYear: false };
}

// What the depot's figures mean, drawn instead of listed: your return against the funds', how
// much it swings, how far below its high it is, and every month. All for the period at the top.
function Analysis({ data }: { data: Inv }) {
  const t = useT();
  const { period } = useApp();
  const all = useMemo(() => depotDays(data), [data]);
  const s = data.stats;
  if (!s) {
    return (
      <Card>
        <Empty title={t("inv.onePoint")} icon="trend">
          {t("inv.onePoint.text")}
        </Empty>
      </Card>
    );
  }
  const whole = period.preset === "all";
  const when = periodLabel(period);
  const { start, end } = periodBounds(period);
  const months = whole ? s.returns : s.returns.filter((x) => x.month >= start.slice(0, 7) && x.month <= end.slice(0, 7));
  const first = data.series.find((p) => p.value > 0);
  const ret = whole ? null : periodReturns(all, period);
  // How much it swung needs three months of the period; before that it says so and shows the whole time.
  const own = whole ? null : monthlyReturns(months, s.risk_free);
  const swingOwn = !!own && own.volatility !== null;
  const ddShown = clipMonths(s.drawdown, period);
  const ddWorst = ddShown.reduce<{ month: string; dd: number } | null>((w, d) => (!w || d.dd < w.dd ? d : w), null);
  const nowDd = s.drawdown.length ? s.drawdown[s.drawdown.length - 1].dd : null;
  // The largest drop since the start, when the chosen period doesn't show it.
  const ddOutside = s.max_drawdown < 0 && !ddShown.some((d) => d.month === s.max_drawdown_month);
  return (
    <>
      <div className="an-grid">
        {whole ? (
          <ReturnCard you={data.xirr} funds={s.twr} since={first ? monthLabel(first.month) : null} />
        ) : (
          ret && <ReturnCard you={ret.you} funds={ret.funds} since={null} title={t(ret.perYear ? "an.ret" : "an.ret.period")} youSub={t("an.ret.youIn", { when })} />
        )}
        <SwingCard volatility={swingOwn ? own.volatility : s.volatility} sharpe={swingOwn ? own.sharpe : s.sharpe} note={whole ? undefined : swingOwn ? when : t("an.swing.whole")} />
      </div>
      {ddWorst && ddShown.length > 1 && (
        <Card title={t("inv.dd")} sub={`${t("inv.dd.sub")} · ${when}`} right={<HighTag dd={nowDd} />}>
          <div className="scroll">
            <DrawdownChart data={ddShown} worst={ddWorst} />
          </div>
          {ddOutside && <p className="an-foot">{t("an.ddFoot", { p: pctS(s.max_drawdown), month: monthLabel(s.max_drawdown_month) })}</p>}
        </Card>
      )}
      {months.length > 0 && (
        <Card
          title={t("inv.monthly")}
          sub={whole ? t("inv.monthly.sub") : `${t("inv.monthly.sub")} · ${when}`}
          right={<MonthsUp up={months.filter((x) => x.r > 0).length} all={months.length} />}
        >
          <div className="scroll">
            <Heatmap returns={months} mark={extremes(months)} />
          </div>
          <p className="an-foot">
            <i className="an-key" />
            {t("an.outlined")}
          </p>
        </Card>
      )}
    </>
  );
}

type Tab = "overview" | "forecast" | "analysis" | "payments";
const TABS: Tab[] = ["overview", "forecast", "analysis", "payments"];
const pathOf = (p: Tab) => (p === "overview" ? "/investments" : `/investments/${p}`);

// The depot on four pages, each in the sidebar under it: the overview (value, what it gained, the
// ETFs as cards), the forecast, the analysis with every figure, and the payments into it. Without
// the sidebar (a phone) a row of tabs at the top switches between them.
export default function Investments({ page }: { page: Tab }) {
  const t = useT();
  const { data, error, reload } = useApi<Inv>("/investments");
  // Links from before the pages had their own addresses ("/investments?tab=analysis").
  const asked = useSearch().get("tab") as Tab | null;
  useSyncEvents(reload);
  if (page === "overview" && asked && asked !== "overview" && TABS.includes(asked)) return <OldAddress to={pathOf(asked)} />;
  const tab = page;
  const crumbs =
    tab === "overview" ? (
      <button className="linkbtn plain" onClick={() => navigate("/networth")}>
        {t("nav.networth")}
      </button>
    ) : (
      <button className="linkbtn plain" onClick={() => navigate("/investments")}>
        {t("nav.investments")}
      </button>
    );
  const title = tab === "overview" ? t("nav.investments") : t(`inv.tab.${tab}`);

  if (!data) return <><PageHeader eyebrow={crumbs} title={title} period={tab === "overview" || tab === "analysis"} />{error ? <ErrorNote error={error} /> : <Loading />}</>;

  if (!data.accounts.length) {
    return (
      <>
        <PageHeader eyebrow={crumbs} title={t("nav.investments")} />
        <Card>
          <Empty title={t("inv.noDepot")} icon="etf">
            {t("inv.noDepot.text")}
          </Empty>
        </Card>
      </>
    );
  }

  return (
    <>
      <PageHeader eyebrow={crumbs} title={title} period={tab === "overview" || tab === "analysis"} />
      <div className="phone-only">
        <Tabs<Tab>
          label={t("inv.tabs")}
          ids="inv"
          value={tab}
          onChange={(v) => redirect(pathOf(v))}
          options={[
            ["overview", t("inv.tab.overview")],
            ["forecast", t("inv.tab.forecast")],
            ["analysis", t("inv.tab.analysis")],
            ["payments", t("inv.tab.payments")],
          ]}
        />
      </div>
      <div className="tabpanel" role="tabpanel" id={`inv-panel-${tab}`} aria-labelledby={`inv-tab-${tab}`} key={tab}>
        {tab === "overview" && <DepotOverview data={data} />}
        {tab === "forecast" && <Forecast start={data.value} paidIn={data.paid_in || null} investing={data.investing} inputs={data.forecast} />}
        {tab === "analysis" && <Analysis data={data} />}
        {tab === "payments" && (
          <>
            <InvestPayments />
            <div className="note">
              <Icon name="upload" size={16} />
              <span>{tr("set.priceHistory.sub")}</span>
              <PriceImport />
            </div>
          </>
        )}
      </div>
    </>
  );
}
