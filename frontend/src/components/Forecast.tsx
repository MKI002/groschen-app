import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { useT, type Key } from "../i18n";
import { eur0, monthLabel, monthShort, num, pct, pctS } from "../lib/format";
import type { ForecastInputs, Investing } from "../lib/types";
import { ForecastChart, milestones, project, type ProjectionPoint } from "./Charts";
import { useTween } from "./Motion";
import { Card, Seg } from "./UI";

// How far along its track a slider is, for the filled part of the track.
const fill = (v: number, min: number, max: number) => ({ ["--p" as string]: `${((v - min) / (max - min)) * 100}%` });
// The time spans to look at; the simulation always runs the longest one, so switching is instant.
const SPANS = ["1", "2", "3", "5", "10", "20", "30"];
const YEARS = 30;

const thisMonth = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
};
const addMonths = (ym: string, m: number) => {
  const k = Number(ym.slice(0, 4)) * 12 + Number(ym.slice(5, 7)) - 1 + m;
  return `${Math.floor(k / 12)}-${String((k % 12) + 1).padStart(2, "0")}`;
};

// A sum that glides to its new value, for numbers that follow the pointer.
function Amount({ value }: { value: number }) {
  return <span className="mono-num">{eur0(useTween(value, 320))}</span>;
}

