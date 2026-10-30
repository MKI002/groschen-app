import { useState } from "react";
import { t as tr, useT } from "../i18n";
import { api } from "../lib/api";
import { dayMonth, eur } from "../lib/format";
import type { SavedDest, SavedGroup, SavedItem, SavedTo } from "../lib/types";
import { Icon } from "./Icons";
import { Modal, useToast } from "./UI";

// Where the saved money went: invested (savings plan with Kleingeld Plus, single ETF purchases),
// put aside (the savings account, other own accounts), or still on the account. The Overview shows
// only those three; the window behind them has the finer split. Groschen finds it by comparing the
// accounts with each other; every booking can be moved to another destination with one click.

export const DESTS: SavedDest[] = ["plan", "etf", "savings", "other", "stays"];
const INVEST = new Set<SavedDest>(["plan", "etf"]);
const SHOWN = 8;

export const destColor: Record<SavedDest, string> = {
  plan: "var(--accent)",
  etf: "var(--accent-ink)",
  savings: "var(--c-teal)",
  other: "var(--c-blue)",
  stays: "var(--c-gray)",
};

export const groupColor: Record<SavedGroup, string> = {
  invested: "var(--accent)",
  aside: "var(--c-teal)",
  stays: "var(--c-gray)",
};

export type GroupPart = { key: SavedGroup; amount: number; focus: SavedDest };

// The three Overview destinations, each opening the window on its largest part.
export function savedGroups(data: SavedTo): GroupPart[] {
  const out: GroupPart[] = [];
  for (const key of ["invested", "aside", "stays"] as SavedGroup[]) {
    const parts = data.parts.filter((p) => p.group === key);
    if (!parts.length) continue;
    const amount = parts.reduce((a, p) => a + p.amount, 0);
    if (Math.abs(amount) < 0.005) continue;
    const focus = [...parts].sort((a, b) => Math.abs(b.amount) - Math.abs(a.amount))[0].key;
    out.push({ key, amount, focus });
  }
  return out;
}

export function groupName(key: SavedGroup, amount: number) {
  return amount < 0 ? (key === "stays" ? tr("chart.fromSavings") : tr(`sv.gfrom.${key}`)) : tr(`sv.g.${key}`);
}

export function destName(key: SavedDest, account?: string | null) {
  if (key === "savings" && account) return account;
  return tr(`sv.d.${key}`);
}

// The name for money that came out of a destination instead of going in (sold ETFs, taken from savings).
export function destFromName(key: SavedDest, account?: string | null) {
  if (key === "stays") return tr("chart.fromSavings");
  return tr("sv.from", { name: destName(key, account) });
}

// A slim bar with one segment per Overview destination; nothing to read, just the proportions.
export function SavedBar({ data, onOpen }: { data: SavedTo; onOpen: () => void }) {
  const t = useT();
  const groups = savedGroups(data);
  const pos = groups.filter((g) => g.amount > 0);
  const total = pos.reduce((a, p) => a + p.amount, 0);
  const invested = groups.find((g) => g.key === "invested")?.amount ?? 0;
  const stays = groups.find((g) => g.key === "stays")?.amount ?? 0;
  const line =
    invested > 0.5 && stays > 0.5
      ? t("sv.tile", { etf: eur(invested), stays: eur(stays) })
      : invested > 0.5
        ? t("sv.tile.etf", { etf: eur(invested) })
        : stays > 0.5 && pos.length === 1
          ? t("sv.tile.allStays")
          : t("sv.tile.where");
  return (
    <button type="button" className="svmini" onClick={onOpen} aria-label={t("sv.open")}>
      {total > 0 && (
        <span className="svbar" aria-hidden="true">
          {pos.map((p, i) => (
            <span key={p.key} style={{ flexGrow: p.amount, background: groupColor[p.key], ["--i" as string]: i }} />
          ))}
        </span>
      )}
      <span className="svline">
        {line}
        <span className="chev" aria-hidden="true">›</span>
      </span>
    </button>
  );
}

