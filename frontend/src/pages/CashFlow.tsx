import { useEffect, useState } from "react";
import { MiniBars, Sankey } from "../components/Charts";
import { Money } from "../components/Motion";
import { Inbox, PaydayHero } from "../components/Planner";
import { SavedBar, SavedToModal, groupColor, groupName, savedGroups } from "../components/SavedTo";
import { FlowTimeline, type TimelinePick } from "../components/Timeline";
import { Card, Empty, ErrorNote, Loading, Ring, Seg, Spinner, Tile, useApi, useSyncEvents } from "../components/UI";
import { catName, locale, useT } from "../i18n";
import { qs } from "../lib/api";
import { periodBounds, periodQuery, useApp } from "../lib/app";
import { colorVar, eur, pct } from "../lib/format";
import { drillPath, navigate } from "../lib/router";
import type { Cashflow, SavedDest, Timeline } from "../lib/types";
import { PageHeader } from "./Shell";

type ChartView = "flow" | "timeline";
const VIEWS: ChartView[] = ["flow", "timeline"];

// The chart last picked stays picked on this browser.
function savedView(): ChartView {
  try {
    const v = localStorage.getItem("groschen.overviewChart") as ChartView | null;
    if (v && VIEWS.includes(v)) return v;
  } catch {
    /* private window or blocked storage */
  }
  return "flow";
}

