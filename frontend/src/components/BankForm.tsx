import { useEffect, useState } from "react";
import { t as tr, useT, type Key } from "../i18n";
import { api } from "../lib/api";
import { pollJob } from "../lib/app";
import { eur } from "../lib/format";
import type { BankAccount, BankInfo, BankLoginKind, Job } from "../lib/types";
import { Icon } from "./Icons";
import { Modal, Spinner } from "./UI";

export type TestResult = { connection_id: number; accounts: BankAccount[] };

export const loginLabel = (kind: BankLoginKind | undefined) => tr(`bank.login.${kind ?? "generic"}` as Key);

// "50010517" reads better as "500 105 17", the way banks print it.
const spacedBlz = (blz: string) => `${blz.slice(0, 3)} ${blz.slice(3, 6)} ${blz.slice(6)}`;

function blzFrom(text: string): string | null {
  const v = text.replace(/\s+/g, "").toUpperCase();
  if (/^\d{8}$/.test(v)) return v;
  if (/^DE\d{20}$/.test(v)) return v.slice(4, 12);
  return null;
}

// Find the bank by name, Bankleitzahl or IBAN. The list comes from the server, which has
// the big banks built in and, once imported, the FinTS institute list with every bank.
function BankPicker({ onPick }: { onPick: (b: BankInfo) => void }) {
  const t = useT();
  const [q, setQ] = useState("");
  const [found, setFound] = useState<BankInfo[] | null>(null);
  useEffect(() => {
    let live = true;
    const timer = setTimeout(() => {
      api.get<BankInfo[]>(`/banks?q=${encodeURIComponent(q.trim())}`).then((r) => live && setFound(r)).catch(() => live && setFound([]));
    }, 180);
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [q]);
  return (
    <div className="field">
      <label htmlFor="bf-bank">{t("bank.pick")}</label>
      <input className="input" id="bf-bank" autoComplete="off" placeholder={t("bank.search")} value={q} onChange={(e) => setQ(e.target.value)} />
      <span className="hint">{t("bank.searchHint")}</span>
      <div className="banklist picker">
        {found?.map((b, i) => (
          <button type="button" className="bank pick stagger" key={`${b.id}-${b.blz ?? i}`} style={{ ["--i" as string]: i }} onClick={() => onPick(b)}>
            <span className="mono">{b.short}</span>
            <span>
              <b>{b.name}</b>
              <small>{b.id === "csv-only" ? t("bank.csvOnly", { name: b.name }) : b.blz ? `BLZ ${spacedBlz(b.blz)}` : t("bank.blzFromIban")}</small>
            </span>
          </button>
        ))}
        {found && !found.length && <p className="muted small">{t("bank.noMatch")}</p>}
      </div>
    </div>
  );
}

// The TAN a bank asks for while a job waits (chipTAN, smsTAN, photoTAN). Banks that approve
// in their app don't need this; the job then just waits for the approval.
export function TanPrompt({ job }: { job: Job<unknown> | null }) {
  const t = useT();
  const [tan, setTan] = useState("");
  // Hidden from the moment it is answered until the server stops asking.
  const [sent, setSent] = useState(false);
  const pending = !!job?.tan;
  useEffect(() => {
    if (!pending) setSent(false);
  }, [pending]);
  const asking = !sent ? job?.tan : null;
  if (!job || !asking) return null;
  async function answer(value: string | null) {
    if (!job) return;
    setSent(true);
    setTan("");
    await api.post(`/jobs/${job.id}/tan`, { tan: value }).catch(() => {});
  }
  return (
    <Modal
      title={t("tan.title")}
      onClose={() => answer(null)}
      actions={
        <>
          <button className="btn ghost" onClick={() => answer(null)}>
            {t("common.cancel")}
          </button>
          <button className="btn primary" disabled={!tan.trim()} onClick={() => answer(tan)}>
            {t("tan.send")}
          </button>
        </>
      }
    >
      <p className="muted small">{asking.text || t("tan.text")}</p>
      {asking.image && <img className="tanimg" src={asking.image} alt="" />}
      <div className="field">
        <label htmlFor="tan-input">{t("tan.label")}</label>
        <input className="input" id="tan-input" autoComplete="one-time-code" inputMode="numeric" value={tan} onChange={(e) => setTan(e.target.value)} onKeyDown={(e) => e.key === "Enter" && tan.trim() && answer(tan)} />
      </div>
    </Modal>
  );
}

// The bank, its login, PIN and product ID, a connection test, and the accounts the bank reports.
export function BankForm({ onConnected, connected, onAccountsChange }: {
  onConnected: (r: TestResult) => void;
  connected: TestResult | null;
  onAccountsChange?: (accounts: BankAccount[]) => void;
}) {
  const t = useT();
  const [bank, setBank] = useState<BankInfo | null>(null);
  const [blzText, setBlzText] = useState("");
  const [server, setServer] = useState("");
  const [advanced, setAdvanced] = useState(false);
  const [login, setLogin] = useState("");
  const [pin, setPin] = useState("");
  const [productId, setProductId] = useState("");
  const [job, setJob] = useState<Job<TestResult> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [help, setHelp] = useState(false);

  // A bank with many Bankleitzahlen (Deutsche Bank, Postbank, Sparkasse) needs the user's own.
  const typedBlz = blzFrom(blzText);
  useEffect(() => {
    if (!bank?.needs_blz || !typedBlz) return;
    let live = true;
    api
      .get<BankInfo>(`/banks/${typedBlz}`)
      .then((b) => {
        if (!live) return;
        setBank({ ...b, needs_blz: false });
        setServer(b.server ?? "");
      })
      .catch((e) => live && setError((e as Error).message));
    return () => {
      live = false;
    };
  }, [bank?.needs_blz, typedBlz]);

  function pick(b: BankInfo) {
    setError(null);
    setBank(b);
    setServer(b.server ?? "");
    setBlzText("");
    setAdvanced(false);
  }

  async function test() {
    if (!bank?.blz) return;
    setBusy(true);
    setError(null);
    try {
      const custom = server.trim() && server.trim() !== bank.server ? server.trim() : null;
      const started = await api.post<Job<TestResult>>("/bank/test", { bank_code: bank.blz, server: custom, login, pin, product_id: productId });
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

  if (!bank || bank.id === "csv-only") {
    return (
      <>
        <BankPicker onPick={pick} />
        {bank && <div className="callout"><span>{t("bank.csvOnly", { name: bank.name })}</span></div>}
      </>
    );
  }

  const waiting = job?.state === "waiting" && !job.tan;
  const needsServer = !server.trim();
  const ready = !!bank.blz && !needsServer && !!login && !!pin && productId.length >= 5;
  const facts = [bank.blz ? `BLZ ${spacedBlz(bank.blz)}` : null, t("bank.readOnly").replace(/\.$/, ""), bank.app ? t("bank.app", { app: bank.app }) : null].filter(Boolean);
  return (
    <>
      <div className="banklist">
        <div className="bank">
          <span className="mono">{bank.short}</span>
          <div style={{ flex: 1 }}>
            <b>{bank.name}</b>
            <small>{facts.join(" · ")}</small>
            <small>{bank.tested ? t("bank.tested") : t("bank.untested")}</small>
          </div>
          {!connected && (
            <button type="button" className="linkbtn" onClick={() => setBank(null)}>
              {t("bank.change")}
            </button>
          )}
        </div>
      </div>
      {bank.needs_blz && (
        <div className="field">
          <label htmlFor="bf-blz">{t("bank.blz")}</label>
          <input className="input" id="bf-blz" autoComplete="off" inputMode="numeric" value={blzText} onChange={(e) => setBlzText(e.target.value)} />
          <span className="hint">{t("bank.blzHint")}</span>
        </div>
      )}
      {bank.blz && (needsServer || advanced || bank.needs_server) && (
        <div className="field">
          <label htmlFor="bf-server">{t("bank.server")}</label>
          <input className="input" id="bf-server" autoComplete="off" placeholder="https://" value={server} onChange={(e) => setServer(e.target.value.trim())} />
          <span className="hint">{needsServer ? t("bank.serverNeeded") : t("bank.serverHint")}</span>
        </div>
      )}
      <div className="row2">
        <div className="field">
          <label htmlFor="bf-login">{loginLabel(bank.login)}</label>
          <input className="input" id="bf-login" autoComplete="off" value={login} onChange={(e) => setLogin(e.target.value.trim())} />
        </div>
        <div className="field">
          <label htmlFor="bf-pin">{t("bank.pin")}</label>
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
          <span>{t("bank.steps")}</span>
        </div>
      )}
      <div className="hstack">
        <button className="btn" onClick={test} disabled={busy || !ready}>
          {busy && <Spinner />}
          {busy ? (waiting ? t("bank.waiting") : t("bank.connecting", { bank: bank.label })) : connected ? t("bank.testAgain") : t("bank.test")}
        </button>
        {bank.blz && !needsServer && !advanced && !bank.needs_server && (
          <button type="button" className="linkbtn" onClick={() => setAdvanced(true)}>
            {t("bank.advanced")}
          </button>
        )}
      </div>
      {waiting && (
        <div className="insight">
          <Icon name="bell" size={18} className="bell-ring" />
          <span>
            <b>{bank.app ? t("bank.app", { app: bank.app }) : t("wz.approve")}</b> {t("bank.approveOnce")}
          </span>
        </div>
      )}
      <TanPrompt job={job} />
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
