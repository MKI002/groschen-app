import { useEffect, useState } from "react";
import { AmountBars, LineChart } from "../components/Charts";
import { openDialog } from "../components/Dialogs";
import { FilterBar, filterQuery, useTxFilters } from "../components/Filters";
import { Icon } from "../components/Icons";
import { Odometer } from "../components/Motion";
import { TxList } from "../components/TxList";
import { BarRow, Card, ChangePill, Empty, ErrorNote, Loading, Seg, Spinner, useApi, useSyncEvents } from "../components/UI";
import { qs } from "../lib/api";
import { periodQuery, useApp } from "../lib/app";
import { colorVar, dateShort, eur, monthLabel, monthShort, pct } from "../lib/format";
import { drillPath, navigate } from "../lib/router";
import { catName, locale, t, useT } from "../i18n";
import type { Drilldown as Data, Tx } from "../lib/types";
import { PageHeader } from "./Shell";
import { EditTx, useTxSaved } from "./Transactions";

const PAGE = 100;
// 1 January 2024 was a Monday, so day 0 is Monday like the server counts.
const weekday = (day: number) => new Date(2024, 0, 1 + day).toLocaleDateString(locale(), { weekday: "short" });
type Chart = "month" | "weekday" | "total";

// One page for everything you can click into: a category group, a category, a payee or one of
// your own groups. The total with its course on top, who and what it was, then every booking.
export default function Drilldown({ group, category, merchant, custom }: { group?: string; category?: number; merchant?: string; custom?: number }) {
  const { period, refresh, groups } = useApp();
  useT();
  const flow = new URLSearchParams(location.search).get("flow") ?? undefined;
  const f = useTxFilters();
  const [sub, setSub] = useState<Set<number | null>>(new Set());
  const [chart, setChart] = useState<Chart>("month");
  const [limit, setLimit] = useState(PAGE);
  const [editing, setEditing] = useState<Tx | null>(null);
  const fq = filterQuery(f);
  const subKey = [...sub].map((s) => (s === null ? "none" : s)).join(",");
  useEffect(() => setLimit(PAGE), [fq.q, fq.account_id, fq.min, fq.max, fq.sort, fq.dir, subKey]);

  const path = `/drilldown${qs({
    group, category_id: category, merchant, custom, flow, ...periodQuery(period), ...fq, sub: subKey, limit,
  })}`;
  const { data, error, loading, reload } = useApi<Data>(path);
  useSyncEvents(reload);
  const saved = useTxSaved(() => setEditing(null), reload, refresh);

  const own = custom !== undefined ? groups.find((g) => g.id === custom) : undefined;
  const title =
    (data?.scope.kind === "merchant" || data?.scope.kind === "custom" ? data.scope.name : catName(data?.scope.name ?? group)) ||
    own?.name ||
    merchant ||
    t("dd.category");
  const income = data?.scope.direction === "income";
  const home = custom !== undefined ? t("nav.groups") : income ? t("cf.income") : t("nav.spending");
  const crumbs = (
    <span className="crumbs">
      <button className="linkbtn plain" onClick={() => navigate(custom === undefined && income ? "/spending?flow=income" : "/spending")}>
        {home}
      </button>
      {data?.scope.kind === "category" && data.scope.group !== data.scope.name && catName(data.scope.group) !== home && (
        <>
          <Icon name="chevRight" size={12} />
          <button className="linkbtn plain" onClick={() => navigate(drillPath({ group: data.scope.group }))}>
            {catName(data.scope.group)}
          </button>
        </>
      )}
    </span>
  );
  const editGroup = own && (
    <button className="btn sm ghost" onClick={() => openDialog({ kind: "group", group: own })}>
      <Icon name="pencil" size={14} /> {t("group.edit")}
    </button>
  );
  if (!data) {
    return (
      <>
        <PageHeader eyebrow={crumbs} title={title} period actions={editGroup} />
        {error ? <ErrorNote error={error} /> : <Loading />}
      </>
    );
  }

  const s = data.summary;
  const color = colorVar(data.scope.color);
  const isPayee = data.scope.kind === "merchant";
  // A group, or a payee booked under more than one category, gets the category breakdown and chips.
  const isGroup = data.scope.kind !== "category" && data.categories.length > 1;
  // Who it went to, unless it all went to one (the bookings below say that already).
  const showMerchants = !isPayee && data.merchant_count > 1;
  const allTime = data.all_time;
  let running = 0;
  const cumulative = (allTime?.monthly ?? []).map((m) => ({ month: m.month, value: (running += m.amount) }));
  const filtered = f.filtered || sub.size > 0;
  const change = s.previous && s.previous.total ? s.total / s.previous.total - 1 : null;
  const catBase = Math.max(...data.categories.map((c) => c.amount), 1);
  const merchBase = Math.max(...data.merchants.map((m) => m.amount), 1);
  const bars =
    chart === "weekday"
      ? data.weekday.map((w) => ({
          key: String(w.day),
          label: weekday(w.day),
          value: w.amount,
          title: t("dd.barTitle", { label: weekday(w.day), amount: eur(w.amount), n: w.count }),
        }))
      : data.monthly.map((m) => ({
          key: m.month,
          label: data.monthly.length > 12 ? monthLabel(m.month) : monthShort(m.month),
          value: m.amount,
          title: t("dd.barTitle", { label: monthLabel(m.month), amount: eur(m.amount), n: m.count }),
        }));
  const charts: [Chart, string][] = [
    ["month", t("dd.months")],
    ["weekday", t("dd.weekdays")],
    ...(isPayee && cumulative.length > 1 ? [["total", t("dd.sinceStart")] as [Chart, string]] : []),
  ];

  function toggleSub(id: number | null) {
    setSub((cur) => {
      const next = new Set(cur);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }
  function reset() {
    f.reset();
    setSub(new Set());
  }

  return (
    <>
      <PageHeader eyebrow={crumbs} title={title} period actions={editGroup} />
      <section className="card ddhero" style={{ ["--c" as string]: color }}>
        <div className="hero-body">
          <div className="eyebrow">{income ? t("dd.received") : t("group.spent")}</div>
          <div className="hero-v">
            <Odometer value={s.total} />
          </div>
          <p className="hero-sub">
            {change !== null && Math.abs(change) >= 0.005 && (
              <ChangePill
                up={change > 0}
                good={(change > 0) === income}
                text={pct(Math.abs(change), 0)}
                title={s.previous ? t("dd.sameBefore", { start: dateShort(s.previous.start), end: dateShort(s.previous.end) }) + ` ${eur(s.previous.total)}` : undefined}
              />
            )}{" "}
            {change !== null && <span>{t("dd.vsBefore")}</span>}
          </p>
          <div className="facts">
            {s.months > 1 && (
              <span>
                <b>{eur(s.per_month)}</b> {t("sp.perMonth")}
              </span>
            )}
            <span>
              <b>{s.count}</b> {t("dd.bookings", { n: s.count })}
            </span>
            {s.largest && (
              <span>
                {t("dd.largestWas")} <b>{eur(s.largest.value)}</b>
              </span>
            )}
          </div>
          {allTime && <p className="hero-note">{t("dd.allTimeLine", { amount: eur(allTime.total), n: allTime.count, date: dateShort(allTime.first) })}</p>}
          {s.review > 0 && (
            <button className="linkbtn" onClick={() => navigate(`/transactions?filter=review&q=${encodeURIComponent(isPayee ? title : "")}`)}>
              {t("dd.review", { n: s.review })}
              <Icon name="chevRight" size={13} />
            </button>
          )}
        </div>
        <div className="ddchart">
          <div className="invchart-h">
            <span className="eyebrow">{chart === "weekday" ? t("dd.byWeekday") : chart === "total" ? t("dd.spentSoFar") : t("group.perMonth")}</span>
            <Seg<Chart> label={t("dd.chart")} value={chart} onChange={setChart} options={charts} />
          </div>
          {chart === "total" ? (
            <LineChart data={cumulative} color={color} label={t("dd.runningLabel", { name: title })} />
          ) : s.count ? (
            <AmountBars key={`${chart}-${path}`} data={bars} color={color} label={t(chart === "month" ? "dd.chartLabelMonth" : "dd.chartLabelWeekday", { name: title })} />
          ) : (
            <Empty title={t("dd.nothingToChart")}>{t("dd.nothingToChart.text")}</Empty>
          )}
        </div>
      </section>

      {(showMerchants || isGroup) && (
        <div className={showMerchants && isGroup ? "grid2" : "stack"}>
          {showMerchants && (
            <Card title={t("dd.topMerchants")} sub={data.merchant_count > data.merchants.length ? t("dd.nOfM", { n: data.merchants.length, m: data.merchant_count }) : undefined}>
              <div className="bars">
                {data.merchants.map((m) => (
                  <BarRow
                    key={m.name}
                    name={m.name}
                    sub={`${m.count}×`}
                    value={m.amount}
                    base={merchBase}
                    color={color}
                    share={m.amount > 0 ? m.share : undefined}
                    onClick={() => navigate(drillPath({ merchant: m.name }))}
                  />
                ))}
              </div>
            </Card>
          )}
          {isGroup && (
            <Card title={t("sp.cats")}>
              <div className="bars">
                {data.categories.map((c) => (
                  <BarRow
                    key={c.id ?? "none"}
                    name={c.id === null ? t("tx.uncategorized") : catName(c.name)}
                    sub={`${c.count}×`}
                    value={c.amount}
                    base={catBase}
                    color={colorVar(c.color)}
                    share={s.total && c.amount > 0 && !sub.size ? c.amount / s.total : undefined}
                    onClick={() => navigate(drillPath({ category: c.id, income }))}
                  />
                ))}
              </div>
            </Card>
          )}
        </div>
      )}

      <Card title={t("nav.transactions")} className="txcard">
        <FilterBar f={f} placeholder={t("dd.search")} />
        {isGroup && (
          <div className="chips" role="group" aria-label={t("sp.cats")}>
            <button className={`chip ${sub.size === 0 ? "on" : ""}`} aria-pressed={sub.size === 0} onClick={() => setSub(new Set())}>
              {t("tx.all")}
            </button>
            {data.categories.map((c) => (
              <button key={c.id ?? "none"} className={`chip ${sub.has(c.id) ? "on" : ""}`} aria-pressed={sub.has(c.id)} onClick={() => toggleSub(c.id)}>
                <span className="sq" style={{ background: colorVar(c.color) }} /> {c.id === null ? t("tx.uncategorized") : catName(c.name)} <span className="n">{c.count}</span>
              </button>
            ))}
          </div>
        )}
        <div className="txsum">
          <span>{t("dd.txCount", { n: data.total })}</span>
          {filtered && (
            <button className="linkbtn" onClick={reset}>
              {t("dd.clearFilters")}
            </button>
          )}
          {loading && <Spinner />}
        </div>
        <ErrorNote error={error} />
        {data.items.length ? (
          <TxList items={data.items} byDay={f.sort === "date"} onOpen={setEditing} />
        ) : (
          <Empty title={t("tx.noMatch")} icon="search">
            {filtered ? t("tx.noMatch.text") : t("dd.nothingInPeriod")}
          </Empty>
        )}
        {data.items.length < data.total && (
          <div className="pager">
            <button className="btn sm" onClick={() => setLimit((l) => l + PAGE)} disabled={loading}>
              {t("tx.more", { left: (data.total - data.items.length).toLocaleString(locale()) })}
            </button>
          </div>
        )}
      </Card>
      {editing && <EditTx tx={editing} onClose={() => setEditing(null)} onSaved={saved} />}
    </>
  );
}
