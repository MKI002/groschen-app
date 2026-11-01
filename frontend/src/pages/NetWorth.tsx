import { useEffect, useState } from "react";
import { LineChart } from "../components/Charts";
import { Icon } from "../components/Icons";
import { Odometer } from "../components/Motion";
import { PlansCard } from "../components/Plans";
import { ChangePill, Empty, ErrorNote, Loading, Modal, Seg, Spinner, useApi, useConfirm, useSyncEvents, useToast } from "../components/UI";
import { getLang, t, useT } from "../i18n";
import { api } from "../lib/api";
import { dateShort, eur, money, monthLong, pct } from "../lib/format";
import { clipMonths, useApp } from "../lib/app";
import { navigate } from "../lib/router";
import type { NetWorth as NW } from "../lib/types";
import { PageHeader, periodLabel } from "./Shell";

type Account = NW["accounts"][number];

function ManualAccount({ account, onClose, onSaved }: { account: Account | null; onClose: () => void; onSaved: () => void }) {
  useT();
  const de = getLang() === "de";
  const [name, setName] = useState(account?.name ?? "");
  const [kind, setKind] = useState(account?.kind ?? "manual_asset");
  const [balance, setBalance] = useState(account ? String(Math.abs(account.balance ?? 0)).replace(".", de ? "," : ".") : "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { confirm, dialog } = useConfirm();
  // German input uses 1.234,56, English 1,234.56.
  const value = Number(de ? balance.replace(/\./g, "").replace(",", ".") : balance.replace(/,/g, ""));

  async function save() {
    setBusy(true);
    try {
      if (account) await api.put(`/accounts/${account.id}/balance`, { balance: value });
      else await api.post("/accounts/manual", { name, kind, balance: value });
      onSaved();
    } catch (e) {
      setError((e as Error).message);
      setBusy(false);
    }
  }

  async function remove() {
    if (!account) return;
    const ok = await confirm({ title: t("nw.removeTitle", { name: account.name }), text: t("nw.confirmRemove", { name: account.name }), action: t("nw.remove") });
    if (!ok) return;
    await api.del(`/accounts/${account.id}`);
    onSaved();
  }

  return (
    <>
      <Modal
        title={account ? t("nw.updateName", { name: account.name }) : t("nw.addTitle")}
        onClose={onClose}
        actions={
          <>
            {account && (
              <button className="btn ghost danger" onClick={remove}>
                {t("nw.remove")}
              </button>
            )}
            <span className="grow" />
            <button className="btn ghost" onClick={onClose}>
              {t("common.cancel")}
            </button>
            <button className="btn primary" onClick={save} disabled={busy || !isFinite(value) || (!account && !name.trim())}>
              {busy && <Spinner />}
              {t("common.save")}
            </button>
          </>
        }
      >
        {!account && (
          <>
            <p className="muted small">{t("nw.manualHint")}</p>
            <div className="field">
              <label htmlFor="ma-name">{t("nw.name")}</label>
              <input className="input" id="ma-name" value={name} onChange={(e) => setName(e.target.value)} placeholder={t("nw.carLoan")} />
            </div>
            <div className="field">
              <span className="label">{t("nw.type")}</span>
              <Seg
                label={t("nw.type")}
                value={kind}
                onChange={setKind}
                options={[
                  ["manual_asset", t("nw.own")],
                  ["manual_liability", t("nw.owe")],
                ]}
              />
            </div>
          </>
        )}
        <div className="field">
          <label htmlFor="ma-bal">{kind === "manual_liability" ? t("nw.owed") : t("nw.value")}</label>
          <input className="input money-in" id="ma-bal" inputMode="decimal" value={balance} onChange={(e) => setBalance(e.target.value)} />
        </div>
        {error && <p className="err">{error}</p>}
      </Modal>
      {dialog}
    </>
  );
}

const KIND_ICON: Record<string, string> = { checking: "bank", savings: "vault", depot: "etf", manual_asset: "wallet", manual_liability: "warn" };

// One account as a tile: what it is, where its number comes from, the balance and its share of
// everything you own. The depot opens the Investments page; accounts kept by hand open for editing.
function AccountTile({ a, total, i, onEdit }: { a: Account; total: number; i: number; onEdit: () => void }) {
  useT();
  const depot = a.kind === "depot";
  const share = a.side === "asset" && total > 0 && a.counted !== 0 ? Math.max(0, (a.balance ?? 0) / total) : null;
  const open = depot ? () => navigate("/investments") : a.manual === 1 ? onEdit : undefined;
  const body = (
    <>
      <span className="nwacct-top">
        <span className={`ibadge ${a.side === "liability" ? "bad" : depot ? "accent" : "muted"}`} style={{ width: 34, height: 34 }} aria-hidden="true">
          <Icon name={KIND_ICON[a.kind] ?? "wallet"} size={17} />
        </span>
        <span className="nwacct-name">
          <b>{a.name}</b>
          <small>
            {a.source}
            {a.balance_date ? ` · ${dateShort(a.balance_date)}` : ""}
          </small>
        </span>
        {open && <Icon name={depot ? "chevRight" : "pencil"} size={15} className="nwacct-go" />}
      </span>
      <span className={`nwacct-v${a.side === "liability" ? " neg" : ""}`}>
        {a.counted === 0 && a.currency ? money(a.orig_balance ?? a.balance, a.currency) : eur(a.side === "liability" ? -Math.abs(a.balance ?? 0) : a.balance)}
        {a.orig_balance != null && a.currency && <small className="orig">{a.counted === 0 ? t("fx.notCounted") : money(a.orig_balance, a.currency)}</small>}
      </span>
      {share !== null && (
        <span className="nwacct-share">
          <span className="meter" aria-hidden="true">
            <span style={{ ["--p" as string]: `${(share * 100).toFixed(1)}%` }} />
          </span>
          <small>{pct(share, 0)}</small>
        </span>
      )}
    </>
  );
  return open ? (
    <button type="button" className="nwacct stagger" style={{ ["--i" as string]: i }} onClick={open} aria-label={depot ? t("nw.openDepot") : t("nw.updateName", { name: a.name })}>
      {body}
    </button>
  ) : (
    <div className="nwacct stagger" style={{ ["--i" as string]: i }}>
      {body}
    </div>
  );
}

// What you own: one number with its course over the chosen period, every account as a tile, and the
// savings plans that keep it growing.
export default function NetWorth() {
  const toast = useToast();
  useT();
  const { data, error, reload } = useApi<NW>("/networth");
  const { period } = useApp();
  const [editing, setEditing] = useState<Account | null | "new">(null);
  useSyncEvents(reload);
  // "#plans" (from Fixed costs) scrolls to the savings plans once they are there.
  useEffect(() => {
    if (location.hash !== "#plans") return;
    const id = window.setTimeout(() => document.getElementById("plans")?.scrollIntoView({ behavior: "smooth", block: "start" }), 400);
    return () => window.clearTimeout(id);
  }, [data]);

  if (!data) return <><PageHeader title={t("nav.networth")} period />{error ? <ErrorNote error={error} /> : <Loading />}</>;

  // The chart and the change follow the shared period; the accounts show today's balances.
  const shown = clipMonths(data.series, period);
  const last = shown[shown.length - 1];
  const current = !last || last.month === data.series[data.series.length - 1]?.month;
  const change = shown.length > 1 ? shown[shown.length - 1].value - shown[0].value : null;
  const value = current ? data.net_worth : (last?.value ?? data.net_worth);

  return (
    <>
      <PageHeader title={t("nav.networth")} period />
      <section className="card nwhero">
        <div className="hero-body">
          <div className="eyebrow">{current ? t("nw.today") : t("nw.endOf", { month: monthLong(last.month) })}</div>
          <div className="hero-v">
            <Odometer value={value} />
          </div>
          <p className="hero-sub">
            {change !== null && <ChangePill up={change >= 0} good={change >= 0} text={eur(Math.abs(change))} />} <span>{periodLabel(period)}</span>
          </p>
          {data.liabilities > 0 && <p className="hero-note">{t("nw.split", { assets: eur(data.assets), debts: eur(data.liabilities) })}</p>}
        </div>
        <div className="nwchart">
          {shown.length > 1 ? (
            <LineChart data={shown} label={t("nw.overTime")} />
          ) : data.series.length > 1 ? (
            <Empty title={t("period.noData")}>{t("period.noData.text")}</Empty>
          ) : (
            <Empty title={t("nw.noHistory")} icon="trend">
              {t("nw.noHistory.text")}
            </Empty>
          )}
        </div>
      </section>
      <div className="nwgrid">
        {data.accounts.map((a, i) => (
          <AccountTile key={a.id} a={a} total={data.assets} i={i} onEdit={() => setEditing(a)} />
        ))}
        <button type="button" className="nwacct add" onClick={() => setEditing("new")}>
          <Icon name="plus" size={18} />
          <span>
            <b>{t("nw.add")}</b>
            <small>{t("nw.outsideHint")}</small>
          </span>
        </button>
      </div>
      <PlansCard />
      {editing && (
        <ManualAccount
          account={editing === "new" ? null : editing}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null);
            toast(t("tx.saved"));
            reload();
          }}
        />
      )}
    </>
  );
}
