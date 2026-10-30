import { useEffect, useState, type ReactNode } from "react";
import { CategoryPicker, forgetCategories, useCategories } from "../components/CategoryPicker";
import { confirmBankLogin, openDialog } from "../components/Dialogs";
import { Backups } from "../components/Backups";
import { SecuritySettings } from "../components/Security";
import { Icon } from "../components/Icons";
import { EGGS, eggHint, eggName, eggsOn, resetFound, setEggsOn, useFoundEggs } from "../components/Eggs";
import { motionPref, setMotionPref, type MotionPref } from "../components/Motion";
import { Card, Disclosure, ErrorNote, Loading, Modal, NumberSetting, Seg, Spinner, Switch, Tabs, useApi, useConfirm, useToast } from "../components/UI";
import { LangPicker } from "../components/LangPicker";
import { catName, getLang, t, useT, type Key } from "../i18n";
import { api } from "../lib/api";
import { useApp } from "../lib/app";
import { colorVar, dateShort, eur, eurPublic, relTime, whenNext } from "../lib/format";
import { redirect } from "../lib/router";
import { PageHeader } from "./Shell";
import type { Category, Connection, Learned, Payday, Paydays, Rule, SettingsInfo, SettingsValues } from "../lib/types";

function Row({ title, sub, children }: { title: ReactNode; sub?: ReactNode; children?: ReactNode }) {
  return (
    <div className="srow">
      <div className="t">
        <b>{title}</b>
        {sub && <small>{sub}</small>}
      </div>
      {children}
    </div>
  );
}

// --- bank ------------------------------------------------------------------------

// The names the bank knows the user by. Money sent to them stays the user's: moved, saved or invested, not spent.
function OwnNames({ names, onChange }: { names: string[]; onChange: (names: string[]) => void }) {
  useT();
  const [draft, setDraft] = useState<string | null>(null);
  const name = (draft ?? "").trim().replace(/\s+/g, " ");
  const words = name.split(" ").filter((w) => w.replace(/[^\p{L}]/gu, "").length > 1);
  const ok = words.length >= 2 && !names.some((n) => n.toLowerCase() === name.toLowerCase());
  return (
    <div className="srow wrap">
      <div className="t">
        <b>{t("own.title")}</b>
        <small>{t("own.sub")}</small>
      </div>
      <div className="own-names">
        {names.map((n) => (
          <span className="chip static" key={n}>
            {n}
            <button type="button" className="chip-x" aria-label={t("own.remove", { name: n })} onClick={() => onChange(names.filter((x) => x !== n))}>
              <Icon name="x" size={12} />
            </button>
          </span>
        ))}
        {draft === null
          ? names.length < 6 && (
              <button type="button" className="chip add" onClick={() => setDraft("")}>
                <Icon name="plus" size={13} />
                {t("own.add")}
              </button>
            )
          : (
              <form
                className="inline-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  if (!ok) return;
                  onChange([...names, name]);
                  setDraft(null);
                }}
              >
                <input
                  className="input"
                  autoFocus
                  value={draft}
                  maxLength={80}
                  placeholder={t("own.ph")}
                  aria-label={t("own.ph")}
                  onChange={(e) => setDraft(e.target.value)}
                  onKeyDown={(e) => e.key === "Escape" && setDraft(null)}
                />
                <button className="btn sm primary" disabled={!ok}>
                  {t("own.save")}
                </button>
                <button type="button" className="btn sm ghost" onClick={() => setDraft(null)}>
                  {t("common.cancel")}
                </button>
              </form>
            )}
      </div>
    </div>
  );
}

function ChangeLogin({ c, onClose }: { c: Connection; onClose: () => void }) {
  const toast = useToast();
  useT();
  const [login, setLogin] = useState("");
  const [pin, setPin] = useState("");
  const [product, setProduct] = useState("");
  const [busy, setBusy] = useState(false);
  async function save() {
    setBusy(true);
    await api.patch(`/connections/${c.id}`, { login: login || null, pin: pin || null, product_id: product || null });
    toast(t("set.loginSaved"));
    onClose();
  }
  return (
    <Modal
      title={t("set.changeLogin")}
      onClose={onClose}
      actions={
        <>
          <button className="btn ghost" onClick={onClose}>
            {t("common.cancel")}
          </button>
          <button className="btn primary" disabled={busy || (!login && !pin && !product)} onClick={save}>
            {t("common.save")}
          </button>
        </>
      }
    >
      <p className="muted small">{t("set.onlyChanged")}</p>
      <div className="field">
        <label htmlFor="cl-login">Zugangsnummer</label>
        <input className="input" id="cl-login" autoComplete="off" placeholder={c.login_hint} value={login} onChange={(e) => setLogin(e.target.value.trim())} />
      </div>
      <div className="field">
        <label htmlFor="cl-pin">{t("set.newPin")}</label>
        <input className="input" id="cl-pin" type="password" autoComplete="off" value={pin} onChange={(e) => setPin(e.target.value)} />
      </div>
      <div className="field">
        <label htmlFor="cl-product">{t("bank.product")}</label>
        <input className="input" id="cl-product" autoComplete="off" value={product} onChange={(e) => setProduct(e.target.value.trim())} />
      </div>
    </Modal>
  );
}