// Where it could go. Everything comes from your data: the value today, what you pay in (and how
// that changed), and the return and swing of the ETF's own price history. The panel shows one
// moment: the end of the chosen span, or the month under the pointer.
export function Forecast({ start, paidIn, investing, inputs, title, sub }: {
  start: number;
  paidIn: number | null;
  investing: Investing | null;
  inputs: ForecastInputs;
  title?: string;
  sub?: string;
}) {
  const t = useT();
  const found = useMemo(
    () => ({
      monthly: Math.round(investing?.per_month ?? 0),
      ret: Math.round(inputs.ret * 1000) / 10,
      raise: Math.round((investing?.raise_pa ?? 0) * 1000) / 10,
    }),
    [investing?.per_month, investing?.raise_pa, inputs.ret],
  );
  const [monthly, setMonthly] = useState(found.monthly);
  const [ret, setRet] = useState(found.ret);
  const [raise, setRaise] = useState(found.raise);
  const [span, setSpan] = useState("10");
  const [pin, setPin] = useState<number | null>(null);
  const [hover, setHover] = useState<number | null>(null);
  const [adjust, setAdjust] = useState(false);
  // New data (another ETF, a sync) goes back to what was found.
  useEffect(() => {
    setMonthly(found.monthly);
    setRet(found.ret);
    setRaise(found.raise);
  }, [found]);
  const reset = () => {
    setMonthly(found.monthly);
    setRet(found.ret);
    setRaise(found.raise);
  };
  const vol = inputs.vol;
  const paid = paidIn && paidIn > 0 ? paidIn : start;
  const data = useMemo(() => project(start, monthly, YEARS, ret / 100, vol, raise / 100, paid), [start, monthly, ret, vol, raise, paid]);
  const marks = useMemo(() => milestones(data, start), [data, start]);
  const months = Number(span) * 12;
  const view = useTween(months, 550);
  const at = Math.min(hover ?? pin ?? months, months);
  const p = data[at];
  const first = thisMonth();
  const changed = monthly !== found.monthly || ret !== found.ret || raise !== found.raise;
  const touch = typeof matchMedia !== "undefined" && matchMedia("(hover: none)").matches;

  const pickSpan = (v: string) => {
    setSpan(v);
    setPin(null);
  };
  const goTo = (m: number) => {
    if (m > months) setSpan(SPANS.find((s) => Number(s) * 12 >= m) ?? "30");
    setPin(m);
  };

  // Amounts to try, straight from your payments: what the forecast uses, this month's, the last six months'.
  const presets: { label: string; amount: number }[] = [];
  const offer = (label: string, amount: number) => {
    const a = Math.round(amount);
    if (presets.some((q) => Math.abs(q.amount - a) <= Math.max(5, 0.1 * Math.max(q.amount, a)))) return;
    presets.push({ label, amount: a });
  };
  offer(investing?.source === "plan" ? t("fc.p.plan") : t("fc.p.avg12", { n: investing?.window_months ?? 12 }), found.monthly);
  if (investing?.this_month) offer(t("fc.p.thisMonth"), investing.this_month);
  if (investing?.recent !== undefined) offer(t("fc.p.recent"), investing.recent);

  const steps = investing?.steps ?? [];
  const planWhy = !investing
    ? t("fc.noPlan")
    : investing.source === "plan"
      ? t(`fc.from.${investing.rhythm}` as Key, { n: investing.count, since: monthLabel(investing.first.slice(0, 7)), day: investing.day })
      : investing.source === "average"
        ? t("fc.from.average", { total: eur0(investing.window_total ?? 0), n: investing.window_count ?? investing.count, months: investing.window_months ?? 12 })
        : t("fc.from.once", { since: monthLabel(investing.first.slice(0, 7)) });
  const raiseWhy =
    found.raise > 0 && steps.length > 1
      ? t("fc.raise.steps", { from: eur0(steps[0].amount), to: eur0(steps[steps.length - 1].amount), since: monthLabel(steps[0].from) })
      : investing?.source === "average"
        ? t("fc.raise.irregular")
        : steps.length > 1 && steps[steps.length - 1].amount > steps[0].amount
          ? t("fc.raise.recent", { from: eur0(steps[0].amount), to: eur0(steps[steps.length - 1].amount), since: monthLabel(steps[0].from) })
          : investing?.source === "plan"
            ? t("fc.raise.same")
            : "–";
  const facts: { key: string; label: string; value: string; why: (string | null)[] }[] = [
    { key: "plan", label: t("fc.f.plan"), value: found.monthly ? t("fc.perMonth", { amount: eur0(found.monthly) }) : t("fc.none"), why: [planWhy] },
    { key: "raise", label: t("fc.f.raise"), value: found.raise ? t("fc.perYear", { p: pct(found.raise / 100, 1) }) : t("fc.flat"), why: [raiseWhy] },
    {
      key: "return",
      label: t("fc.f.return"),
      value: t("fc.perYear", { p: pct(found.ret / 100, 1) }),
      why: [
        inputs.hist !== undefined && inputs.hist !== null && inputs.years >= 1
          ? t("fc.return.hist", { hist: pctS(inputs.hist), years: num(inputs.years, 1), weight: pct(inputs.weight ?? 0, 0), prior: pct(inputs.prior, 0) })
          : t("fc.return.prior", { prior: pct(inputs.prior, 0) }),
      ],
    },
    { key: "swing", label: t("fc.f.swing"), value: t("fc.perYear", { p: pct(vol, 0) }), why: [inputs.vol_known ? t("fc.swing.hist") : t("fc.swing.default")] },
  ];

  const when = addMonths(first, at);
  const whenText =
    at === 0
      ? t("fc.today")
      : at % 12 === 0
        ? t(at === 12 ? "fc.t.year" : "fc.t.years", { n: at / 12 })
        : at < 12
          ? t(at === 1 ? "fc.inMonth" : "fc.inMonths", { n: at })
          : t("fc.t.years", { n: num(at / 12, 1) });
  const gain = p.p50 - p.paid;
  const risk = at === 0 ? null : p.below < 0.02 ? t("fc.hardly") : p.below <= 0.5 ? t("fc.oneIn", { n: Math.max(2, Math.round(1 / p.below)) }) : t("fc.share", { p: pct(p.below, 0) });

  return (
    <Card
      title={title ?? t("inv.proj")}
      sub={sub ?? t("inv.proj.sub")}
      className="fc"
      right={
        <div className="legend">
          <span>
            <span className="sq dash" style={{ background: "var(--accent)" }} />
            {t("inv.middle")}
          </span>
          <span>
            <span className="sq" style={{ background: "var(--accent)", opacity: 0.3 }} />
            {t("inv.eightOfTen")}
          </span>
          <span>
            <span className="sq" style={{ background: "var(--muted)", opacity: 0.45 }} />
            {t("inv.paidIn")}
          </span>
        </div>
      }
    >
      <div className="fc-facts" role="group" aria-label={t("fc.why")}>
        {facts.map((f) => (
          <div key={f.key} className="fc-fact">
            <small>{f.label}</small>
            <b>{f.value}</b>
            <span className="fc-src">{f.why.filter(Boolean).join(". ")}</span>
          </div>
        ))}
      </div>

      <div className="fc-main">
        <div className="fc-hero">
          <div className="fc-when">
            {whenText}
            <span> · {`${monthShort(when)} ${when.slice(0, 4)}`}</span>
          </div>
          <div className="fc-big">
            <Amount value={p.p50} />
          </div>
          <RangeBar p={p} />
          {at > 0 && <p className={`fc-verdict ${gain >= 0 ? "pos" : "neg"}`}>{t(gain >= 0 ? "fc.more" : "fc.less", { amount: eur0(Math.abs(gain)), paid: eur0(p.paid) })}</p>}
          {risk && <p className="fc-risk">{risk}</p>}
        </div>

        <div className="fc-more">
          {presets.length > 1 && (
            <div className="fc-row">
              <span>{t("fc.pay")}</span>
              {presets.map((q) => (
                <button key={q.label} type="button" className={`fc-chip${monthly === q.amount ? " on" : ""}`} aria-pressed={monthly === q.amount} onClick={() => setMonthly(q.amount)}>
                  <small>{q.label}</small> {eur0(q.amount)}
                </button>
              ))}
            </div>
          )}
          {marks.length > 0 && (
            <div className="fc-row">
              <span>{t("fc.milestones")}</span>
              {marks.map((s) => (
                <button key={s.value} type="button" className={`fc-chip${pin === s.m ? " on" : ""}`} onClick={() => goTo(s.m)}>
                  {t("fc.ms", { amount: eur0(s.value), year: addMonths(first, s.m).slice(0, 4) })}
                </button>
              ))}
            </div>
          )}
          <div className="fc-tools">
            <button className="linkbtn" aria-expanded={adjust} onClick={() => setAdjust(!adjust)}>
              {adjust ? t("fc.adjust.close") : t("fc.adjust")}
            </button>
            {changed && (
              <button className="linkbtn" onClick={reset}>
                {t("fc.reset")}
              </button>
            )}
          </div>
        </div>

        <div className="fc-chartcol">
          <div className="fc-bar">
            <span className="fc-hint">{touch ? t("fc.hintTouch") : t("fc.hint")}</span>
            <Seg value={span} options={SPANS.map((s) => [s, t("fc.span", { n: s })] as [string, string])} onChange={pickSpan} label={t("fc.spanLabel")} />
          </div>
          <ForecastChart data={data} span={view} at={at} first={first} milestones={marks} onHover={setHover} onPin={(m) => setPin(pin === m ? null : m)} />
        </div>
      </div>

      {adjust && (
        <div className="sliders fc-sliders">
          <label>
            <span>
              {t("inv.planSlider")} <b>{eur0(monthly)}</b>
            </span>
            <input type="range" style={fill(monthly, 0, 2000)} min={0} max={2000} step={5} value={monthly} onChange={(e) => setMonthly(Number(e.target.value))} />
          </label>
          <label>
            <span>
              {t("fc.raise")} <b>{pct(raise / 100, 1)}</b>
            </span>
            <input type="range" style={fill(raise, 0, 10)} min={0} max={10} step={0.5} value={raise} onChange={(e) => setRaise(Number(e.target.value))} />
          </label>
          <label>
            <span>
              {t("inv.expected")} <b>{pct(ret / 100, 1)}</b>
            </span>
            <input type="range" style={fill(ret, -2, 12)} min={-2} max={12} step={0.1} value={ret} onChange={(e) => setRet(Number(e.target.value))} />
          </label>
        </div>
      )}
    </Card>
  );
}

