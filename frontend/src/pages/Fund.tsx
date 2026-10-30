import { useMemo, useState } from "react";
import { extremes, MonthsUp, PeriodBars, RangeCard, ReturnCard, RollingCard, SwingCard } from "../components/Analysis";
import { AmountBars, DrawdownChart, Heatmap, PriceChart } from "../components/Charts";
import { Forecast } from "../components/Forecast";
import { PayoutTag, payoutText } from "../components/Payout";
import { Icon } from "../components/Icons";
import { Odometer } from "../components/Motion";
import { Card, ChangePill, Empty, ErrorNote, Loading, Seg, Spinner, Tabs, useApi, useSyncEvents, useToast } from "../components/UI";
import { useZoom } from "../components/Zoom";
import { t as tr, useT, type Key } from "../i18n";
import { api } from "../lib/api";
import { dateShort, eur, eur0, figure, fundName, monthLabel, monthShort, num, pct, pctS, relTime } from "../lib/format";
import { navigate, redirect, useSearch } from "../lib/router";
import type { Fund as FundData } from "../lib/types";
import { OnlinePricesOffer } from "./Investments";
import { PageHeader } from "./Shell";

type Range = "1m" | "3m" | "6m" | "1y" | "3y" | "5y" | "max";
const RANGE_MONTHS: Record<Range, number> = { "1m": 1, "3m": 3, "6m": 6, "1y": 12, "3y": 36, "5y": 60, max: 0 };

// The chosen range is kept for every ETF in this browser.
const RANGE_KEY = "groschen.fundRange";
function loadRange(): Range {
  try {
    const v = localStorage.getItem(RANGE_KEY) as Range | null;
    if (v && v in RANGE_MONTHS) return v;
  } catch {
    /* storage blocked: the default */
  }
  return "1y";
}

function cutoff(last: string, months: number) {
  const d = new Date(`${last}T12:00:00`);
  d.setMonth(d.getMonth() - months);
  return d.toISOString().slice(0, 10);
}

function RefreshPrices() {
  const t = useT();
  const toast = useToast();
  const [busy, setBusy] = useState(false);
  async function go() {
    setBusy(true);
    try {
      await api.post("/market/refresh");
      setTimeout(() => window.dispatchEvent(new Event("groschen:synced")), 5000);
      toast(t("fund.refreshing"));
    } catch (e) {
      toast((e as Error).message);
    }
    setTimeout(() => setBusy(false), 5000);
  }
  return (
    <button className="btn sm ghost" onClick={go} disabled={busy}>
      {busy ? <Spinner /> : <Icon name="refresh" size={15} />}
      {t("fund.refresh")}
    </button>
  );
}

function YearBars({ years }: { years: FundData["years"] }) {
  const max = Math.max(0.05, ...years.map((y) => Math.abs(y.r)));
  return (
    <div className="yearbars">
      {years.map((y, i) => (
        <div key={y.year} className="yb stagger" style={{ ["--i" as string]: i }} title={`${y.year}: ${pctS(y.r)}`}>
          <span className="yb-year">
            {y.year}
            {y.partial && <small>*</small>}
          </span>
          <span className="yb-track">
            <span className={`yb-bar ${y.r >= 0 ? "up" : "down"}`} style={{ width: `${(Math.abs(y.r) / max) * 50}%` }} />
          </span>
          <b className={y.r >= 0 ? "pos" : "neg"}>{pctS(y.r)}</b>
        </div>
      ))}
    </div>
  );
}

