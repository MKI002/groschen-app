import { useMemo, useState } from "react";
import { Sunburst, YearHeatmap, type SunGroup } from "../components/Charts";
import { openDialog } from "../components/Dialogs";
import { Icon } from "../components/Icons";
import { BarRow, Card, Empty, ErrorNote, Loading, Seg, useApi, useSyncEvents } from "../components/UI";
import { catName, locale, useT } from "../i18n";
import { qs } from "../lib/api";
import { periodQuery, useApp } from "../lib/app";
import { colorVar, eur, int, pct } from "../lib/format";
import { drillPath, navigate, redirect, useSearch } from "../lib/router";
import type { Cashflow } from "../lib/types";
import { SpendSwitch } from "./Recurring";
import { PageHeader } from "./Shell";

type Daily = { year: number; first: string | null; last: string | null; days: { date: string; amount: number; count: number }[] };

// Every day of one year, with the year's few numbers underneath. A click opens that day's transactions.
function YearCard() {
  const t = useT();
  const now = new Date().getFullYear();
  const [year, setYear] = useState(now);
  const { data, reload } = useApi<Daily>(`/daily${qs({ year })}`);
  useSyncEvents(reload);
  const firstYear = data?.first ? Number(data.first.slice(0, 4)) : now;
  const stats = useMemo(() => {
    if (!data || data.year !== year) return null;
    const today = new Date().toISOString().slice(0, 10);
    const from = data.first && data.first > `${year}-01-01` ? data.first : `${year}-01-01`;
    const to = today < `${year}-12-31` ? today : `${year}-12-31`;
    const span = Math.max(0, Math.round((Date.parse(to) - Date.parse(from)) / 86400000) + 1);
    const spent = data.days.filter((d) => d.amount > 0);
    const top = spent.reduce<(typeof spent)[number] | null>((a, d) => (!a || d.amount > a.amount ? d : a), null);
    return { free: Math.max(0, span - spent.length), top, avg: spent.length ? spent.reduce((a, d) => a + d.amount, 0) / spent.length : 0 };
  }, [data, year]);
  return (
    <Card
      title={t("yh.title")}
      sub={t("yh.sub")}
      right={
        <div className="period steps">
          <button className="ib" aria-label={t("yh.prev")} disabled={year <= firstYear} onClick={() => setYear(year - 1)}>
            <Icon name="chevRight" size={15} className="flip" />
          </button>
          <span className="period-y">{year}</span>
          <button className="ib" aria-label={t("yh.next")} disabled={year >= now} onClick={() => setYear(year + 1)}>
            <Icon name="chevRight" size={15} />
          </button>
        </div>
      }
    >
      {data && data.year === year ? (
        <>
          <YearHeatmap year={year} days={data.days} onPick={(d) => navigate(`/transactions?from=${d}&to=${d}`)} />
          <div className="yh-foot">
            {stats && (
              <span className="facts">
                <span>
                  <b>{int(stats.free)}</b> {t("yh.free")}
                </span>
                {stats.top && (
                  <button className="linkbtn plain" onClick={() => navigate(`/transactions?from=${stats.top!.date}&to=${stats.top!.date}`)}>
                    <b>{eur(stats.top.amount)}</b> {t("yh.top", { date: new Date(`${stats.top.date}T12:00:00`).toLocaleDateString(locale(), { day: "numeric", month: "short" }) })}
                  </button>
                )}
                <span>
                  <b>{eur(stats.avg)}</b> {t("yh.avg")}
                </span>
              </span>
            )}
            <span className="legend">
              <span className="yh-key l0" />
              {t("yh.none")}
              <span className="yh-gap" />
              {t("yh.less")}
              {[1, 2, 3, 4, 5].map((l) => (
                <span key={l} className={`yh-key l${l}`} />
              ))}
              {t("yh.more")}
            </span>
          </div>
        </>
      ) : (
        <Loading />
      )}
    </Card>
  );
}

// Your own groups (say "Kinder" or "Urlaub"), as chips above the breakdown, plus the way to make one.
function GroupChips() {
  const t = useT();
  const { groups } = useApp();
  return (
    <div className="chips grouprow" role="group" aria-label={t("nav.groups")}>
      {groups.map((g) => (
        <button key={g.id} className="chip" onClick={() => navigate(`/groups/${g.id}`)}>
          <Icon name={g.icon} size={14} />
          {g.name}
        </button>
      ))}
      <button className="chip add" onClick={() => openDialog({ kind: "group", group: null })}>
        <Icon name="plus" size={14} />
        {t("group.new")}
      </button>
    </div>
  );
}

