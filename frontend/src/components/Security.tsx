import { useState, type ReactNode } from "react";
import { Icon } from "./Icons";
import { Card, Modal, NumberSetting, Switch, useApi, useConfirm, useToast } from "./UI";
import { t, useT } from "../i18n";
import { api } from "../lib/api";
import { dateShort, relTime } from "../lib/format";
import { addPasskey, cancelled, passkeyBlocker } from "../lib/passkey";
import type { LoginEvent, LoginSession, Passkey, SettingsValues } from "../lib/types";

type Set = <K extends keyof SettingsValues>(key: K, value: SettingsValues[K]) => Promise<void>;

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

// "Firefox on Windows" from a browser's user-agent text, good enough to tell devices apart.
export function deviceName(agent: string | null) {
  const a = agent ?? "";
  const browser = /Edg\//.test(a)
    ? "Edge"
    : /OPR\//.test(a)
      ? "Opera"
      : /Firefox\//.test(a)
        ? "Firefox"
        : /Chrome\//.test(a)
          ? "Chrome"
          : /Safari\//.test(a)
            ? "Safari"
            : null;
  const os = /iPhone/.test(a)
    ? "iPhone"
    : /iPad/.test(a)
      ? "iPad"
      : /Android/.test(a)
        ? "Android"
        : /Mac OS X|Macintosh/.test(a)
          ? "Mac"
          : /Windows/.test(a)
            ? "Windows"
            : /Linux/.test(a)
              ? "Linux"
              : null;
  if (browser && os) return t("sec.device", { browser, os });
  return browser ?? os ?? t("sec.unknownDevice");
}

function Passkeys({ values, data, reload, onChanged }: { values: SettingsValues; data: Passkey[] | null; reload: () => void; onChanged: () => void }) {
  const toast = useToast();
  const { confirm, dialog } = useConfirm();
  const [busy, setBusy] = useState(false);
  const [renaming, setRenaming] = useState<Passkey | null>(null);
  const blocker = passkeyBlocker();
  const here = location.hostname;

  async function add() {
    setBusy(true);
    try {
      await addPasskey();
      toast(t("sec.pk.added"));
      reload();
    } catch (e) {
      if (!cancelled(e)) toast((e as Error).message);
    }
    setBusy(false);
  }

  async function remove(p: Passkey) {
    const last = (data?.length ?? 0) === 1;
    const ok = await confirm({
      title: t("sec.pk.deleteTitle", { name: p.name }),
      text: last && !values.password_login ? t("sec.pk.deleteLastText") : t("sec.pk.deleteText"),
      action: t("common.delete"),
    });
    if (!ok) return;
    try {
      const r = await api.del<{ password_login: boolean }>(`/passkeys/${p.id}`);
      if (r.password_login) {
        toast(t("sec.pk.passwordBack"));
        onChanged();
      }
      reload();
    } catch (e) {
      toast((e as Error).message);
    }
  }

  return (
    <Card
      title={t("sec.pk.title")}
      sub={t("sec.pk.sub")}
      right={
        !blocker && (
          <button className="btn sm primary" onClick={add} disabled={busy}>
            <Icon name="plus" size={14} />
            {t("sec.pk.add")}
          </button>
        )
      }
    >
      {blocker && (
        <div className="sec-note">
          <Icon name="lock" size={16} />
          <div>
            <b>{t(`sec.pk.why.${blocker}`, { host: here })}</b>
            <p>{t("sec.pk.how")}</p>
          </div>
        </div>
      )}
      {data?.map((p) => (
        <Row
          key={p.id}
          title={p.name}
          sub={`${t("sec.pk.created", { date: dateShort(p.created_at) })} · ${p.last_used_at ? t("sec.pk.used", { when: relTime(p.last_used_at) }) : t("sec.pk.unused")}${p.rp_id !== here ? ` · ${t("sec.pk.for", { host: p.rp_id })}` : ""}`}
        >
          <span className="hstack">
            <button className="ib" aria-label={t("sec.pk.rename")} title={t("sec.pk.rename")} onClick={() => setRenaming(p)}>
              <Icon name="pencil" size={15} />
            </button>
            <button className="ib" aria-label={t("common.delete")} title={t("common.delete")} onClick={() => remove(p)}>
              <Icon name="trash" size={15} />
            </button>
          </span>
        </Row>
      ))}
      {data && !data.length && !blocker && <p className="muted small sec-empty">{t("sec.pk.none")}</p>}
      {renaming && <Rename passkey={renaming} onClose={() => setRenaming(null)} onSaved={reload} />}
      {dialog}
    </Card>
  );
}

function Rename({ passkey, onClose, onSaved }: { passkey: Passkey; onClose: () => void; onSaved: () => void }) {
  const [name, setName] = useState(passkey.name);
  const [error, setError] = useState<string | null>(null);
  async function save() {
    try {
      await api.patch(`/passkeys/${passkey.id}`, { name: name.trim() });
      onSaved();
      onClose();
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <Modal
      title={t("sec.pk.rename")}
      onClose={onClose}
      actions={
        <button className="btn primary" disabled={!name.trim()} onClick={save}>
          {t("common.save")}
        </button>
      }
    >
      <div className="field">
        <label htmlFor="pk-name">{t("sec.pk.name")}</label>
        <input
          className="input"
          id="pk-name"
          autoFocus
          maxLength={60}
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && name.trim() && save()}
        />
      </div>
      {error && <p className="err">{error}</p>}
    </Modal>
  );
}