function ConnectionCard({ c, reminder }: { c: Connection; reminder: number }) {
  const { sync, syncing, refresh } = useApp();
  const toast = useToast();
  const { confirm, dialog } = useConfirm();
  useT();
  const [editing, setEditing] = useState(false);
  const left = c.login_days_left;
  const due = left <= reminder;
  const tone = left <= 3 ? "bad" : due ? "warn" : "";

  async function toggle(id: number, enabled: boolean) {
    await api.patch(`/accounts/${id}`, { enabled });
    refresh();
  }
  async function disconnect() {
    const ok = await confirm({ title: t("set.disconnectTitle"), text: t("set.confirmDisconnect"), action: t("set.disconnect") });
    if (!ok) return;
    await api.del(`/connections/${c.id}`);
    toast(t("set.disconnected"));
    refresh();
  }

  // Everyday actions first and big, rare ones tucked under "Advanced", the one you can't undo last and red.
  return (
    <div className="conn">
      <div className="conn-h">
        <span className="mono">{c.short}</span>
        <div style={{ flex: 1 }}>
          <b>{c.bank_name}</b>
          <small>
            FinTS · {t("set.loginHint", { hint: c.login_hint })} · {t("set.lastSync", { when: relTime(c.last_sync_at) })}
          </small>
        </div>
        <span className={`tag ${c.status === "error" ? "bad" : "good"}`}>{c.status === "error" ? t("set.needsAttention") : t("set.connected")}</span>
      </div>
      {c.last_error && <ErrorNote error={c.last_error} />}
      <div className="conn-actions">
        <button className="btn sm primary" onClick={() => sync()} disabled={!!syncing}>
          {syncing ? <Spinner /> : <Icon name="refresh" size={15} />}
          {t("shell.syncNow")}
        </button>
        {/* Always there: Groschen can't see a login in the ING app, so it is told right after. */}
        <button className="btn sm" onClick={() => confirmBankLogin(c, toast, refresh)}>
          <Icon name="check" size={15} />
          {t("set.loggedIn")}
        </button>
        <button className="btn sm" onClick={() => setEditing(true)}>
          <Icon name="pencil" size={14} />
          {t("set.changeLogin")}
        </button>
      </div>
      <div style={{ display: "grid", gap: 6 }}>
        <div className="hstack small" style={{ justifyContent: "space-between" }}>
          <span>{t("set.loginWithin")}</span>
          <b>{t("set.days", { n: left })}</b>
        </div>
        <div className="meter">
          <span className={tone} style={{ width: `${Math.max(3, (left / 90) * 100)}%` }} />
        </div>
        <small className="muted small">{t("set.loginExplain", { due: dateShort(c.login_due), n: reminder, button: t("set.loggedIn") })}</small>
      </div>
      <div className="conn-accounts">
        <span className="label">{t("set.accountsShown")}</span>
        {c.accounts.map((a) => (
          <Row key={a.id} title={a.name} sub={a.balance !== null ? eur(a.balance) : undefined}>
            <Switch label={t("set.showAccount", { name: a.name })} checked={a.enabled === 1} onChange={(x) => toggle(a.id, x)} />
          </Row>
        ))}
      </div>
      <Disclosure label={t("set.advanced")}>
        <Row title={t("set.fetch90")} sub={t("set.fetch90.sub")}>
          <button className="btn sm" onClick={() => sync(true)} disabled={!!syncing}>
            {t("set.fetch90.btn")}
          </button>
        </Row>
        <Row title={t("set.disconnectRow")} sub={t("set.disconnect.sub")}>
          <button className="btn sm ghost danger" onClick={disconnect}>
            {t("set.disconnect")}
          </button>
        </Row>
      </Disclosure>
      {editing && <ChangeLogin c={c} onClose={() => setEditing(false)} />}
      {dialog}
    </div>
  );
}

// --- import ------------------------------------------------------------------------