// One moment on a line: the range 8 in 10 futures end in, red where it's below what you paid in and
// green above, the paid-in mark, and the middle outcome as the dot.
function RangeBar({ p }: { p: ProjectionPoint }) {
  const t = useT();
  const lo = Math.min(p.p10, p.paid), hi = Math.max(p.p90, p.paid);
  const pad = (hi - lo) * 0.06 || Math.max(1, hi * 0.02);
  const a = lo - pad, b = hi + pad;
  const x = (v: number) => ((v - a) / (b - a)) * 100;
  const cut = Math.min(Math.max(p.paid, p.p10), p.p90);
  const style = {
    "--lo": `${x(p.p10)}%`,
    "--cut": `${x(cut)}%`,
    "--hi": `${x(p.p90)}%`,
    "--paid": `${x(p.paid)}%`,
    "--mid": `${x(p.p50)}%`,
  } as CSSProperties;
  return (
    <div className="fc-range" style={style} role="img" aria-label={t("fc.likely", { lo: eur0(p.p10), hi: eur0(p.p90) })}>
      <div className="fc-track">
        <span className="loss" />
        <span className="gain" />
        <span className="paid">
          <i>{t("fc.chart.paid")}</i>
        </span>
        <span className="mid" />
      </div>
      <div className="fc-ends">
        <span>
          <small>{t("fc.t.bad")}</small>
          <b>{eur0(p.p10)}</b>
        </span>
        <span className="r">
          <small>{t("fc.t.good")}</small>
          <b>{eur0(p.p90)}</b>
        </span>
      </div>
    </div>
  );
}