function Sessions() {
  const toast = useToast();
  const { data, reload } = useApi<LoginSession[]>("/sessions");
  const [history, setHistory] = useState(false);
  const others = (data ?? []).filter((s) => !s.current).length;

  async function end(s: LoginSession) {
    await api.del(`/sessions/${s.id}`);
    toast(t("sec.s.ended"));
    reload();
  }
  async function endOthers() {
    const r = await api.post<{ ended: number }>("/sessions/others");
    toast(t("sec.s.endedOthers", { n: r.ended }));
    reload();
  }

  return (
    <Card
      title={t("sec.s.title")}
      sub={t("sec.s.sub")}
      right={
        others > 0 && (
          <button className="btn sm" onClick={endOthers}>
            <Icon name="logout" size={14} />
            {t("sec.s.endOthers")}
          </button>
        )
      }
    >
      {data?.map((s) => (
        <Row
          key={s.id}
          title={
            <>
              {deviceName(s.agent)}
              {s.current && <span className="tag good sec-tag">{t("sec.s.this")}</span>}
            </>
          }
          sub={[s.ip, t("sec.s.seen", { when: relTime(s.last_seen) }), t(`sec.via.${s.method}`)].filter(Boolean).join(" · ")}
        >
          {!s.current && (
            <button className="btn sm ghost" onClick={() => end(s)}>
              {t("sec.s.end")}
            </button>
          )}
        </Row>
      ))}
      <Row title={t("sec.log.title")} sub={t("sec.log.sub")}>
        <button className="btn sm" onClick={() => setHistory(true)}>
          {t("sec.log.show")}
        </button>
      </Row>
      {history && <History onClose={() => setHistory(false)} />}
    </Card>
  );
}

function History({ onClose }: { onClose: () => void }) {
  const { data } = useApi<LoginEvent[]>("/logins");
  return (
    <Modal title={t("sec.log.title")} onClose={onClose} wide>
      {data && !data.length && <p className="muted small">{t("sec.log.none")}</p>}
      <div className="sec-log">
        {data?.map((e, i) => (
          <div className="sec-log-row" key={i}>
            <span className={`sec-dot ${e.ok ? "ok" : "bad"}`}>
              <Icon name={e.ok ? "check" : "x"} size={12} />
            </span>
            <div>
              <b>{e.ok ? t(`sec.log.ok.${e.method}`) : t(`sec.log.bad.${e.method}`, { name: e.username ?? "?" })}</b>
              <small>{[relTime(e.at), deviceName(e.agent), e.ip].filter(Boolean).join(" · ")}</small>
            </div>
          </div>
        ))}
      </div>
    </Modal>
  );
}

export function SecuritySettings({ values, set, onChanged }: { values: SettingsValues; set: Set; onChanged: () => void }) {
  useT();
  const { data, reload } = useApi<Passkey[]>("/passkeys");
  const hasPasskey = !!data?.length;
  return (
    <>
      <Passkeys values={values} data={data} reload={reload} onChanged={onChanged} />
      <Card title={t("sec.login.title")}>
        <Row title={t("sec.pw.title")} sub={hasPasskey ? t(values.password_login ? "sec.pw.on" : "sec.pw.off") : t("sec.pw.needsPasskey")}>
          {hasPasskey && <Switch checked={values.password_login} onChange={(v) => set("password_login", v)} label={t("sec.pw.title")} />}
        </Row>
        <Row title={t("sec.days.title")} sub={t("sec.days.sub")}>
          <NumberSetting value={values.session_days} onSave={(v) => set("session_days", v)} label={t("sec.days.title")} unit={t("sec.unit.days")} step={1} min={1} max={365} width={76} />
        </Row>
        <Row title={t("sec.idle.title")} sub={values.idle_minutes ? t("sec.idle.on", { n: values.idle_minutes }) : t("sec.idle.off")}>
          <NumberSetting value={values.idle_minutes} onSave={(v) => set("idle_minutes", v)} label={t("sec.idle.title")} unit={t("sec.unit.min")} step={5} min={0} max={1440} width={76} />
        </Row>
        <Row title={t("sec.lock.title")} sub={t("sec.lock.sub", { n: values.login_max_failures, m: values.login_lock_minutes })}>
          <span className="hstack sec-lock">
            <NumberSetting value={values.login_max_failures} onSave={(v) => set("login_max_failures", v)} label={t("sec.lock.tries")} unit={t("sec.unit.tries")} step={1} min={3} max={100} width={64} />
            <NumberSetting value={values.login_lock_minutes} onSave={(v) => set("login_lock_minutes", v)} label={t("sec.lock.wait")} unit={t("sec.unit.min")} step={5} min={1} max={1440} width={64} />
          </span>
        </Row>
      </Card>
      <Sessions />
    </>
  );
}