// Bank statements come in here; the price history is imported on the Investments page where it is used.
function CsvImport() {
  const toast = useToast();
  useT();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function upload(files: FileList | null) {
    if (!files?.length) return;
    setBusy(true);
    setError(null);
    for (const f of Array.from(files)) {
      const form = new FormData();
      form.append("file", f);
      try {
        const r = await api.upload<{ imported: number; account_name: string; skipped?: number }>("/import/csv", form);
        toast(t("set.importedTx", { n: r.imported, account: r.account_name, skipped: r.skipped ?? 0 }));
        window.dispatchEvent(new Event("groschen:synced"));
      } catch (e) {
        setError(`${f.name}: ${(e as Error).message}`);
      }
    }
    setBusy(false);
  }
  return (
    <Card title={t("set.import")}>
      <Row title={t("set.importCsv")} sub={t("set.importCsv.sub")}>
        <label className="btn sm" htmlFor="set-csv">
          {busy ? <Spinner /> : <Icon name="upload" size={15} />}
          {t("set.chooseFiles")}
        </label>
        <input id="set-csv" type="file" accept=".csv,text/csv" multiple hidden onChange={(e) => upload(e.target.files)} />
      </Row>
      {error && <p className="err">{error}</p>}
    </Card>
  );
}

// --- categories, rules ---------------------------------------------------------------

const FIELD_LABEL: Record<string, Key> = { counterparty: "rule.merchant", purpose: "rule.purpose", any: "rule.any" };

function Rules({ cats }: { cats: Category[] }) {
  const toast = useToast();
  useT();
  const { data: rules, reload } = useApi<Rule[]>("/rules");
  const [field, setField] = useState("counterparty");
  const [op, setOp] = useState("contains");
  const [value, setValue] = useState("");
  const [cat, setCat] = useState<number | "">("");
  async function add() {
    const r = await api.post<{ applied: number }>("/rules", { field, op, value, category_id: cat });
    setValue("");
    toast(t("rule.saved", { n: r.applied }));
    reload();
    window.dispatchEvent(new Event("groschen:synced"));
  }
  async function remove(id: number) {
    await api.del(`/rules/${id}`);
    reload();
  }
  return (
    <>
      {(rules ?? []).map((r) => (
        <div className="rule" key={r.id}>
          {t("rule.if")} {t(FIELD_LABEL[r.field] ?? "rule.any")} {r.op === "equals" ? t("rule.is") : t("rule.contains")} <code>{r.value}</code> {t("rule.then")}{" "}
          <span className="catchip">
            <span className="sq" style={{ background: colorVar(r.color) }} />
            {catName(r.category)}
          </span>
          <button className="ib" style={{ marginLeft: "auto" }} aria-label={t("rule.delete")} onClick={() => remove(r.id)}>
            <Icon name="x" size={14} />
          </button>
        </div>
      ))}
      {rules && !rules.length && <p className="txsum">{t("rule.none")}</p>}
      <div className="inline-form">
        <span className="small">{t("rule.if")}</span>
        <select className="input" aria-label={t("rule.field")} value={field} onChange={(e) => setField(e.target.value)}>
          <option value="counterparty">{t("rule.merchant")}</option>
          <option value="purpose">{t("rule.purpose")}</option>
          <option value="any">{t("rule.any")}</option>
        </select>
        <select className="input" aria-label={t("rule.match")} value={op} onChange={(e) => setOp(e.target.value)}>
          <option value="contains">{t("rule.contains")}</option>
          <option value="equals">{t("rule.exactly")}</option>
        </select>
        <input className="input" aria-label={t("rule.text")} placeholder={t("rule.example")} value={value} onChange={(e) => setValue(e.target.value)} />
        <select className="input" aria-label={t("tx.category")} value={cat} onChange={(e) => setCat(Number(e.target.value))}>
          <option value="">{t("rule.category")}</option>
          {cats.map((c) => (
            <option key={c.id} value={c.id}>
              {catName(c.group)} · {catName(c.name)}
            </option>
          ))}
        </select>
        <button className="btn sm" disabled={!value.trim() || cat === ""} onClick={add}>
          <Icon name="plus" size={15} />
          {t("rule.add")}
        </button>
      </div>
    </>
  );
}

