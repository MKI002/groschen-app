import { useEffect, useState } from "react";
import { catName, t, useT, type Key } from "../i18n";
import { api } from "../lib/api";
import { currentPath } from "../lib/router";
import { useApp } from "../lib/app";
import { colorVar } from "../lib/format";
import type { Category, Connection, UserGroup } from "../lib/types";
import { BankForm, type TestResult } from "./BankForm";
import { useCategories } from "./CategoryPicker";
import { Icon } from "./Icons";
import { Modal, useConfirm } from "./UI";

// Dialogs that more than one page opens. Any page asks for one with openDialog();
// the shell draws it, so "New group" or "Connect ING" work from wherever the button is.

type Request = { kind: "connect" } | { kind: "group"; group: UserGroup | null };

export function openDialog(req: Request) {
  window.dispatchEvent(new CustomEvent<Request>("groschen:dialog", { detail: req }));
}

export function DialogHost() {
  const [req, setReq] = useState<Request | null>(null);
  const { refresh } = useApp();
  useEffect(() => {
    const on = (e: Event) => setReq((e as CustomEvent<Request>).detail);
    window.addEventListener("groschen:dialog", on);
    return () => window.removeEventListener("groschen:dialog", on);
  }, []);
  if (!req) return null;
  if (req.kind === "connect") {
    return (
      <ConnectBank
        onDone={() => {
          setReq(null);
          refresh();
        }}
      />
    );
  }
  return <GroupEditor group={req.group} onClose={() => setReq(null)} />;
}

// "I was logged in to ING": restarts the 90-day count. Offered wherever the reminder shows.
export async function confirmBankLogin(c: Connection, toast: (m: string) => void, refresh: () => void) {
  await api.post(`/connections/${c.id}/confirm-login`);
  toast(t("set.loginConfirmed"));
  refresh();
}

function ConnectBank({ onDone }: { onDone: () => void }) {
  const [connected, setConnected] = useState<TestResult | null>(null);
  const { sync } = useApp();
  useT();
  return (
    <Modal
      title={t("shell.connectIng")}
      onClose={onDone}
      actions={
        <button
          className="btn primary"
          disabled={!connected}
          onClick={() => {
            onDone();
            sync(true);
          }}
        >
          {t("set.doneSync")}
        </button>
      }
    >
      <BankForm connected={connected} onConnected={setConnected} onAccountsChange={(accounts) => setConnected((c) => c && { ...c, accounts })} />
    </Modal>
  );
}

const GROUP_ICONS: [string, Key][] = [
  ["car", "grp.car"],
  ["home", "grp.home"],
  ["plane", "grp.travel"],
  ["tag", "grp.other"],
];

function GroupEditor({ group, onClose }: { group: UserGroup | null; onClose: () => void }) {
  const { refresh } = useApp();
  const cats = useCategories();
  const { confirm, dialog } = useConfirm();
  useT();
  const [name, setName] = useState(group?.name ?? "");
  const [icon, setIcon] = useState(group?.icon ?? "car");
  const [ids, setIds] = useState<number[]>(group?.category_ids ?? []);
  async function save() {
    const body = { name, icon, category_ids: ids };
    if (group) await api.patch(`/groups/${group.id}`, body);
    else await api.post("/groups", body);
    refresh();
    window.dispatchEvent(new Event("groschen:synced"));
    onClose();
  }
  async function remove() {
    if (!group) return;
    const ok = await confirm({ title: t("grp.deleteTitle"), text: t("grp.confirmDelete", { name: group.name }), action: t("common.delete") });
    if (!ok) return;
    await api.del(`/groups/${group.id}`);
    refresh();
    onClose();
    if (currentPath() === `/groups/${group.id}`) history.back();
  }
  const byGroup = new Map<string, Category[]>();
  for (const c of cats.filter((c) => c.kind === "expense")) {
    if (!byGroup.has(c.group)) byGroup.set(c.group, []);
    byGroup.get(c.group)!.push(c);
  }
  return (
    <>
      <Modal
        title={group ? t("grp.edit", { name: group.name }) : t("nav.newGroup")}
        onClose={onClose}
        actions={
          <>
            {group && (
              <button className="btn ghost danger" style={{ marginRight: "auto" }} onClick={remove}>
                {t("common.delete")}
              </button>
            )}
            <button className="btn ghost" onClick={onClose}>
              {t("common.cancel")}
            </button>
            <button className="btn primary" disabled={!name.trim() || !ids.length} onClick={save}>
              {t("common.save")}
            </button>
          </>
        }
      >
        <p className="muted small">{t("grp.explain")}</p>
        <div className="row2">
          <div className="field">
            <label htmlFor="gr-name">{t("nw.name")}</label>
            <input className="input" id="gr-name" value={name} onChange={(e) => setName(e.target.value)} placeholder={t("grp.car")} />
          </div>
          <div className="field">
            <span className="label">{t("grp.icon")}</span>
            <div className="seg iconseg" role="group" aria-label={t("grp.icon")}>
              {GROUP_ICONS.map(([v, l]) => (
                <button key={v} type="button" className={icon === v ? "on" : ""} aria-pressed={icon === v} aria-label={t(l)} title={t(l)} onClick={() => setIcon(v)}>
                  <Icon name={v} size={17} />
                </button>
              ))}
            </div>
          </div>
        </div>
        <div className="catpick">
          {[...byGroup.entries()].map(([g, list]) => (
            <div key={g}>
              <h4>{catName(g)}</h4>
              <div className="chips">
                {list.map((c) => {
                  const on = ids.includes(c.id);
                  return (
                    <button key={c.id} type="button" className={`chip ${on ? "on" : ""}`} aria-pressed={on} onClick={() => setIds((x) => (on ? x.filter((i) => i !== c.id) : [...x, c.id]))}>
                      <span className="sq" style={{ background: colorVar(c.color) }} />
                      {catName(c.name)}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </Modal>
      {dialog}
    </>
  );
}
