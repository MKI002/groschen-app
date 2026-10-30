import { useT } from "../i18n";
import { dateShort, eur, fundName, monthLong, monthShort, relDay } from "../lib/format";
import { navigate } from "../lib/router";
import type { Plan, Plans } from "../lib/types";
import { Icon } from "./Icons";
import { Card, Disclosure, useApi, useSyncEvents } from "./UI";

const ICON: Record<Plan["kind"], string> = { etf: "etf", roundup: "coin", savings: "vault" };

// The last twelve months as coins: gold where the plan paid in, an empty ring where it didn't, a dashed
// one for this month while its payment is still to come.
function CoinStreak({ p }: { p: Plan }) {
  const t = useT();
  const paid = new Map(p.months.map((m) => [m.month, m.amount]));
  const now = new Date();
  const months = Array.from({ length: 12 }, (_, i) => {
    const d = new Date(now.getFullYear(), now.getMonth() - 11 + i, 1);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  });
  const thisMonth = months[11];
  return (
    <span className="coins" role="img" aria-label={t("plans.streakLabel", { n: months.filter((m) => paid.has(m)).length })}>
      {months.map((m, i) => {
        const amount = paid.get(m);
        const state = amount ? "paid" : m === thisMonth && p.active ? "soon" : m < p.since ? "before" : "missed";
        return (
          <span
            key={m}
            className={`pcoin ${state}`}
            style={{ ["--i" as string]: i }}
            title={amount ? `${monthLong(m)}: ${eur(amount)}` : state === "soon" ? t("plans.soon", { when: relDay(p.next_date) }) : monthLong(m)}
          >
            {i % 3 === 0 && <small>{monthShort(m)}</small>}
          </span>
        );
      })}
    </span>
  );
}

function PlanCard({ p, i }: { p: Plan; i: number }) {
  const t = useT();
  const etf = p.kind === "etf" && p.isin;
  const last = p.changes[p.changes.length - 1];
  const body = (
    <>
      <span className="plan-top">
        <span className={`ibadge ${p.invested ? "accent" : "info"}`} style={{ width: 34, height: 34 }} aria-hidden="true">
          <Icon name={ICON[p.kind]} size={17} />
        </span>
        <span className="plan-name">
          <b>{p.kind === "etf" ? (p.name ? fundName(p.name) : t("plans.unnamed")) : p.kind === "roundup" ? t("plans.roundup") : p.name}</b>
          <small>{t(`plans.kind.${p.kind}`)}</small>
        </span>
        <span className={`plan-state${p.active ? " on" : ""}`}>{t(`plans.state.${p.state}`)}</span>
      </span>
      <span className="plan-amt">
        {p.kind === "roundup" ? "≈ " : ""}
        {eur(p.amount)}
        <small>{t("plans.perMonth")}</small>
      </span>
      <CoinStreak p={p} />
      <span className="plan-foot">
        <span>{t("plans.total", { amount: eur(p.total_all), date: monthLong(p.since) })}</span>
        {last && <span className="plan-change">{t("plans.changed", { from: eur(last.from), to: eur(last.to), month: monthShort(last.month) })}</span>}
        {!p.active && <span>{t("plans.lastOn", { date: dateShort(p.last_date) })}</span>}
      </span>
    </>
  );
  return etf ? (
    <button type="button" className="plan stagger" style={{ ["--i" as string]: i }} onClick={() => navigate(`/investments/etf/${p.isin}`)}>
      {body}
    </button>
  ) : (
    <div className="plan stagger" style={{ ["--i" as string]: i }}>
      {body}
    </div>
  );
}

// Savings plans Groschen found by itself: ETF plans, Kleingeld Plus and standing orders to savings.
// Nothing to set up: a plan shows up after its third payment, pauses when one is missed and moves
// to "Ended" once about three are missing. Its next payment brings it back.
export function PlansCard() {
  const t = useT();
  const { data, reload } = useApi<Plans>("/plans");
  useSyncEvents(reload);
  if (!data || (!data.items.length && !data.ended.length)) return null;
  return (
    <Card
      id="plans"
      className="plans"
      title={t("plans.title")}
      sub={t("plans.sub")}
      right={
        <span className="plans-sum">
          <b>{eur(data.monthly)}</b> {t("plans.perMonth")}
        </span>
      }
    >
      {data.items.length > 0 ? (
        <div className="plangrid">
          {data.items.map((p, i) => (
            <PlanCard key={p.key} p={p} i={i} />
          ))}
        </div>
      ) : (
        <p className="muted">{t("plans.noneRunning")}</p>
      )}
      {data.ended.length > 0 && (
        <Disclosure label={t("plans.ended", { n: data.ended.length })} openLabel={t("plans.endedHide")}>
          <div className="plangrid">
            {data.ended.map((p, i) => (
              <PlanCard key={p.key} p={p} i={i} />
            ))}
          </div>
        </Disclosure>
      )}
    </Card>
  );
}