// What kind of fund it is: pays out or reinvests (and how often), costs, size and make-up,
// and the payouts that actually reached your accounts.
function FactsCard({ data }: { data: FundData }) {
  const t = useT();
  const f = data.facts;
  const pay = data.payout;
  const pos = data.position;
  const policyText = pay.policy ? payoutText(t, pay.policy, pay.frequency) : t("pay.unknown");
  const from = pay.source ? t(`pay.src.${pay.source}` as Key) : "";
  const rows: [string, string, string?][] = [];
  if (f?.ter !== undefined) rows.push([t("facts.ter"), `${pct(f.ter, 2)} ${t("fund.pa")}`, pos?.cost_pa ? t("facts.ter.you", { amount: eur(pos.cost_pa) }) : undefined]);
  if (f?.size !== undefined) rows.push([t("facts.size"), `${f.size_currency ?? "EUR"} ${f.size >= 1000 ? `${num(f.size / 1000, 1)} ${t("facts.bn")}` : `${num(f.size, 0)} ${t("facts.m")}`}`, f.size < 100 ? t("facts.size.small") : undefined]);
  if (f?.replication) rows.push([t("facts.replication"), t(`facts.rep.${f.replication}` as Key), f.replication_detail]);
  if (f?.currency) rows.push([t("facts.currency"), f.currency, f.hedged === undefined ? undefined : f.hedged ? t("facts.hedged") : t("facts.unhedged")]);
  if (f?.index) rows.push([t("facts.index"), f.index]);
  if (f?.domicile) rows.push([t("facts.domicile"), f.domicile]);
  if (f?.inception) rows.push([t("facts.inception"), dateShort(f.inception)]);
  return (
    <Card title={t("facts.title")} sub={f?.fetched_at ? t("facts.sub", { when: relTime(f.fetched_at) }) : t("facts.subOffline")}>
      <div className="inv-facts">
        <div className={`payout-fact ${pay.policy ?? ""}`}>
          <small>{t("facts.payout")}</small>
          <b>{policyText}</b>
          <span className="muted small">
            {pay.policy === "accumulating" ? t("pay.acc.d") : pay.policy === "distributing" ? t("pay.dist.d") : t("pay.unknown.d")}
            {from ? ` ${from}` : ""}
          </span>
        </div>
        {pay.policy === "distributing" && (
          <div>
            <small>{t("facts.received")}</small>
            <b>{eur(pay.received_12m)}</b>
            <span className="muted small">
              {pay.count_12m ? t("facts.received.d", { n: pay.count_12m, p: pay.yield_12m !== null ? pct(pay.yield_12m, 2) : "–" }) : t("facts.received.none")}
              {pay.dividend_yield != null ? ` ${t("facts.yieldNow", { p: pct(pay.dividend_yield, 2) })}` : ""}
            </span>
          </div>
        )}
        {rows.map(([label, value, detail]) => (
          <div key={label}>
            <small>{label}</small>
            <b>{value}</b>
            {detail && <span className="muted small">{detail}</span>}
          </div>
        ))}
      </div>
      {pay.policy === "distributing" && <p className="txsum">{t("facts.priceOnly")}</p>}
      {pay.received.length > 0 && (
        <div className="chips">
          {pay.received
            .slice(-8)
            .reverse()
            .map((p) => (
              <span key={p.date + p.amount} className="chip static">
                {dateShort(p.date)} · <b className="pos">+{eur(p.amount)}</b>
              </span>
            ))}
        </div>
      )}
    </Card>
  );
}

