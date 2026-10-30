import { useEffect, useState, type ReactNode } from "react";
import { t, useT } from "../i18n";
import type { BankAccount } from "../lib/types";
import { Icon } from "./Icons";
import { Dropdown, useApi } from "./UI";

// The search, sort, account and amount filters, shared by Transactions and the detail pages
// so the same filter looks and works the same everywhere.

export type Sort = "date" | "amount" | "merchant";
type Order = "new" | "old" | "big" | "name";
const ORDERS: Record<Order, [Sort, boolean]> = { new: ["date", true], old: ["date", false], big: ["amount", true], name: ["merchant", false] };

// Commas are what people type for cents here.
const euros = (s: string) => {
  const v = Number(s.replace(/\./g, "").replace(",", "."));
  return s.trim() && isFinite(v) && v >= 0 ? v : undefined;
};

export function useTxFilters(initialQ = "") {
  const [q, setQ] = useState(initialQ);
  const [query, setQuery] = useState(initialQ);
  const [account, setAccount] = useState("");
  const [minText, setMinText] = useState("");
  const [maxText, setMaxText] = useState("");
  const [range, setRange] = useState<{ min?: number; max?: number }>({});
  const [sort, setSort] = useState<Sort>("date");
  const [desc, setDesc] = useState(true);

  // Typing waits a moment before asking the server, so the numbers don't flicker on every key.
  useEffect(() => {
    const timer = window.setTimeout(() => {
      setQuery(q);
      setRange({ min: euros(minText), max: euros(maxText) });
    }, 300);
    return () => window.clearTimeout(timer);
  }, [q, minText, maxText]);

  const order: Order = sort === "date" ? (desc ? "new" : "old") : sort === "amount" ? "big" : "name";
  function setOrder(o: Order) {
    const [s, d] = ORDERS[o];
    setSort(s);
    setDesc(d);
  }
  function reset() {
    setQ("");
    setAccount("");
    setMinText("");
    setMaxText("");
  }
  const filtered = !!(query || account || range.min !== undefined || range.max !== undefined);
  return { q, setQ, query, account, setAccount, minText, setMinText, maxText, setMaxText, range, sort, desc, order, setOrder, reset, filtered };
}

export type TxFilters = ReturnType<typeof useTxFilters>;

// The query parameters the server understands for these filters.
export function filterQuery(f: TxFilters) {
  return { q: f.query, account_id: f.account, min: f.range.min, max: f.range.max, sort: f.sort, dir: f.desc ? "desc" : "asc" };
}

// One row: the search, whatever the page adds (its quick filters), a button for the rarer filters
// (account, amount) and the sort order. The rarer filters fold out underneath and stay open while set.
export function FilterBar({ f, placeholder, children }: { f: TxFilters; placeholder?: string; children?: ReactNode }) {
  useT();
  const accounts = useApi<BankAccount[]>("/accounts");
  const extra = Number(!!f.account) + Number(!!(f.minText || f.maxText));
  const [open, setOpen] = useState(extra > 0);
  const list = (accounts.data ?? []).filter((a) => a.kind !== "depot");
  return (
    <div className="fbar">
      <div className="fbar-row">
        <label className="search">
          <Icon name="search" size={16} />
          <input placeholder={placeholder ?? t("tx.search")} aria-label={t("tx.searchLabel")} value={f.q} onChange={(e) => f.setQ(e.target.value)} />
          {f.q && (
            <button type="button" className="ib sm" aria-label={t("tx.clearSearch")} onClick={() => f.setQ("")}>
              <Icon name="x" size={13} />
            </button>
          )}
        </label>
        {children}
        <span className="fbar-end">
          <button type="button" className={`btn ghost sm${open || extra ? " on" : ""}`} aria-expanded={open} onClick={() => setOpen(!open)}>
            <Icon name="filter" size={15} />
            {t("tx.filters")}
            {extra > 0 && <span className="n">{extra}</span>}
          </button>
          <Dropdown<Order>
            label={t("tx.sort")}
            icon="sort"
            value={f.order}
            onChange={f.setOrder}
            options={[
              ["new", t("tx.sort.new")],
              ["old", t("tx.sort.old")],
              ["big", t("tx.sort.big")],
              ["name", t("tx.sort.name")],
            ]}
          />
        </span>
      </div>
      {open && (
        <div className="fbar-more">
          {list.length > 1 && (
            <Dropdown<string>
              label={t("tx.account")}
              icon="bank"
              value={f.account}
              onChange={f.setAccount}
              options={[["", t("tx.allAccounts")], ...list.map((a): [string, string] => [String(a.id), a.name])]}
            />
          )}
          <div className="amtrange" role="group" aria-label={t("tx.amountRange")}>
            <span className="muted">{t("tx.amountFrom")}</span>
            <input className="input money-in" inputMode="decimal" placeholder="0" aria-label={t("dd.min.label")} value={f.minText} onChange={(e) => f.setMinText(e.target.value)} />
            <span className="muted">{t("tx.amountTo")}</span>
            <input className="input money-in" inputMode="decimal" placeholder="∞" aria-label={t("dd.max.label")} value={f.maxText} onChange={(e) => f.setMaxText(e.target.value)} />
            <span className="muted">€</span>
          </div>
          {f.filtered && (
            <button type="button" className="linkbtn" onClick={f.reset}>
              {t("dd.clearFilters")}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
