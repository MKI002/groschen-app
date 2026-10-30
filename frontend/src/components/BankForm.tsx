import { useState } from "react";
import { useT } from "../i18n";
import { api } from "../lib/api";
import { pollJob } from "../lib/app";
import { eur } from "../lib/format";
import type { BankAccount, Job } from "../lib/types";
import { Icon } from "./Icons";
import { Spinner } from "./UI";

export type TestResult = { connection_id: number; accounts: BankAccount[] };

// Zugangsnummer, PIN and product ID, a connection test, and the accounts ING reports.
export function BankForm({ onConnected, connected, onAccountsChange }: {
  onConnected: (r: TestResult) => void;
  connected: TestResult | null;
  onAccountsChange?: (accounts: BankAccount[]) => void;
}) {
  const t = useT();
  const [login, setLogin] = useState("");
  const [pin, setPin] = useState("");
  const [productId, setProductId] = useState("");
  const [job, setJob] = useState<Job<TestResult> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [help, setHelp] = useState(false);

  async function test() {
    setBusy(true);
    setError(null);
    try {
      const started = await api.post<Job<TestResult>>("/bank/test", { bank_code: "50010517", login, pin, product_id: productId });
      const done = await pollJob(started, setJob);
      if (done.state === "done" && done.result) {
        setPin("");
        onConnected(done.result);
      } else setError(done.error || t("bank.testFailed"));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
      setJob(null);
    }
  }

  async function toggle(acc: BankAccount, enabled: boolean) {
    await api.patch(`/accounts/${acc.id}`, { enabled });
    onAccountsChange?.((connected?.accounts ?? []).map((a) => (a.id === acc.id ? { ...a, enabled: enabled ? 1 : 0 } : a)));
  }

  const waiting = job?.state === "waiting";
  return (
    <>
      <div className="banklist">
        <div className="bank">
          <span className="mono">ING</span>
          <div>
            <b>ING-DiBa AG</b>
            <small>{t("bank.ingLine")}</small>
          </div>
        </div>
      </div>
      <div className="row2">
        <div className="field">
          <label htmlFor="bf-login">Zugangsnummer</label>
          <input className="input" id="bf-login" inputMode="numeric" autoComplete="off" placeholder={t("bank.digits")} value={login} onChange={(e) => setLogin(e.target.value.trim())} />
        </div>
        <div className="field">
          <label htmlFor="bf-pin">Internetbanking PIN</label>
          <input className="input" id="bf-pin" type="password" autoComplete="off" value={pin} onChange={(e) => setPin(e.target.value)} />
          <span className="hint">{t("bank.pinHint")}</span>
        </div>
      </div>
      <div className="field">
        <label htmlFor="bf-product">{t("bank.product")}</label>
        <input className="input" id="bf-product" autoComplete="off" value={productId} onChange={(e) => setProductId(e.target.value.trim())} />
        <span className="hint">
          {t("bank.productHint")}{" "}
          <button type="button" className="linkbtn" onClick={() => setHelp((v) => !v)}>
            {help ? t("bank.hideSteps") : t("bank.howGet")}
          </button>
        </span>
      </div>
      {help && (
        <div className="callout">
          <span>
            {t("bank.steps")}
          </span>
        </div>
      )}
      <div className="hstack">
        <button className="btn" onClick={test} disabled={busy || !login || !pin || productId.length < 5}>
          {busy && <Spinner />}
          {busy ? (waiting ? t("bank.waiting") : t("bank.connecting")) : connected ? t("bank.testAgain") : t("bank.test")}
        </button>
      </div>
      {waiting && (
        <div className="insight">
          <Icon name="bell" size={18} className="bell-ring" />
          <span>
            <b>{t("wz.approve")}</b> {t("bank.approveOnce")}
          </span>
        </div>
      )}
      {error && (
        <p className="err" role="alert">
          {error}
        </p>
      )}
      {connected && (
        <div className="result">
          <div className="ok">
            <span className="dotok" />
            {t("bank.found", { n: connected.accounts.length })}
          </div>
          {connected.accounts.map((a, i) => (
            <label className="acct stagger" key={a.id} style={{ ["--i" as string]: i }}>
              <input type="checkbox" checked={a.enabled !== 0} onChange={(e) => toggle(a, e.target.checked)} />
              {a.name}
              <span className="iban">
                {a.kind === "depot" ? t("bank.depot") : a.iban ? `${a.iban.slice(0, 4)} ${a.iban.slice(4, 8)} •••• ${a.iban.slice(-4)}` : ""}
                {a.balance !== null && a.balance !== undefined ? ` · ${eur(a.balance)}` : ""}
              </span>
            </label>
          ))}
        </div>
      )}
      <div className="callout">
        <Icon name="lock" size={18} />
        <span>
          <b>{t("bank.readOnly")}</b> {t("bank.readOnly.text")}
        </span>
      </div>
    </>
  );
}