// How the ETF did and what that means, drawn instead of listed: the price change over each period,
// your return against the fund's, where the price stands in its year, how much it swings, how
// often twelve months ended higher, how you invested, and every year, month and drop.
function Analysis({ data }: { data: FundData }) {
  const t = useT();
  const rk = data.risk;
  const inv = data.investing;
  const ddWorst = rk?.drawdown.length ? rk.drawdown.reduce((a, b) => (b.dd < a.dd ? b : a)) : null;
  const avgEffect = inv?.avg_buy && inv.avg_market ? inv.avg_buy / inv.avg_market - 1 : null;
  if (!rk && !inv && !data.years.length && !data.periods.length) {
    return (
      <Card>
        <Empty title={t("fund.noHistory")} icon="trend">
          {data.online_enabled ? t("fund.noHistory.on") : t("fund.noHistory.off")}
        </Empty>
      </Card>
    );
  }
  const since = inv?.first ?? data.position?.since ?? null;
  return (
    <>
      {data.periods.length > 0 && (
        <Card title={t("an.perf")} sub={data.last_date ? t("an.perf.sub", { date: dateShort(data.last_date) }) : undefined}>
          <PeriodBars periods={data.periods} />
        </Card>
      )}
      {(rk || inv?.xirr != null) && (
        <div className="an-grid">
          <ReturnCard you={inv?.xirr} funds={inv?.fund_pa} since={since ? monthLabel(since.slice(0, 7)) : null} one />
          {rk && <RangeCard low={rk.low_52w} high={rk.high_52w} price={data.last_price} avg200={rk.ma200} dd={rk.current_drawdown} ath={rk.ath} athDate={rk.ath_date} />}
          {rk && <SwingCard volatility={rk.volatility} sharpe={rk.sharpe} />}
          {rk && <RollingCard rolling={rk.rolling ?? []} up={rk.rolling_up} />}
        </div>
      )}
      {inv && (
        <Card title={t("fund.inv")} sub={inv.estimated ? t("fund.inv.estimated") : t("fund.inv.sub")}>
          <div className="an-facts">
            <div>
              <small>{t("fund.inv.rhythm")}</small>
              <b>{t(`fund.rhythm.${inv.rhythm}` as Key, { day: inv.day })}</b>
            </div>
            <div>
              <small>{t("fund.inv.usual")}</small>
              <b>{eur0(inv.typical)}</b>
            </div>
            <div>
              <small>{t("fund.inv.total")}</small>
              <b>{eur0(inv.total)}</b>
              <span>{t("fund.inv.count", { n: inv.count, since: monthLabel(inv.first.slice(0, 7)) })}</span>
            </div>
            <div>
              <small>{t("fund.inv.avg")}</small>
              <b>{inv.avg_buy ? eur(inv.avg_buy) : "–"}</b>
              {avgEffect !== null && <span className={avgEffect <= 0 ? "pos" : ""}>{t(avgEffect <= 0 ? "fund.inv.cheaper" : "fund.inv.dearer", { p: pct(Math.abs(avgEffect), 1) })}</span>}
            </div>
          </div>
          {inv.steps.length > 1 && (
            <p className="txsum">
              {t("fund.inv.steps")}{" "}
              {inv.steps.map((s, i) => (
                <span key={s.from}>
                  {i ? " → " : ""}
                  <b>{eur0(s.amount)}</b> {t("fund.inv.from", { month: `${monthShort(s.from)} ${s.from.slice(0, 4)}` })}
                </span>
              ))}
            </p>
          )}
          {inv.monthly.length > 1 && (
            <div className="scroll">
              <AmountBars
                data={inv.monthly.map((m) => ({ key: m.month, label: monthLabel(m.month), value: m.amount, title: `${monthLabel(m.month)}: ${eur(m.amount)}` }))}
                color="var(--accent)"
                label={t("fund.inv")}
                avgLabel={t("fund.inv.avgBar")}
              />
            </div>
          )}
        </Card>
      )}
      {data.years.length > 0 && (
        <Card title={t("fund.years")} sub={t("fund.years.sub")}>
          <YearBars years={data.years} />
        </Card>
      )}
      {rk && rk.monthly.length > 2 && (
        <Card title={t("inv.monthly")} sub={t("fund.monthly.sub")} right={<MonthsUp up={rk.months_up} all={rk.months} />}>
          <div className="scroll">
            <Heatmap returns={rk.monthly} mark={extremes(rk.monthly)} />
          </div>
          <p className="an-foot">
            <i className="an-key" />
            {t("an.outlined")}
          </p>
        </Card>
      )}
      {rk && ddWorst && rk.drawdown.length > 2 && (
        <Card title={t("inv.dd")} sub={t("fund.dd.sub")}>
          <div className="scroll">
            <DrawdownChart data={rk.drawdown} worst={ddWorst} />
          </div>
          {/* With daily prices the deepest fall can lie between two month ends, below the chart's lowest point. */}
          {data.daily && rk.max_drawdown < ddWorst.dd - 0.005 && (
            <p className="an-foot">
              {t("an.ddFund", {
                p: pctS(rk.max_drawdown),
                span: t(rk.recovered ? "fund.dd.back" : "fund.dd.notBack", { from: dateShort(rk.max_drawdown_from), to: dateShort(rk.max_drawdown_to), back: dateShort(rk.recovered) }),
              })}
            </p>
          )}
        </Card>
      )}
    </>
  );
}