// Each merchant with its category as a chip; a click opens the same picker as a booking, with search.
function LearnedMerchants() {
  useT();
  const toast = useToast();
  const { data, reload } = useApi<Learned[]>("/learned");
  const [all, setAll] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [picking, setPicking] = useState<Learned | null>(null);
  async function change(m: Learned, category_id: number) {
    setBusy(m.key);
    const r = await api.put<{ changed: number }>("/learned", { key: m.key, category_id });
    setBusy(null);
    toast(r.changed ? t("learn.moved", { n: r.changed, merchant: m.name }) : t("tx.saved"));
    reload();
    window.dispatchEvent(new Event("groschen:synced"));
  }
  async function forget(m: Learned) {
    setBusy(m.key);
    await api.del(`/learned?key=${encodeURIComponent(m.key)}`);
    setBusy(null);
    toast(t("learn.forgotten", { merchant: m.name }));
    reload();
    window.dispatchEvent(new Event("groschen:synced"));
  }
  if (!data) return null;
  if (!data.length) return <p className="txsum">{t("learn.none")}</p>;
  const shown = all ? data : data.slice(0, 6);
  return (
    <>
      <p className="txsum">{t("learn.intro")}</p>
      {shown.map((m, i) => (
        <div className="rule learned stagger" key={m.key} style={{ ["--i" as string]: i }}>
          <b title={m.key}>{m.name}</b>
          <button type="button" className="chip learned-cat" disabled={busy === m.key} aria-label={t("learn.catFor", { merchant: m.name })} onClick={() => setPicking(m)}>
            <span className="sq" style={{ background: colorVar(m.color) }} />
            <span className="learned-name">{catName(m.category)}</span>
            <Icon name="chevDown" size={13} />
          </button>
          <button className="ib sm" title={t("learn.forget")} aria-label={t("learn.forgetLabel", { merchant: m.name })} onClick={() => forget(m)} disabled={busy === m.key}>
            {busy === m.key ? <Spinner /> : <Icon name="x" size={14} />}
          </button>
        </div>
      ))}
      {data.length > 6 && (
        <button className="btn sm ghost" onClick={() => setAll((x) => !x)}>
          {all ? t("learn.fewer") : t("learn.all", { n: data.length })}
        </button>
      )}
      {picking && (
        <Modal title={t("learn.catFor", { merchant: picking.name })} onClose={() => setPicking(null)}>
          <CategoryPicker
            value={picking.category_id}
            onPick={(id) => {
              setPicking(null);
              if (id !== picking.category_id) void change(picking, id);
            }}
          />
        </Modal>
      )}
    </>
  );
}

function CategoryEditor({ onClose }: { onClose: () => void }) {
  useT();
  const { confirm, dialog } = useConfirm();
  const [cats, setCats] = useState<Category[] | null>(null);
  const [name, setName] = useState("");
  const [group, setGroup] = useState("");
  const [kind, setKind] = useState("expense");
  const load = () => api.get<Category[]>("/categories").then(setCats);
  useEffect(() => {
    load();
  }, []);
  const groups = [...new Set((cats ?? []).map((c) => c.group))];
  async function add() {
    await api.post("/categories", { name, group, kind });
    setName("");
    forgetCategories();
    load();
  }
  async function remove(c: Category) {
    if (c.used && !(await confirm({ title: t("cat.deleteTitle"), text: t("cat.confirmDelete", { n: c.used, name: catName(c.name) }), action: t("common.delete") }))) return;
    await api.del(`/categories/${c.id}`);
    forgetCategories();
    load();
  }
  async function rename(c: Category) {
    const n = prompt(t("cat.newName"), catName(c.name));
    // Keep the stored name when the shown translation comes back unchanged.
    if (!n || n === c.name || n === catName(c.name)) return;
    await api.patch(`/categories/${c.id}`, { name: n, group: c.group, kind: c.kind });
    forgetCategories();
    load();
  }
  return (
    <>
    <Modal title={t("sp.cats")} onClose={onClose}>
      {!cats ? (
        <Loading />
      ) : (
        <div className="catpick">
          {groups.map((g) => (
            <div key={g}>
              <h4>{catName(g)}</h4>
              {cats
                .filter((c) => c.group === g)
                .map((c) => (
                  <div className="srow" key={c.id}>
                    <span className="hstack">
                      <span className="sq" style={{ background: colorVar(c.color) }} />
                      {catName(c.name)}
                      <span className="muted small">{t("cat.used", { n: c.used })}</span>
                    </span>
                    <span className="row-actions">
                      <button className="btn sm ghost" onClick={() => rename(c)}>
                        {t("cat.rename")}
                      </button>
                      <button className="btn sm ghost danger" onClick={() => remove(c)}>
                        {t("common.delete")}
                      </button>
                    </span>
                  </div>
                ))}
            </div>
          ))}
        </div>
      )}
      <div className="inline-form">
        <input className="input" placeholder={t("cat.new")} aria-label={t("cat.newLabel")} value={name} onChange={(e) => setName(e.target.value)} />
        <input className="input" placeholder={t("group.title")} aria-label={t("group.title")} list="cat-groups" value={group} onChange={(e) => setGroup(e.target.value)} />
        <datalist id="cat-groups">
          {groups.map((g) => (
            <option key={g} value={g} label={catName(g)} />
          ))}
        </datalist>
        <select className="input" aria-label={t("cat.kind")} value={kind} onChange={(e) => setKind(e.target.value)}>
          <option value="expense">{t("cf.spending")}</option>
          <option value="income">{t("cf.income")}</option>
          <option value="transfer">{t("cat.transfer")}</option>
        </select>
        <button className="btn sm" disabled={!name.trim() || !group.trim()} onClick={add}>
          {t("cat.add")}
        </button>
      </div>
    </Modal>
    {dialog}
    </>
  );
}

// --- salary ------------------------------------------------------------------------------