// The start page, read top to bottom: what is free until payday and what deserves a look (both about
// today), then the chosen period in three numbers and where its money went. Breakdowns live on Spending.
export default function CashFlow() {
  const { period, setPeriod, badges } = useApp();
  const t = useT();
  const [view, setViewState] = useState<ChartView>(savedView);
  const setView = (v: ChartView) => {
    setViewState(v);
    try {
      localStorage.setItem("groschen.overviewChart", v);
    } catch {
      /* ignore */
    }
  };
  // Which destination the "where your savings went" window opens on; undefined while it is closed.
  const [savedOpen, setSavedOpen] = useState<SavedDest | null | undefined>(undefined);
  // A savings band clicked on the timeline opens that window once its month has loaded.
  const [savedFor, setSavedFor] = useState<{ month: string; focus: SavedDest } | null>(null);
  const { data, error, loading, reload } = useApi<Cashflow>(`/cashflow${qs(periodQuery(period))}`);
  const timeline = useApi<Timeline>(view === "timeline" ? "/cashflow/timeline" : null);
  useSyncEvents(reload);
  useSyncEvents(timeline.reload);
  useEffect(() => {
    if (savedFor && data && !loading && data.range.start.slice(0, 7) === savedFor.month && period.preset === "month") {
      setSavedOpen(savedFor.focus);
      setSavedFor(null);
    }
  }, [savedFor, data, loading, period.preset]);

  const today = new Date().toLocaleDateString(locale(), { weekday: "long", day: "numeric", month: "long" });
  const top = (
    <>
      <PageHeader eyebrow={today} title={t("nav.overview")} period />
      <div className="ov-top">
        <PaydayHero />
        <Inbox review={badges?.review ?? 0} insights={data?.insights ?? []} />
      </div>
    </>
  );
  if (!data) return <>{top}{error ? <ErrorNote error={error} /> : <Loading />}</>;

  const d = data;
  const bounds = periodBounds(period);
  const showMonth = (month: string) => setPeriod({ preset: "month", anchor: `${month}-01` });
  const pickOnTimeline = (month: string, pick: TimelinePick) => {
    showMonth(month);
    if (pick.kind === "saved") setSavedFor({ month, focus: pick.focus });
    else if (pick.kind === "group") navigate(drillPath({ group: pick.name }));
    else navigate(drillPath({ category: pick.id, income: true }));
  };
  const spendGroups = d.groups.filter((g) => g.amount > 0);
  const noData = d.transaction_count === 0;
  // A single month or the last 30 days have no monthly average and no months to compare: the tiles
  // count bookings instead, and their small bars go by week.
  const single = d.trend.unit === "week";
  const unit = d.trend.unit;
  const byLabel = unit === "week" ? t("cf.byWeek") : unit === "year" ? t("cf.byYear") : t("cf.byMonth");
  const rate = d.savings_rate;

  return (
    <>
      {top}
      <div className="sect">
        <span>{d.range.label}</span>
        {loading && <Spinner />}
      </div>
      {noData ? (
        <Card>
          <Empty title={t("cf.empty")} icon="calendar">
            {t("cf.empty.text")}
          </Empty>
        </Card>
      ) : (
        <>
          <div className="kpis">
            <Tile
              label={t("cf.income")}
              swatch="var(--good)"
              value={<Money value={d.income_total} />}
              detail={single ? t("cf.count", { n: d.income.length }) : t("cf.avg", { amount: eur(d.avg_income) })}
              aside={<MiniBars values={d.trend.points.map((p) => p.income)} color="var(--good)" label={byLabel} />}
            />
            <Tile
              label={t("cf.spending")}
              swatch="var(--spend)"
              value={<Money value={d.spending_total} />}
              detail={single ? t("cf.txCount", { n: d.transaction_count }) : t("cf.avg", { amount: eur(d.avg_spending) })}
              aside={<MiniBars values={d.trend.points.map((p) => p.spending)} color="var(--spend)" label={byLabel} />}
            />
            <Tile
              label={t("cf.saved")}
              swatch="var(--accent)"
              value={
                <span className={d.saved < 0 ? "neg" : ""}>
                  <Money value={d.saved} />
                </span>
              }
              detail={d.saved_to ? <SavedBar data={d.saved_to} onOpen={() => setSavedOpen(null)} /> : d.saved >= 0 ? t("cf.savedPos") : t("cf.savedNeg")}
              aside={
                rate !== null && (
                  <span className="rate" title={t("cf.rate")}>
                    <Ring value={rate} tone={rate < 0 ? "bad" : "accent"} label={pct(rate, 0)} size={58} />
                    <small>{t("cf.rate")}</small>
                  </span>
                )
              }
            />
          </div>
          <Card
            className="flowcard"
            title={t("cf.where")}
            sub={view === "flow" ? t("cf.flowHint") : t("tl.hint")}
            right={<Seg label={t("cf.chart")} value={view} onChange={setView} options={[["flow", t("cf.flow")], ["timeline", t("tl.view")]]} />}
          >
            {view === "timeline" ? (
              timeline.data ? (
                <FlowTimeline
                  data={timeline.data}
                  focus={bounds.end.slice(0, 7)}
                  follow={period.preset === "month"}
                  inPeriod={(m) => m >= bounds.start.slice(0, 7) && m <= bounds.end.slice(0, 7)}
                  onSettle={showMonth}
                  onMonth={showMonth}
                  onPick={pickOnTimeline}
                />
              ) : timeline.error ? (
                <ErrorNote error={timeline.error} />
              ) : (
                <Loading />
              )
            ) : (
              <div className="scroll">
                <Sankey
                  income={d.income.map((i) => ({ name: catName(i.name), key: i.name, amount: i.amount, color: "var(--good)" }))}
                  spending={spendGroups.map((g) => ({ name: catName(g.name), key: g.name, amount: g.amount, color: colorVar(g.color) }))}
                  saved={d.saved}
                  savedTo={
                    d.saved_to &&
                    savedGroups(d.saved_to).map((g) => ({
                      name: groupName(g.key, g.amount),
                      amount: g.amount,
                      color: groupColor[g.key],
                      onClick: () => setSavedOpen(g.focus),
                    }))
                  }
                  onPick={(side, name) =>
                    navigate(side === "spending" ? drillPath({ group: name }) : drillPath({ category: d.income.find((i) => i.name === name)?.id ?? null, income: true }))
                  }
                />
              </div>
            )}
          </Card>
        </>
      )}
      {d.saved_to && savedOpen !== undefined && (
        <SavedToModal data={d.saved_to} label={d.range.label} focus={savedOpen} onClose={() => setSavedOpen(undefined)} onChanged={reload} />
      )}
    </>
  );
}
