import { useMemo, useState } from "react";
import { t as tr, useT } from "../i18n";
import { api } from "../lib/api";
import { dayMonth, eur, monthLong, veil } from "../lib/format";
import type { InvestPayment } from "../lib/types";
import { Icon } from "./Icons";
import { Card, Empty, ErrorNote, Loading, useApi, useSyncEvents, useToast } from "./UI";

const SHOWN_MONTHS = 6;

type Month = { month: string; items: InvestPayment[]; total: number };

// Every payment the Investments page counts, grouped by month. Groschen adds them on its own
// (the Investments category plus bookings that read like an ETF buy or a broker transfer);
// one click takes a payment out when it belongs to something outside this depot, another puts it back.
export function InvestPayments() {
  const t = useT();
  const toast = useToast();
  const { data, error, reload } = useApi<{ payments: InvestPayment[] }>("/investments/payments");
  useSyncEvents(reload);
  const [flipped, setFlipped] = useState<Record<number, boolean>>({});
  const [busy, setBusy] = useState<number | null>(null);
  const [open, setOpen] = useState<Record<string, boolean>>({});
  const [all, setAll] = useState(false);

  const payments = useMemo(
    () => (data?.payments ?? []).map((p) => (p.id in flipped ? { ...p, counted: flipped[p.id] } : p)),
    [data, flipped],
  );
  const months = useMemo(() => {
    const out: Month[] = [];
    for (const p of payments) {
      const m = p.date.slice(0, 7);
      let last = out[out.length - 1];
      if (!last || last.month !== m) out.push((last = { month: m, items: [], total: 0 }));
      last.items.push(p);
      if (p.counted) last.total += p.amount;
    }
    return out;
  }, [payments]);

  if (!data) return <Card title={t("inv.pay.title")}>{error ? <ErrorNote error={error} /> : <Loading />}</Card>;

  const detected = payments.filter((p) => p.how === "detected" && p.counted).length;
  const yearAgo = new Date();
  yearAgo.setFullYear(yearAgo.getFullYear() - 1);
  const since = yearAgo.toISOString().slice(0, 10);
  const lastYear = payments.filter((p) => p.counted && p.date >= since).reduce((s, p) => s + p.amount, 0);
  const shown = all ? months : months.slice(0, SHOWN_MONTHS);

  async function toggle(p: InvestPayment) {
    const counted = !p.counted;
    setBusy(p.id);
    setFlipped((f) => ({ ...f, [p.id]: counted }));
    try {
      await api.put(`/investments/payments/${p.id}`, { counted });
      toast(counted ? tr("inv.pay.backIn") : tr("inv.pay.out"));
      // Paid in, the savings plan and the forecast all follow the payments: fetch the page again.
      window.dispatchEvent(new Event("groschen:synced"));
    } catch (e) {
      setFlipped((f) => ({ ...f, [p.id]: p.counted }));
      toast((e as Error).message);
    }
    setBusy(null);
  }

  return (
    <Card
      title={t("inv.pay.title")}
      sub={t("inv.pay.sub")}
      right={payments.length ? <b>{t("inv.pay.year", { amount: eur(lastYear) })}</b> : undefined}
    >
      {!payments.length ? (
        <Empty title={t("inv.pay.none")}>{t("inv.pay.none.text")}</Empty>
      ) : (
        <>
          {detected > 0 && (
            <p className="ipay-note">
              <Icon name="spark" size={15} />
              {t(detected === 1 ? "inv.pay.found1" : "inv.pay.found", { n: detected })}
            </p>
          )}
          <div className="ipay">
            {shown.map((m, i) => {
              const isOpen = open[m.month] ?? i === 0;
              return (
                <section key={m.month} className={`ipay-month${isOpen ? " open" : ""}`}>
                  <button type="button" className="ipay-head" aria-expanded={isOpen} onClick={() => setOpen((o) => ({ ...o, [m.month]: !isOpen }))}>
                    <span className="chev" aria-hidden="true">›</span>
                    <span className="ipay-m">{monthLong(m.month)}</span>
                    <span className="ipay-n muted">{t(m.items.length === 1 ? "inv.pay.count1" : "inv.pay.count", { n: m.items.length })}</span>
                    <span className="ipay-total">{eur(m.total)}</span>
                  </button>
                  {isOpen && (
                    <ul className="ipay-list">
                      {m.items.map((p) => (
                        <li key={p.id} className={p.counted ? "" : "off"}>
                          <span className="ipay-date">{dayMonth(p.date)}</span>
                          <span className="ipay-what">
                            <span className="ipay-name">
                              <span className="ipay-nm">{p.name}</span>
                              {p.how === "detected" && (
                                <span className="tag found" title={t("inv.pay.found.title")}>
                                  {t("inv.pay.foundTag")}
                                </span>
                              )}
                            </span>
                            {p.purpose && <span className="ipay-purpose muted">{veil(p.purpose)}</span>}
                          </span>
                          <span className="ipay-amt">{eur(p.amount)}</span>
                          <button
                            type="button"
                            className={`btn sm ipay-btn${p.counted ? " ghost" : ""}`}
                            disabled={busy === p.id}
                            onClick={() => toggle(p)}
                            title={p.counted ? t("inv.pay.skip.title") : undefined}
                          >
                            <Icon name={p.counted ? "x" : "rewind"} size={14} />
                            {p.counted ? t("inv.pay.skip") : t("inv.pay.undo")}
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </section>
              );
            })}
          </div>
          {months.length > SHOWN_MONTHS && (
            <button type="button" className="linkbtn ipay-more" onClick={() => setAll(!all)}>
              {all ? t("inv.pay.fewer") : t("inv.pay.all", { n: months.length })}
            </button>
          )}
        </>
      )}
    </Card>
  );
}