// Everything that decides "free to spend until payday": which month salary counts for, and what stays untouched.
function SalaryCard({ v, set }: { v: SettingsValues; set: <K extends keyof SettingsValues>(key: K, value: SettingsValues[K]) => Promise<void> }) {
  const toast = useToast();
  const enabled = v.payday_shift;
  const { data, setData } = useApi<Paydays>("/paydays", [enabled]);
  async function setMode(p: Payday, mode: Payday["mode"]) {
    try {
      setData(await api.patch<Paydays>("/paydays", { key: p.key, mode }));
      window.dispatchEvent(new Event("groschen:synced"));
    } catch (e) {
      toast((e as Error).message);
    }
  }
  return (
    <Card title={t("set.salary")} id="salary">
      <Row title={t("pay.toggle")} sub={t("pay.toggle.sub")}>
        <Switch label={t("pay.toggle")} checked={enabled} onChange={(x) => set("payday_shift", x)} />
      </Row>
      {enabled &&
        (data?.sources ?? []).map((p) => (
          <Row key={p.key} title={p.name} sub={`${t("pay.source", { day: p.usual_day, amount: eur(p.amount), moved: p.moved, count: p.count })} · ${t("pay.autoIs", { mode: t(`pay.auto.${p.auto}`) })}`}>
            <Seg<Payday["mode"]>
              label={t("pay.monthFor", { name: p.name })}
              value={p.mode}
              onChange={(m) => setMode(p, m)}
              options={[
                ["auto", t("pay.autoShort")],
                ["next", t("pay.next")],
                ["same", t("pay.same")],
              ]}
            />
          </Row>
        ))}
      {enabled && data && !data.sources.length && <p className="txsum">{t("pay.none", { amount: eurPublic(300) })}</p>}
      <Row title={t("set.hints.buffer")} sub={t("set.hints.bufferSub")}>
        <NumberSetting value={v.safe_buffer} onSave={(x) => set("safe_buffer", x)} label={t("set.hints.bufferLabel")} unit="€" step={50} min={0} max={1000000} />
      </Row>
    </Card>
  );
}

// --- password -----------------------------------------------------------------------------

