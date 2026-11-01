import { useRef, useState } from "react";
import { getLang, useT, type Key } from "../i18n";
import { api, ApiError } from "../lib/api";
import { homeCurrency } from "../lib/format";
import { CURRENCIES, currencyName } from "../lib/regions";
import { Modal } from "./UI";

export type ImportResult = { account_id: number; account_name: string; imported: number; skipped: number; first: string | null; last: string | null; file: string };

// A bank file Groschen couldn't read alone: its first rows, for the user to say which column is which.
type Preview = { delimiter: string; header_row: number; columns: string[]; sample: string[][]; width: number };
type Role = "" | "date" | "amount" | "debit" | "credit" | "counterparty" | "purpose" | "currency" | "balance";
const ROLES: [Role, Key][] = [
  ["", "map.none"],
  ["date", "map.date"],
  ["amount", "map.amount"],
  ["debit", "map.debit"],
  ["credit", "map.credit"],
  ["counterparty", "map.counterparty"],
  ["purpose", "map.purpose"],
  ["currency", "map.currency"],
  ["balance", "map.balance"],
];

const DATE = /^\s*(\d{1,4}[./-]\d{1,2}[./-]\d{1,4}|\d{8})\b/;
const MONEY = /^\s*[-+(]?\s*[^\d\s]{0,3}\s*-?\d[\d.,' ]*\d?\s*[^\d\s]{0,3}\)?-?\s*$/;

// A first guess, so most files need one click: the first date column, the first column of sums, and
// the column with the longest texts as the payee.
function guess(p: Preview): Role[] {
  const roles: Role[] = Array(p.width).fill("");
  const col = (i: number) => p.sample.map((r) => r[i] ?? "").filter(Boolean);
  const all = (i: number, re: RegExp) => col(i).length > 0 && col(i).every((c) => re.test(c));
  const date = [...roles.keys()].find((i) => all(i, DATE));
  if (date !== undefined) roles[date] = "date";
  const amount = [...roles.keys()].find((i) => !roles[i] && all(i, MONEY) && col(i).some((c) => /[.,]\d{1,2}\)?-?\s*$/.test(c)));
  if (amount !== undefined) roles[amount] = "amount";
  const text = [...roles.keys()]
    .filter((i) => !roles[i] && col(i).some((c) => /[A-Za-z]{3}/.test(c)))
    .sort((a, b) => col(b).join("").length - col(a).join("").length)[0];
  if (text !== undefined) roles[text] = "counterparty";
  return roles;
}

function ColumnPicker({ file, preview, onPick, onCancel }: { file: string; preview: Preview; onPick: (mapping: Record<string, unknown>) => void; onCancel: () => void }) {
  const t = useT();
  const [roles, setRoles] = useState<Role[]>(() => guess(preview));
  const [currency, setCurrency] = useState(homeCurrency());
  const has = (r: Role) => roles.includes(r);
  const ready = has("date") && (has("amount") || has("debit") || has("credit"));
  function pick(i: number, role: Role) {
    // A role belongs to one column: picking it again moves it.
    setRoles((rs) => rs.map((r, j) => (j === i ? role : role && r === role ? "" : r)));
  }
  function done() {
    const mapping: Record<string, unknown> = {};
    roles.forEach((r, i) => r && (mapping[r] = i));
    if (!has("currency")) mapping.currency_code = currency;
    onPick(mapping);
  }
  return (
    <Modal
      wide
      title={t("map.title")}
      onClose={onCancel}
      actions={
        <>
          <button className="btn ghost" onClick={onCancel}>
            {t("common.cancel")}
          </button>
          <button className="btn primary" disabled={!ready} onClick={done}>
            {t("map.import")}
          </button>
        </>
      }
    >
      <p className="muted">{t("map.sub", { file })}</p>
      <div className="colpick" role="group" aria-label={t("map.title")}>
        <table>
          <thead>
            <tr>
              {roles.map((r, i) => (
                <th key={i}>
                  <select className={`pill${r ? " on" : ""}`} aria-label={t("map.column", { n: i + 1, name: preview.columns[i] || "" })} value={r} onChange={(e) => pick(i, e.target.value as Role)}>
                    {ROLES.map(([role, label]) => (
                      <option key={role} value={role}>
                        {t(label)}
                      </option>
                    ))}
                  </select>
                  {preview.columns[i] && <small>{preview.columns[i]}</small>}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {preview.sample.map((row, n) => (
              <tr key={n}>
                {roles.map((r, i) => (
                  <td key={i} className={r ? "on" : ""}>
                    {row[i]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!has("currency") && (
        <label className="field">
          <span className="label">{t("map.currencyOf")}</span>
          <select className="input" value={currency} onChange={(e) => setCurrency(e.target.value)}>
            {CURRENCIES.map((c) => (
              <option key={c} value={c}>
                {c} · {currencyName(c, getLang())}
              </option>
            ))}
          </select>
        </label>
      )}
      {!ready && <p className="hint">{t("map.need")}</p>}
    </Modal>
  );
}

// Import bank files one after another. A file Groschen can't read alone stops for the column
// picker; the answer is kept on the server, so the bank's next file goes through by itself.
export function useCsvImport(onDone: (r: ImportResult) => void, onError: (message: string) => void) {
  const [ask, setAsk] = useState<{ file: File; preview: Preview } | null>(null);
  const answer = useRef<((mapping: Record<string, unknown> | null) => void) | null>(null);

  async function send(file: File, mapping?: Record<string, unknown>): Promise<void> {
    const form = new FormData();
    form.append("file", file);
    if (mapping) form.append("mapping", JSON.stringify(mapping));
    try {
      onDone(await api.upload<ImportResult>("/import/csv", form));
    } catch (e) {
      const err = e as ApiError;
      const preview = (err.data as { mapping?: Preview } | null)?.mapping;
      if (err.status === 422 && preview && !mapping) {
        const picked = await new Promise<Record<string, unknown> | null>((resolve) => {
          answer.current = resolve;
          setAsk({ file, preview });
        });
        setAsk(null);
        if (picked) await send(file, picked);
        return;
      }
      onError(`${file.name}: ${err.message}`);
    }
  }

  async function importFiles(files: FileList | File[] | null) {
    for (const f of Array.from(files ?? [])) await send(f);
  }

  const dialog = ask && (
    <ColumnPicker file={ask.file.name} preview={ask.preview} onPick={(m) => answer.current?.(m)} onCancel={() => answer.current?.(null)} />
  );
  return { importFiles, dialog };
}