type Tab = "overview" | "analysis" | "forecast" | "facts";
const TABS: Tab[] = ["overview", "analysis", "forecast", "facts"];

// One ETF: your part of it and its price at a glance; the analysis, a forecast for your position and
// the fund's facts each behind their own tab.
export default function Fund({ isin }: { isin: string }) {
  const t = useT();
  const { data, error, reload } = useApi<FundData>(`/investments/${encodeURIComponent(isin)}`, [isin]);
  useSyncEvents(reload);
  const [range, setRangeState] = useState<Range>(loadRange);
  const setRange = (r: Range) => {
    setRangeState(r);
    try {
      localStorage.setItem(RANGE_KEY, r);
    } catch {
      /* storage blocked: the range lasts until the page is left */
    }
  };
  const asked = useSearch().get("tab") as Tab | null;
  const tab: Tab = asked && TABS.includes(asked) ? asked : "overview";

  const crumbs = (
    <button className="linkbtn plain" onClick={() => navigate("/investments")}>
      {t("nav.investments")}
    </button>
  );

  const ranges = useMemo(() => {
    if (!data?.first_date || !data.last_date) return [] as Range[];
    const all = Object.keys(RANGE_MONTHS) as Range[];
    return all.filter((r) => r === "max" || cutoff(data.last_date!, RANGE_MONTHS[r]) >= data.first_date!.slice(0, 10) || r === "1m");
  }, [data?.first_date, data?.last_date]);
  const shownRange: Range = ranges.includes(range) ? range : ranges[ranges.length - 1] ?? "max";
  const shown = useMemo(() => {
    if (!data?.prices.length || !data.last_date) return [];
    if (shownRange === "max") return data.prices;
    const from = cutoff(data.last_date, RANGE_MONTHS[shownRange]);
    const pts = data.prices.filter((p) => p.d >= from);
    return pts.length > 1 ? pts : data.prices.slice(-2);
  }, [data, shownRange]);
  // The chart zooms in time: each point sits at its day, counted from the first one.
  const dates = useMemo(() => shown.map((p) => p.d), [shown]);
  const days = useMemo(() => shown.map((p) => (Date.parse(p.d) - Date.parse(shown[0].d)) / 864e5), [shown]);
  const zoom = useZoom(`price:${isin}`, shownRange, dates, days, 5);

  if (!data) {
    return (
      <>
        <PageHeader eyebrow={crumbs} title={isin} />
        {error ? <ErrorNote error={error} /> : <Loading />}
      </>
    );
  }

  const pos = data.position;
  const inv = data.investing;
  const change = shown.length > 1 && zoom.to[1] > zoom.to[0] ? shown[zoom.to[1]].p / shown[zoom.to[0]].p - 1 : null;
  const gainPct = pos?.gain != null && pos.cost ? pos.gain / pos.cost : null;

  return (
    <>
      <PageHeader eyebrow={crumbs} title={fundName(data.name)} actions={data.online_enabled ? <RefreshPrices /> : undefined} />
      <div className="fund-meta">
        <span className="muted">{data.name}</span>
        <span className="chip static isin">{data.isin}</span>
        <PayoutTag policy={data.payout.policy} frequency={data.payout.frequency} />
      </div>
      <Tabs<Tab>
        label={t("fund.tabs")}
        ids="fund"
        value={tab}
        onChange={(v) => redirect(v === "overview" ? `/investments/etf/${data.isin}` : `/investments/etf/${data.isin}?tab=${v}`)}
        options={[
          ["overview", t("inv.tab.overview")],
          ["analysis", t("inv.tab.analysis")],
          ["forecast", t("inv.tab.forecast")],
          ["facts", t("fund.tab.facts")],
        ]}
      />
      <div className="tabpanel" role="tabpanel" id={`fund-panel-${tab}`} aria-labelledby={`fund-tab-${tab}`} key={tab}>
        {tab === "overview" && (
          <>
            {!data.online_enabled && <OnlinePricesOffer compact />}
            {data.online_enabled && data.source.error && (
              <div className="note warn">
                <Icon name="warn" size={16} />
                <span>{t("fund.sourceError", { error: data.source.error })}</span>
              </div>
            )}
            <section className="card invhero">
              {pos && (
                <div className="hero-body">
                  <div className="eyebrow">{t("fund.yourValue")}</div>
                  <div className="hero-v">
                    <Odometer value={pos.value} />
                  </div>
                  <p className="hero-sub">
                    {pos.gain !== null && <ChangePill up={pos.gain >= 0} good={pos.gain >= 0} text={`${eur(Math.abs(pos.gain))} · ${pctS(gainPct)}`} />}{" "}
                    <span>{t("fund.ofDepot", { p: pct(pos.share, 0) })}</span>
                  </p>
                  <p className="hero-note">
                    {t("fund.unitsLine", { n: figure(pos.pieces, 3), price: eur(pos.price) })}
                    {pos.avg_price ? ` · ${t("fund.avgLine", { price: eur(pos.avg_price) })}` : ""}
                  </p>
                  {inv && <p className="hero-note">{t(`fund.rhythm.${inv.rhythm}` as Key, { day: inv.day })} · {eur0(inv.typical)}</p>}
                </div>
              )}
              <div className="invchart">
                <div className="invchart-h">
                  <span className="eyebrow">
                    {t("fund.price")}
                    {change !== null && <b className={change >= 0 ? "pos" : "neg"}> {pctS(change)}</b>}
                  </span>
                  {ranges.length > 1 && <Seg<Range> value={shownRange} onChange={setRange} label={t("fund.range")} options={ranges.map((r) => [r, t(`fund.p.${r}` as Key)])} />}
                </div>
                {shown.length > 1 ? (
                  <PriceChart data={shown} buys={inv?.purchases ?? []} avg={pos?.avg_price ?? null} label={t("fund.price")} zoom={zoom} />
                ) : (
                  <Empty title={t("fund.noHistory")}>{data.online_enabled ? t("fund.noHistory.on") : t("fund.noHistory.off")}</Empty>
                )}
              </div>
            </section>
            <p className="txsum">
              {data.last_date && t("fund.price.sub", { date: dateShort(data.last_date), source: data.source.online ? t("fund.src.online") : t("fund.src.bank") })}
            </p>
          </>
        )}
        {tab === "analysis" && <Analysis data={data} />}
        {tab === "forecast" &&
          (pos ? (
            <Forecast start={pos.value} paidIn={pos.cost} investing={inv} inputs={data.forecast} title={t("fund.fc")} sub={t("fund.fc.sub")} />
          ) : (
            <Card>
              <Empty title={t("fund.noPosition")} icon="trend" />
            </Card>
          ))}
        {tab === "facts" && (
          <>
            <FactsCard data={data} />
            <p className="txsum">
              {t("fund.foot")}
              {data.source.fetched_at ? ` ${tr("fund.fetched", { when: relTime(data.source.fetched_at) })}` : ""}
            </p>
          </>
        )}
      </div>
    </>
  );
}