function PasswordChange({ onClose }: { onClose: () => void }) {
  const toast = useToast();
  useT();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [error, setError] = useState<string | null>(null);
  async function save() {
    try {
      await api.post("/me/password", { current, new: next });
      toast(t("pw.changed"));
      onClose();
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <Modal
      title={t("pw.change")}
      onClose={onClose}
      actions={
        <button className="btn primary" disabled={!current || next.length < 8} onClick={save}>
          {t("pw.change")}
        </button>
      }
    >
      <div className="field">
        <label htmlFor="pw-cur">{t("pw.current")}</label>
        <input className="input" id="pw-cur" type="password" autoComplete="current-password" value={current} onChange={(e) => setCurrent(e.target.value)} />
      </div>
      <div className="field">
        <label htmlFor="pw-new">{t("pw.new")}</label>
        <input className="input" id="pw-new" type="password" autoComplete="new-password" value={next} onChange={(e) => setNext(e.target.value)} />
        <span className="hint">{t("pw.hint")}</span>
      </div>
      {error && <p className="err">{error}</p>}
    </Modal>
  );
}

function EasterEggs() {
  const found = useFoundEggs();
  const [on, setOn] = useState(eggsOn);
  const names = EGGS.filter((e) => found.includes(e.id)).map((e) => eggName(e.id));
  const next = EGGS.find((e) => !found.includes(e.id));
  return (
    <Row
      title={t("egg.title")}
      sub={
        on
          ? `${found.length ? t("egg.found", { n: found.length, total: EGGS.length, names: names.join(", ") }) : t("egg.none", { total: EGGS.length })} ${next ? t("egg.hint", { hint: eggHint(next.id) }) : t("egg.all")}`
          : t("egg.off")
      }
    >
      <span className="hstack">
        {on && found.length > 0 && (
          <button className="btn sm" onClick={resetFound}>
            {t("egg.hide")}
          </button>
        )}
        <Switch
          label={t("egg.title")}
          checked={on}
          onChange={(x) => {
            setEggsOn(x);
            setOn(x);
          }}
        />
      </span>
    </Row>
  );
}

// --- page ------------------------------------------------------------------------------------

type Tab = "bank" | "categories" | "hints" | "depot" | "backup" | "privacy" | "security" | "account";
const TABS: [Tab, Key][] = [
  ["bank", "set.tab.bank"],
  ["categories", "set.tab.categories"],
  ["hints", "set.tab.hints"],
  ["depot", "set.tab.depot"],
  ["backup", "set.tab.backup"],
  ["privacy", "set.tab.privacy"],
  ["security", "set.tab.security"],
  ["account", "set.tab.account"],
];
// Old links (bookmarks, the Investments page, the reminder banner) land on the tab that now holds them.
const OLD_HASH: Record<string, Tab> = { groups: "categories", salary: "hints", investments: "depot", network: "privacy", look: "account" };
const tabFromHash = (hash: string): Tab => {
  const h = hash.replace(/^#/, "");
  return TABS.some(([k]) => k === h) ? (h as Tab) : OLD_HASH[h] ?? "bank";
};

export default function Settings() {
  const { connections, status, refresh, groups, logout } = useApp();
  useT();
  const toast = useToast();
  const cats = useCategories();
  const { data, error, reload, setData } = useApi<SettingsInfo>("/settings");
  const [modal, setModal] = useState<null | "cats" | "password" | "log">(null);
  const [tab, setTab] = useState<Tab>(() => tabFromHash(location.hash));
  const [motion, setMotion] = useState<MotionPref>(motionPref);
  const [rerunning, setRerunning] = useState(false);

  useEffect(() => {
    const on = () => setTab(tabFromHash(location.hash));
    window.addEventListener("hashchange", on);
    window.addEventListener("groschen:navigate", on);
    return () => {
      window.removeEventListener("hashchange", on);
      window.removeEventListener("groschen:navigate", on);
    };
  }, []);
  // An old address such as #groups is rewritten to its new tab so the link in the bar is the one to share.
  useEffect(() => {
    if (location.hash.slice(1) !== tab) redirect(`/settings#${tab}`);
  }, [tab]);

  const header = <PageHeader title={t("nav.settings")} />;
  if (!data) return <>{header}{error ? <ErrorNote error={error} /> : <Loading />}</>;
  const v = data.values;

  async function set<K extends keyof SettingsValues>(key: K, value: SettingsValues[K]) {
    setData((d) => (d ? { ...d, values: { ...d.values, [key]: value } } : d));
    try {
      await api.patch("/settings", { [key]: value });
      refresh();
      // The price server joins or leaves the allowed hosts, and the first fetch starts.
      if (key === "online_prices") {
        reload();
        if (value) setTimeout(reload, 8000);
      }
    } catch (e) {
      toast((e as Error).message);
      reload();
    }
  }

  async function restoreHints() {
    try {
      const r = await api.del<{ restored: number }>("/alerts/dismissed");
      toast(r.restored ? t("set.hints.restored", { n: r.restored }) : t("set.hints.noneDismissed"));
      refresh();
    } catch (e) {
      toast((e as Error).message);
    }
  }

  async function rerun() {
    setRerunning(true);
    const r = await api.post<{ categorized: number }>("/categorize/rerun");
    setRerunning(false);
    toast(t("smart.rerunDone", { n: r.categorized }));
    window.dispatchEvent(new Event("groschen:synced"));
    refresh();
  }

  const net = data.network;
  const auto = data.learning.recent ? Math.round((data.learning.recent_auto / data.learning.recent) * 100) : null;

  const panels: Record<Tab, ReactNode> = {
    bank: (
      <>
        <Card title={t("set.banks")} right={!connections.length && <button className="btn sm primary" onClick={() => openDialog({ kind: "connect" })}>{t("shell.connectIng")}</button>}>
          {connections.map((c) => (
            <ConnectionCard key={c.id} c={c} reminder={v.reminder_days} />
          ))}
          {!connections.length && <p className="txsum">{t("set.noBank")}</p>}
          <Row title={t("set.schedule")} sub={data.next_runs.sync ? t("set.nextSync", { when: whenNext(data.next_runs.sync) }) : t("set.schedule.sub")}>
            <select className="pill" aria-label={t("set.schedule")} value={v.sync_schedule} onChange={(e) => set("sync_schedule", e.target.value as SettingsValues["sync_schedule"])}>
              <option value="daily">{t("sched.daily")}</option>
              <option value="twice">{t("sched.twiceShort")}</option>
              <option value="6h">{t("sched.6h")}</option>
            </select>
          </Row>
          <Row title={t("set.reminder")} sub={t("set.reminder.sub")}>
            <Seg
              label={t("set.reminder")}
              value={String(v.reminder_days)}
              onChange={(x) => set("reminder_days", Number(x))}
              options={[30, 15, 7].map((n) => [String(n), t("remind.before", { n })])}
            />
          </Row>
        </Card>
        <CsvImport />
      </>
    ),
    categories: (
      <>
        <Card title={t("set.autoCat")} right={<span className="tag good">{t("smart.offline")}</span>}>
          <Row title={t("wz.categorizer")} sub={data.model.label}>
            <Seg<SettingsValues["categorizer"]>
              label={t("wz.categorizer")}
              value={v.categorizer}
              onChange={(x) => set("categorizer", x)}
              options={[
                ["model", t("smart.model")],
                ["rules", t("wz.rules")],
              ]}
            />
          </Row>
          <Row
            title={t("smart.doing")}
            sub={`${auto === null ? t("smart.noRecent") : t("smart.auto", { p: auto })} · ${t("smart.learned", { corrections: data.learning.corrections, merchants: data.learning.memory })}`}
          >
            <button className="btn sm" onClick={rerun} disabled={rerunning}>
              {rerunning && <Spinner />}
              {t("smart.rerun")}
            </button>
          </Row>
          <Row title={t("smart.review")} sub={t("smart.review.sub")}>
            <Switch label={t("smart.review.label")} checked={v.review_uncertain} onChange={(x) => set("review_uncertain", x)} />
          </Row>
          <OwnNames
            names={v.holder_names ?? []}
            onChange={(names) => void set("holder_names", names).then(() => window.dispatchEvent(new Event("groschen:synced")))}
          />
        </Card>
        <Card title={t("set.catsRules")} right={<button className="btn sm" onClick={() => setModal("cats")}><Icon name="pencil" size={14} />{t("set.editCats")}</button>}>
          <Rules cats={cats} />
        </Card>
        <Card title={t("learn.title")} sub={t("learn.sub")}>
          <LearnedMerchants />
        </Card>
        <Card title={t("nav.groups")} id="groups" sub={t("grp.explain")} right={<button className="btn sm" onClick={() => openDialog({ kind: "group", group: null })}><Icon name="plus" size={15} />{t("nav.newGroup")}</button>}>
          {groups.map((g) => (
            <Row key={g.id} title={g.name} sub={cats.filter((c) => g.category_ids.includes(c.id)).map((c) => catName(c.name)).join(", ")}>
              <button className="btn sm" onClick={() => openDialog({ kind: "group", group: g })}>
                <Icon name="pencil" size={14} />
                {t("set.edit")}
              </button>
            </Row>
          ))}
        </Card>
      </>
    ),
    hints: (
      <>
        <Card title={t("set.hints")} sub={t("set.hints.intro")}>
          <Row title={t("set.hints.dup")} sub={t("set.hints.dupSub")}>
            <Switch label={t("set.hints.dup")} checked={v.alert_duplicates} onChange={(x) => set("alert_duplicates", x)} />
          </Row>
          <Row title={t("set.hints.price")} sub={t("set.hints.priceSub")}>
            <Switch label={t("set.hints.price")} checked={v.alert_price_up} onChange={(x) => set("alert_price_up", x)} />
          </Row>
          <Row title={t("set.hints.subs")} sub={t("set.hints.subsSub")}>
            <Switch label={t("set.hints.subs")} checked={v.alert_subscriptions} onChange={(x) => set("alert_subscriptions", x)} />
          </Row>
          <Row title={t("set.hints.unusual")} sub={t("set.hints.unusualSub")}>
            <Switch label={t("set.hints.unusual")} checked={v.alert_unusual} onChange={(x) => set("alert_unusual", x)} />
          </Row>
          <Row title={t("pref.unusual")} sub={t("set.hints.expensiveSub")}>
            <Switch label={t("pref.unusual")} checked={v.unusual_alerts} onChange={(x) => set("unusual_alerts", x)} />
          </Row>
          <Row title={t("set.hints.large")} sub={t("set.hints.largeSub")}>
            <NumberSetting value={v.alert_large} onSave={(x) => set("alert_large", x)} label={t("set.hints.largeLabel")} unit="€" step={50} min={0} max={100000} />
          </Row>
          <Row title={t("set.hints.dismissed")} sub={t("set.hints.dismissedSub")}>
            <button className="btn sm" onClick={restoreHints}>
              {t("set.hints.restore")}
            </button>
          </Row>
        </Card>
        <SalaryCard v={v} set={set} />
      </>
    ),
    depot: (
      <Card title={t("nav.investments")} id="depot" sub={t("set.depot.sub")}>
        <Row title={t("set.rate")} sub={t("set.rate.sub")}>
          <NumberSetting value={v.risk_free_rate} onSave={(x) => set("risk_free_rate", x)} label={t("set.rate.label")} unit="%" step={0.05} min={-5} max={20} width={80} />
        </Row>
        <Row title={t("set.allowance")} sub={t("set.allowance.sub", { single: eurPublic(1000, 0), couple: eurPublic(2000, 0) })}>
          <NumberSetting value={v.tax_allowance} onSave={(x) => set("tax_allowance", x)} label={t("set.allowance.label")} unit="€" step={100} min={0} max={10000} />
        </Row>
        <Row title={t("set.online")} sub={t("set.online.sub", { host: data.market.host })}>
          <Switch label={t("set.online")} checked={v.online_prices} onChange={(x) => set("online_prices", x)} />
        </Row>
        {v.online_prices && (
          <Row
            title={t("set.online.status")}
            sub={
              data.market.last
                ? t("set.online.last", { when: relTime(data.market.last), n: data.market.funds.filter((f) => !f.error).length, all: data.market.funds.length })
                : t("set.online.never")
            }
          >
            <button
              className="btn sm"
              onClick={async () => {
                try {
                  await api.post("/market/refresh");
                  toast(t("fund.refreshing"));
                  setTimeout(reload, 6000);
                } catch (e) {
                  toast((e as Error).message);
                }
              }}
            >
              <Icon name="refresh" size={15} />
              {t("fund.refresh")}
            </button>
          </Row>
        )}
        {v.online_prices && data.market.funds.some((f) => f.error) && (
          <p className="txsum">
            {data.market.funds
              .filter((f) => f.error)
              .map((f) => t("set.online.failed", { isin: f.isin, error: f.error ?? "" }))
              .join(" · ")}
          </p>
        )}
      </Card>
    ),
    backup: (
      <>
        <Backups values={v} backups={data.backups} nextRun={data.next_runs.backup} reload={reload} />
      </>
    ),
    privacy: (
      <>
        <Card title={t("bk.title")}>
          <Row title={t("bk.export")} sub={t("bk.export.sub")}>
            <a className="btn sm" href={`/api/export/transactions.csv?lang=${getLang()}`} download>
              <Icon name="download" size={15} />
              {t("bk.exportBtn")}
            </a>
          </Row>
          <p className="txsum">{t("bk.note")}</p>
        </Card>
        <Card title={t("net.title")} id="network">
          <Row
            title={t("net.internet")}
            sub={
              v.online_prices
                ? t("net.internet.subPrices", { hosts: data.network.allowed_hosts.filter((h) => h !== data.market.host).join(", ") || t("net.yourBank"), prices: data.market.host })
                : t("net.internet.sub", { hosts: data.network.allowed_hosts.join(", ") || t("net.yourBank") })
            }
          >
            <span className="tag good">{v.online_prices ? t("net.bankAndPrices") : t("net.bankOnly")}</span>
          </Row>
          <Row
            title={t("net.log")}
            sub={
              net.count
                ? t("net.logged", { days: net.days, n: net.count, hosts: net.hosts.join(", ") || t("net.nobody") }) +
                  (net.blocked.length ? t("net.blocked", { hosts: net.blocked.join(", ") }) : "")
                : t("net.none", { days: net.days })
            }
          >
            <button className="btn sm" onClick={() => setModal("log")} disabled={!net.entries.length}>
              {t("net.showLog")}
            </button>
          </Row>
          <p className="txsum">
            {t("net.updates.sub")} {t("net.fonts.sub")}
          </p>
        </Card>
      </>
    ),
    security: <SecuritySettings values={v} set={set} onChanged={reload} />,
    account: (
      <>
        <Card title={t("set.account")}>
          <Row title={status.user?.name ?? t("look.you")} sub={t("look.username", { name: status.user?.username ?? "" })}>
            <button className="btn sm" onClick={() => setModal("password")}>
              {t("pw.change")}
            </button>
          </Row>
          <Row title={t("nav.logout")} sub={t("set.logout.sub")}>
            <button className="btn sm" onClick={logout}>
              <Icon name="logout" size={15} />
              {t("nav.logout")}
            </button>
          </Row>
        </Card>
        <Card title={t("set.look")}>
          <Row title={t("common.language")} sub={t("look.language.sub")}>
            <LangPicker onPick={(l) => set("language", l)} />
          </Row>
          <Row title={t("look.motion")} sub={t(`look.motion.${motion}.sub`)}>
            <Seg<MotionPref>
              label={t("look.motion")}
              value={motion}
              onChange={(m) => {
                setMotion(m);
                setMotionPref(m);
              }}
              options={[
                ["full", t("look.motion.full")],
                ["calm", t("look.motion.calm")],
                ["off", t("look.motion.off")],
              ]}
            />
          </Row>
          <EasterEggs />
          <Row title={t("look.version")} sub={`Groschen ${data.version}`} />
        </Card>
      </>
    ),
  };

  return (
    <>
      {header}
      <Tabs<Tab> label={t("nav.settings")} ids="set" value={tab} onChange={setTab} options={TABS.map(([k, label]) => [k, t(label)])} />
      <div className="stack tabpanel setpanel" role="tabpanel" id={`set-panel-${tab}`} aria-labelledby={`set-tab-${tab}`} key={tab}>
        {panels[tab]}
      </div>

      {modal === "cats" && (
        <CategoryEditor
          onClose={() => {
            setModal(null);
            window.dispatchEvent(new Event("groschen:synced"));
          }}
        />
      )}
      {modal === "password" && <PasswordChange onClose={() => setModal(null)} />}
      {modal === "log" && (
        <Modal title={t("net.log")} onClose={() => setModal(null)}>
          <p className="muted small">{t("net.log.sub")}</p>
          <div className="netlog">
            {net.entries.map((e, i) => (
              <div key={i}>
                <span>{relTime(e.ts)}</span>
                <span>{e.host}</span>
                <span className={e.allowed ? "pos" : "neg"}>{e.allowed ? e.purpose || t("net.allowed") : t("net.blockedWord")}</span>
              </div>
            ))}
          </div>
        </Modal>
      )}
    </>
  );
}
