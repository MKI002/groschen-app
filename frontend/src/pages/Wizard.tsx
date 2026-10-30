import { useEffect, useState, type ReactNode } from "react";
import { BankForm, type TestResult } from "../components/BankForm";
import { Icon, Logo } from "../components/Icons";
import { LangPicker } from "../components/LangPicker";
import { celebrate } from "../components/Motion";
import { Seg, Spinner } from "../components/UI";
import { getLang, useT, type Key } from "../i18n";
import { api } from "../lib/api";
import { pollJob } from "../lib/app";
import { dateShort, int } from "../lib/format";
import type { Job, SettingsValues, Status } from "../lib/types";

const REMIND = [30, 15, 7];

const STEPS: [Key, Key][] = [
  ["wz.step1", "wz.step1.sub"],
  ["wz.step2", "wz.step2.sub"],
  ["wz.step3", "wz.step3.sub"],
  ["wz.step4", "wz.step4.sub"],
  ["wz.step5", "wz.step5.sub"],
];

type ImportResult = { account_name: string; imported: number; skipped: number; first: string | null; last: string | null; file: string };

export default function Wizard({ status, onFinished }: { status: Status; onFinished: () => void }) {
  const t = useT();
  const [step, setStep] = useState(status.has_user ? 2 : 1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // step 1
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [pass, setPass] = useState("");
  const [pass2, setPass2] = useState("");

  // step 2
  const [connected, setConnected] = useState<TestResult | null>(null);

  // step 3
  const [imports, setImports] = useState<ImportResult[]>([]);
  const [importErrors, setImportErrors] = useState<string[]>([]);
  const [prices, setPrices] = useState<string | null>(null);

  // step 4
  const [prefs, setPrefs] = useState<Partial<SettingsValues>>({
    categorizer: "model", sync_schedule: "daily", reminder_days: 15, alert_price_up: true, unusual_alerts: true, review_uncertain: true,
  });

  // step 5
  const [finishJob, setFinishJob] = useState<Job | null>(null);

  useEffect(() => setError(null), [step]);

  async function createAccount() {
    if (pass !== pass2) return setError(t("wz.passMismatch"));
    if (pass.length < 8) return setError(t("wz.passShort"));
    setBusy(true);
    try {
      await api.post("/setup/account", { name: name.trim() || username, username, password: pass });
      setStep(2);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function importFiles(files: FileList | null) {
    if (!files) return;
    setBusy(true);
    for (const file of Array.from(files)) {
      const form = new FormData();
      form.append("file", file);
      try {
        const r = await api.upload<ImportResult>("/import/csv", form);
        setImports((x) => [...x, r]);
      } catch (e) {
        setImportErrors((x) => [...x, `${file.name}: ${(e as Error).message}`]);
      }
    }
    setBusy(false);
  }

  async function importPrices(files: FileList | null) {
    const file = files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    try {
      const r = await api.upload<{ imported: number; isins: string[]; first: string; last: string }>("/import/prices", form);
      setPrices(t("wz.pricesDone", { n: r.imported, funds: t("wz.funds", { n: r.isins.length }), from: dateShort(r.first), to: dateShort(r.last) }));
    } catch (e) {
      setImportErrors((x) => [...x, `${file.name}: ${(e as Error).message}`]);
    }
  }

  async function savePrefs() {
    setBusy(true);
    try {
      await api.patch("/settings", { ...prefs, language: getLang() });
      setStep(5);
      const job = await api.post<Job>("/setup/finish");
      const done = await pollJob(job, setFinishJob);
      if (done.state === "error") setError(done.error);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function openDashboard() {
    setBusy(true);
    try {
      await api.post("/setup/complete");
      onFinished();
    } catch (e) {
      setError((e as Error).message);
      setBusy(false);
    }
  }

  const finished = finishJob?.state === "done";
  useEffect(() => {
    if (finished) celebrate(document.querySelector(".wz-main h2"), 26);
  }, [finished]);
  const failed = finishJob?.state === "error";

  let body: ReactNode = null;
  let next: ReactNode = null;
  let back = step > 2 && step < 5;

  if (step === 1) {
    body = (
      <>
        <h2>{t("wz.welcome")}</h2>
        <p className="sub">{t("wz.welcome.sub")}</p>
        <div className="row2">
          <div className="field">
            <label htmlFor="wz-name">{t("wz.name")}</label>
            <input className="input" id="wz-name" autoComplete="name" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="wz-user">{t("login.username")}</label>
            <input className="input" id="wz-user" autoComplete="username" value={username} onChange={(e) => setUsername(e.target.value)} />
          </div>
        </div>
        <div className="row2">
          <div className="field">
            <label htmlFor="wz-pass">{t("login.password")}</label>
            <input className="input" id="wz-pass" type="password" autoComplete="new-password" value={pass} onChange={(e) => setPass(e.target.value)} />
            <span className="hint">{t("wz.passHint")}</span>
          </div>
          <div className="field">
            <label htmlFor="wz-pass2">{t("wz.pass2")}</label>
            <input className="input" id="wz-pass2" type="password" autoComplete="new-password" value={pass2} onChange={(e) => setPass2(e.target.value)} />
          </div>
        </div>
      </>
    );
    next = (
      <button className="btn primary" disabled={busy || username.trim().length < 2 || !pass} onClick={createAccount}>
        {busy && <Spinner />}
        {t("common.continue")}
      </button>
    );
  }

  if (step === 2) {
    body = (
      <>
        <h2>{t("wz.bank")}</h2>
        <p className="sub">{t("wz.bank.sub")}</p>
        <BankForm connected={connected} onConnected={setConnected} onAccountsChange={(accounts) => setConnected((c) => c && { ...c, accounts })} />
      </>
    );
    next = (
      <>
        {!connected && (
          <button className="btn ghost" onClick={() => setStep(3)}>
            {t("wz.skipCsv")}
          </button>
        )}
        <button className="btn primary" disabled={!connected} onClick={() => setStep(3)}>
          {t("common.continue")}
        </button>
      </>
    );
  }

  if (step === 3) {
    body = (
      <>
        <h2>{t("wz.history")}</h2>
        <p className="sub">{t("wz.history.sub")}</p>
        <label
          className="drop"
          htmlFor="wz-file"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            importFiles(e.dataTransfer.files);
          }}
        >
          <Icon name="upload" size={28} />
          <span>
            <b>{t("wz.drop")}</b> {t("wz.drop.click")}
          </span>
          <span className="small">{t("wz.drop.skip")}</span>
          <input type="file" id="wz-file" accept=".csv,text/csv" multiple hidden onChange={(e) => importFiles(e.target.files)} />
        </label>
        {busy && (
          <p className="muted hstack">
            <Spinner /> {t("wz.importing")}
          </p>
        )}
        {imports.map((r, i) => (
          <div className="result" key={i}>
            <div className="ok">
              <span className="dotok" />
              {r.file} → {r.account_name}
            </div>
            <span className="muted small">
              {t("wz.imported", { n: r.imported })}
              {r.first ? ` ${t("wz.fromTo", { from: dateShort(r.first), to: dateShort(r.last) })}` : ""} · {t("wz.already", { n: int(r.skipped) })}
            </span>
          </div>
        ))}
        {importErrors.map((e, i) => (
          <p className="err" key={i}>
            {e}
          </p>
        ))}
        <div className="callout">
          <span>
            <b>{t("wz.prices.title")}</b> {t("wz.prices.text")}{" "}
            <label className="linkbtn" htmlFor="wz-prices">
              {t("wz.prices.choose")}
            </label>
            <input type="file" id="wz-prices" accept=".csv,.txt,text/csv" hidden onChange={(e) => importPrices(e.target.files)} />
            {prices && <span className="okmsg"> · {prices}</span>}
          </span>
        </div>
      </>
    );
    next = (
      <button className="btn primary" disabled={busy} onClick={() => setStep(4)}>
        {imports.length ? t("common.continue") : t("wz.skip90")}
      </button>
    );
  }

  if (step === 4) {
    const set = <K extends keyof SettingsValues>(k: K, v: SettingsValues[K]) => setPrefs((p) => ({ ...p, [k]: v }));
    body = (
      <>
        <h2>{t("wz.smart")}</h2>
        <p className="sub">{t("wz.smart.sub")}</p>
        <div className="choice" role="radiogroup" aria-label={t("wz.categorizer")}>
          <label className="opt">
            <input type="radio" name="cz" checked={prefs.categorizer === "model"} onChange={() => set("categorizer", "model")} />
            <span>
              <b>{t("wz.model")}</b>
              <small>{t("wz.model.text")}</small>
            </span>
          </label>
          <label className="opt">
            <input type="radio" name="cz" checked={prefs.categorizer === "rules"} onChange={() => set("categorizer", "rules")} />
            <span>
              <b>{t("wz.rules")}</b>
              <small>{t("wz.rules.text")}</small>
            </span>
          </label>
        </div>
        <div className="callout">
          <span>
            <b>{t("wz.light")}</b> {t("wz.light.text")}
          </span>
        </div>
        <div className="row2">
          <div className="field">
            <label htmlFor="wz-sync">{t("sched.label")}</label>
            <select className="input" id="wz-sync" value={prefs.sync_schedule} onChange={(e) => set("sync_schedule", e.target.value as SettingsValues["sync_schedule"])}>
              <option value="daily">{t("sched.daily")}</option>
              <option value="twice">{t("sched.twice")}</option>
              <option value="6h">{t("sched.6h")}</option>
            </select>
          </div>
          <div className="field">
            <span className="label">{t("remind.label")}</span>
            <Seg
              label={t("remind.label")}
              value={String(prefs.reminder_days ?? 15)}
              onChange={(x) => set("reminder_days", Number(x))}
              options={REMIND.map((n) => [String(n), t("remind.before", { n })])}
            />
          </div>
        </div>
        <div className="checks">
          <label className="check">
            <input type="checkbox" checked={!!prefs.alert_price_up} onChange={(e) => set("alert_price_up", e.target.checked)} />
            {t("pref.subs")}
          </label>
          <label className="check">
            <input type="checkbox" checked={!!prefs.unusual_alerts} onChange={(e) => set("unusual_alerts", e.target.checked)} />
            {t("pref.unusual")}
          </label>
          <label className="check">
            <input type="checkbox" checked={!!prefs.review_uncertain} onChange={(e) => set("review_uncertain", e.target.checked)} />
            {t("pref.review")}
          </label>
        </div>
      </>
    );
    next = (
      <button className="btn primary" disabled={busy} onClick={savePrefs}>
        {connected ? t("wz.startSync") : t("wz.finish")}
      </button>
    );
  }

  if (step === 5) {
    back = false;
    const steps = finishJob?.steps ?? [];
    body = (
      <>
        <h2>{finished ? t("wz.done") : failed ? t("wz.failed") : t("wz.working")}</h2>
        <p className="sub">
          {finished
            ? t("wz.done.sub")
            : failed
              ? t("wz.failed.sub")
              : connected
                ? t("wz.working.bank")
                : t("wz.working.csv")}
        </p>
        <ul className="progress-list">
          {steps.map((s, i) => (
            <li key={i} className={s.state === "running" ? "run" : s.state === "done" ? "ok" : ""}>
              <span className="ic">{s.state === "done" ? "✓" : s.state === "error" ? "!" : ""}</span>
              {s.label}
            </li>
          ))}
        </ul>
        {finishJob?.state === "waiting" && (
          <div className="insight">
            <Icon name="bell" size={18} />
            <span>
              <b>{t("wz.approve")}</b> {t("wz.approve.wait")}
            </span>
          </div>
        )}
      </>
    );
    next = (
      <button className="btn primary" disabled={busy && !finished && !failed} onClick={openDashboard}>
        {t("wz.open")}
      </button>
    );
  }

  return (
    <div id="wizard">
      <div className="wz">
        <aside className="wz-rail">
          <div className="brand">
            <Logo />
            Groschen
          </div>
          <LangPicker />
          <ol className="wz-steps">
            {STEPS.map(([title, s], i) => {
              const n = i + 1;
              return (
                <li key={title} className={n < step ? "done" : n === step ? "cur" : ""} aria-current={n === step ? "step" : undefined}>
                  <span className="n">{n < step ? "✓" : n}</span>
                  <span>
                    <b>{t(title)}</b>
                    <small>{t(s)}</small>
                  </span>
                </li>
              );
            })}
          </ol>
          <div className="stepdots" aria-hidden="true">
            {STEPS.map((_, i) => (
              <i key={i} className={i < step ? "on" : ""} />
            ))}
          </div>
          <p className="fine">{t("wz.fine")}</p>
        </aside>
        <section className="wz-main">
          <div className="wz-body">
            {body}
            {error && (
              <p className="err" role="alert">
                {error}
              </p>
            )}
          </div>
          <div className="wz-foot">
            <button className="btn ghost" style={{ visibility: back ? "visible" : "hidden" }} onClick={() => setStep((s) => Math.max(2, s - 1))}>
              {t("common.back")}
            </button>
            <div className="hstack">{next}</div>
          </div>
        </section>
      </div>
    </div>
  );
}