// Where the money goes (and where it comes from): the sunburst and a ranked list side by side,
// your own groups above them and every day of the year below.
export default function Spending() {
  const { period } = useApp();
  const t = useT();
  const income = useSearch().get("flow") === "income";
  const [mode, setMode] = useState<"groups" | "cats">("groups");
  const [zoom, setZoom] = useState<string | null>(null);
  const { data, error, reload } = useApi<Cashflow>(`/cashflow${qs(periodQuery(period))}`);
  useSyncEvents(reload);
  const flowSeg = (
    <Seg<"out" | "in">
      label={t("sp.flow")}
      value={income ? "in" : "out"}
      onChange={(v) => {
        setZoom(null);
        redirect(v === "in" ? "/spending?flow=income" : "/spending");
      }}
      options={[
        ["out", t("cf.spending")],
        ["in", t("cf.income")],
      ]}
    />
  );
  const header = (
    <>
      <PageHeader title={t("nav.spending")} period actions={flowSeg} />
      <SpendSwitch />
    </>
  );
  const sun = useMemo<SunGroup[]>(() => {
    if (!data) return [];
    if (income) return data.income.filter((i) => i.amount > 0).map((i) => ({ key: String(i.id ?? i.name), name: catName(i.name), color: "var(--good)", amount: i.amount, children: [] }));
    return data.groups
      .filter((g) => g.amount > 0)
      .map((g) => ({
        key: g.name,
        name: catName(g.name),
        color: colorVar(g.color),
        amount: g.amount,
        children: data.categories
          .filter((c) => c.group === g.name && c.amount > 0)
          .map((c) => ({ id: c.id, key: String(c.id ?? c.name), name: catName(c.name), color: colorVar(c.color), amount: c.amount })),
      }));
  }, [data, income]);

  if (!data) return <>{header}{error ? <ErrorNote error={error} /> : <Loading />}</>;

  const total = (income ? data.income_total : data.spending_total) || 1;
  const zg = zoom ? sun.find((g) => g.key === zoom) : null;
  type Row = { key: string; name: string; sub: string; amount: number; color: string; to: string };
  const rows: Row[] = income
    ? data.income.map((i) => ({ key: i.name, name: catName(i.name), sub: "", amount: i.amount, color: "var(--good)", to: drillPath({ category: i.id, income: true }) }))
    : zg
      ? zg.children.map((c) => ({ key: c.key, name: c.name, sub: "", amount: c.amount, color: c.color, to: drillPath({ category: c.id }) }))
      : mode === "groups"
        ? // Groups where refunds outweighed spending (a tax refund, say) have no slice but still get a row.
          data.groups.map((g) => ({ key: g.name, name: catName(g.name), sub: g.amount < 0 ? t("cf.refunds") : "", amount: g.amount, color: colorVar(g.color), to: drillPath({ group: g.name }) }))
        : data.categories
            .filter((c) => c.amount > 0)
            .slice(0, 15)
            .map((c) => ({ key: `${c.id}`, name: catName(c.name), sub: c.name === c.group ? "" : catName(c.group), amount: c.amount, color: colorVar(c.color), to: drillPath({ category: c.id }) }));
  const base = Math.max(...rows.map((r) => r.amount), 1);
  const largest = income ? data.income[0] : data.groups.find((g) => g.amount > 0);
  const listTotal = zg ? zg.amount : total;
  const avg = income ? data.avg_income : data.avg_spending;

  return (
    <>
      {header}
      {!income && <GroupChips />}
      <Card
        className="spendcard"
        title={income ? t("sp.incomeBreakdown") : zg ? zg.name : t("sp.breakdown")}
        sub={
          zg ? (
            t("sb.zoomedHint")
          ) : (
            <span className="facts inline">
              {data.months > 1 && (
                <span>
                  <b>{eur(avg)}</b> {t("sp.perMonth")}
                </span>
              )}
              {largest && (
                <span>
                  {t(income ? "sp.mostFrom" : "sp.mostOn")} <b>{catName(largest.name)}</b> ({pct(largest.amount / total, 0)})
                </span>
              )}
            </span>
          )
        }
        right={
          !income &&
          (zg ? (
            <button className="btn sm" onClick={() => setZoom(null)}>
              <Icon name="chevRight" size={14} className="flip" />
              {t("sb.back")}
            </button>
          ) : (
            <Seg label={t("sp.breakdown")} value={mode} onChange={setMode} options={[["groups", t("sp.groups")], ["cats", t("sp.cats")]]} />
          ))
        }
      >
        {sun.length === 0 ? (
          <Empty title={income ? t("cf.noIncome") : t("sp.empty")} icon="pie" />
        ) : (
          <div className="donutwrap">
            <Sunburst
              groups={sun}
              zoom={zoom}
              zoomable={!income}
              onZoom={setZoom}
              label={t("sp.donutTotal")}
              shown={income ? data.income_total : data.spending_total}
              onPickGroup={(key) => {
                if (income) {
                  const i = data.income.find((x) => String(x.id ?? x.name) === key);
                  navigate(drillPath({ category: i?.id ?? null, income: true }));
                } else navigate(drillPath({ group: key }));
              }}
              onPickCategory={(_, id) => navigate(drillPath({ category: id }))}
            />
            <div className="bars">
              {rows.map((r) => (
                <BarRow key={r.key} name={r.name} sub={r.sub} value={r.amount} base={base} color={r.color} share={r.amount > 0 ? r.amount / listTotal : undefined} onClick={() => navigate(r.to)} />
              ))}
              {zg && (
                <button className="linkbtn" onClick={() => navigate(drillPath({ group: zg.key }))}>
                  {t("sb.openGroup", { name: zg.name })}
                  <Icon name="chevRight" size={13} />
                </button>
              )}
            </div>
          </div>
        )}
      </Card>
      {!income && <YearCard />}
    </>
  );
}
