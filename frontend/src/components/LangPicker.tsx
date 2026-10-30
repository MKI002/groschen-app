import { LANGUAGES, setLang, useLang, useT, type Lang } from "../i18n";
import { Icon } from "./Icons";

// A small language switch. `onPick` lets the caller also save the choice on the server.
export function LangPicker({ onPick, className }: { onPick?: (lang: Lang) => void; className?: string }) {
  const lang = useLang();
  const t = useT();
  return (
    <label className={`langpick ${className ?? ""}`}>
      <Icon name="globe" size={16} />
      <select
        aria-label={t("common.language")}
        value={lang}
        onChange={(e) => {
          const l = e.target.value as Lang;
          setLang(l);
          onPick?.(l);
        }}
      >
        {(Object.keys(LANGUAGES) as Lang[]).map((l) => (
          <option key={l} value={l}>
            {LANGUAGES[l].name}
          </option>
        ))}
      </select>
    </label>
  );
}
