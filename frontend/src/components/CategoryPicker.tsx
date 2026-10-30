import { useEffect, useRef, useState } from "react";
import { catName, t, useT } from "../i18n";
import { api } from "../lib/api";
import { colorVar } from "../lib/format";
import type { Category } from "../lib/types";
import { Icon } from "./Icons";

let cache: Category[] | null = null;

export function useCategories() {
  const [cats, setCats] = useState<Category[]>(cache ?? []);
  useEffect(() => {
    if (cache) return;
    api.get<Category[]>("/categories").then((c) => {
      cache = c;
      setCats(c);
    });
  }, []);
  return cats;
}

export function forgetCategories() {
  cache = null;
}

// A category named like its group is the group's general choice ("just Subscriptions").
export const isGeneral = (c: Category) => c.name === c.group;

// For searching: lower case and without accents, so "uber" finds "Über".
const fold = (s: string) => s.toLocaleLowerCase().normalize("NFD").replace(/\p{Diacritic}/gu, "");

export function CategoryPicker({ value, onPick, amount }: { value: number | null; onPick: (id: number) => void; amount?: number }) {
  const cats = useCategories();
  useT();
  const [, setVersion] = useState(0);
  const [adding, setAdding] = useState<string | null>(null);
  const [newName, setNewName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const busy = useRef(false);
  const list = useRef<HTMLDivElement>(null);
  // The list scrolls on its own inside the dialog: open it with the chosen category in view.
  useEffect(() => {
    const el = list.current, on = el?.querySelector<HTMLElement>(".chip.on");
    if (!el || !on) return;
    const top = on.getBoundingClientRect().top - el.getBoundingClientRect().top;
    if (top > el.clientHeight - on.offsetHeight) el.scrollTop += top - el.clientHeight / 2;
  }, [cats.length]);
  const q = fold(query.trim());
  const groups = new Map<string, Category[]>();
  for (const c of cache ?? cats) {
    if (q) {
      // A search looks through every category, also those that don't fit the amount's direction.
      if (!fold(catName(c.name)).includes(q) && !fold(catName(c.group)).includes(q)) continue;
    } else {
      if (amount !== undefined && amount > 0 && c.kind === "expense" && !["Shopping", "Personal"].includes(c.group)) continue;
      if (amount !== undefined && amount < 0 && c.kind === "income") continue;
    }
    if (!groups.has(c.group)) groups.set(c.group, []);
    groups.get(c.group)!.push(c);
  }
  const first = [...groups.values()].map((list) => list.find(isGeneral) ?? list[0])[0];

  async function create(group: string, list: Category[]) {
    const name = newName.trim();
    if (!name) return setAdding(null);
    if (busy.current) return;
    busy.current = true;
    setError(null);
    try {
      const kind = (list.find(isGeneral) ?? list[0]).kind;
      const r = await api.post<{ id: number }>("/categories", { name, group, kind });
      cache = await api.get<Category[]>("/categories");
      setVersion((v) => v + 1);
      setAdding(null);
      setNewName("");
      onPick(r.id);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      busy.current = false;
    }
  }

  const chip = (c: Category, label = catName(c.name), extra = "") => (
    <button key={c.id} type="button" className={`chip ${extra} ${c.id === value ? "on" : ""}`} onClick={() => onPick(c.id)}>
      <span className="sq" style={{ background: colorVar(c.color) }} />
      {label}
    </button>
  );

  return (
    <div className="catpick-wrap">
      <label className="catpick-search">
        <Icon name="search" size={15} />
        <input
          type="search"
          placeholder={t("pick.search")}
          aria-label={t("pick.search")}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              if (q && first) onPick(first.id);
            } else if (e.key === "Escape" && query) {
              e.nativeEvent.stopPropagation(); // clear the search, keep the dialog open
              setQuery("");
            }
          }}
        />
      </label>
      <div className="catpick" ref={list}>
        {q && !first && <p className="muted small">{t("pick.none")}</p>}
        {[...groups.entries()].map(([g, list]) => {
          const general = list.find(isGeneral);
          const subs = list.filter((c) => c !== general);
          const shown = catName(g);
          return (
            <div key={g}>
              <h4>{shown}</h4>
              <div className="chips">
                {general && chip(general, subs.length ? t("pick.general", { group: shown }) : shown, "general")}
                {subs.map((c) => chip(c))}
                {q ? null : adding === g ? (
                  <input
                    className="input chip-input"
                    autoFocus
                    maxLength={40}
                    placeholder={t("pick.newSub")}
                    aria-label={t("pick.newSubIn", { group: shown })}
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        create(g, list);
                      } else if (e.key === "Escape") {
                        e.nativeEvent.stopPropagation(); // keep the dialog open
                        setAdding(null);
                      }
                    }}
                    onBlur={() => create(g, list)}
                  />
                ) : (
                  <button
                    type="button"
                    className="chip add"
                    onClick={() => {
                      setNewName("");
                      setError(null);
                      setAdding(g);
                    }}
                  >
                    {t("pick.new")}
                  </button>
                )}
              </div>
              {adding === g && error && <p className="err">{error}</p>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