export function SavedToModal({ data, label, focus, onClose, onChanged }: {
  data: SavedTo; label: string; focus?: SavedDest | null; onClose: () => void; onChanged: () => void;
}) {
  const t = useT();
  const toast = useToast();
  const parts = data.parts;
  const first = parts.find((p) => p.key !== "stays" && p.count > 0)?.key ?? parts[0]?.key ?? "stays";
  const [sel, setSel] = useState<SavedDest>(focus && parts.some((p) => p.key === focus) ? focus : first);
  const [busy, setBusy] = useState<number | null>(null);
  const [all, setAll] = useState(false);
  const pos = parts.filter((p) => p.amount > 0);
  const total = pos.reduce((a, p) => a + p.amount, 0);
  const items = data.items.filter((i) => i.dest === sel);
  const shown = all ? items : items.slice(0, SHOWN);
  const account = parts.find((p) => p.key === "savings")?.account;

  async function move(item: SavedItem, dest: SavedDest | null) {
    setBusy(item.id);
    try {
      await api.put(`/savings/${item.id}`, { dest, learn: true });
      toast(
        dest === null
          ? t("sv.reset")
          : item.learnable
            ? t("sv.moved.learn", { dest: destName(dest, account), name: item.name })
            : t("sv.moved", { dest: destName(dest, account) }),
      );
      // The Investments page follows these choices too.
      window.dispatchEvent(new Event("groschen:synced"));
      onChanged();
    } catch (e) {
      toast((e as Error).message);
    }
    setBusy(null);
  }

  return (
    <Modal title={t("sv.title")} onClose={onClose} wide>
      <p className="muted sv-intro">
        {t("sv.intro", { period: label, amount: eur(data.saved) })} {t("sv.how")}
      </p>
      {total > 0 && (
        <div className="svbar big" role="group" aria-label={t("sv.title")}>
          {pos.map((p, i) => (
            <button
              key={p.key}
              type="button"
              className={sel === p.key ? "on" : ""}
              style={{ flexGrow: p.amount, background: destColor[p.key], ["--i" as string]: i }}
              title={`${destName(p.key, p.account)} ${eur(p.amount)}`}
              aria-label={`${destName(p.key, p.account)} ${eur(p.amount)}`}
              onClick={() => {
                setSel(p.key);
                setAll(false);
              }}
            />
          ))}
        </div>
      )}
      <div className="svlegend">
        {parts.map((p) => (
          <button key={p.key} type="button" className={`svchip${sel === p.key ? " on" : ""}`} aria-pressed={sel === p.key} onClick={() => {
                setSel(p.key);
                setAll(false);
              }}>
            <span className="sq" style={{ background: destColor[p.key] }} />
            <span className="nm">{p.amount < 0 ? destFromName(p.key, p.account) : destName(p.key, p.account)}</span>
            <b>{eur(Math.abs(p.amount))}</b>
          </button>
        ))}
      </div>
      <div className="svlist">
        {sel === "stays" && <p className="muted sv-note">{(parts.find((p) => p.key === "stays")?.amount ?? 0) < 0 ? t("sv.stays.neg") : t("sv.stays.text")}</p>}
        {!items.length && sel !== "stays" && <p className="muted sv-note">{t("sv.none")}</p>}
        {items.length > 0 && (
          <ul>
            {shown.map((i) => (
              <li key={i.id}>
                <span className="sv-date">{dayMonth(i.date)}</span>
                <span className="sv-what">
                  <span className="sv-name">
                    <span className="sv-nm">{i.name}</span>
                    <span className={`tag sv-how ${i.how}`} title={t(`sv.how.${i.how}.title`)}>
                      {i.how === "mirror" && <Icon name="repeat" size={11} />}
                      {t(`sv.how.${i.how}`)}
                    </span>
                  </span>
                  <span className="sv-route muted">
                    {i.from}
                    {" → "}
                    {i.to ?? (INVEST.has(i.dest) ? t("sv.depot") : i.name)}
                  </span>
                </span>
                <span className="sv-amt">{eur(i.amount)}</span>
                <span className="sv-move">
                  <select
                    className="pill"
                    value={i.dest}
                    disabled={busy === i.id}
                    aria-label={t("sv.change", { name: i.name })}
                    onChange={(e) => move(i, e.target.value as SavedDest)}
                  >
                    {DESTS.map((d) => (
                      <option key={d} value={d}>
                        {destName(d, account)}
                      </option>
                    ))}
                  </select>
                  {(i.how === "user" || i.how === "learned") && (
                    <button type="button" className="ib" title={t("sv.undo", { dest: destName(i.auto, account) })} aria-label={t("sv.undo", { dest: destName(i.auto, account) })} disabled={busy === i.id} onClick={() => move(i, null)}>
                      <Icon name="rewind" size={14} />
                    </button>
                  )}
                </span>
              </li>
            ))}
          </ul>
        )}
        {items.length > SHOWN && (
          <button type="button" className="linkbtn sv-more" onClick={() => setAll(!all)}>
            {all ? t("sv.fewer") : t("sv.all", { n: items.length })}
          </button>
        )}
      </div>
    </Modal>
  );
}
