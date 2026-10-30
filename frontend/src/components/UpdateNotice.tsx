// After a container update, a tab that stayed open keeps running the old interface until it
// reloads. It asks the server now and then which build it serves, and offers a reload once
// that is a newer one.

import { useEffect, useState } from "react";
import { t, useT } from "../i18n";
import { api } from "../lib/api";
import { Icon } from "./Icons";

const EVERY = 10 * 60 * 1000;

// The hashed name of this page's own script; the dev server has none.
function ownBuild() {
  return document.querySelector<HTMLScriptElement>('script[type="module"][src^="/assets/"]')?.getAttribute("src") ?? "";
}

export function UpdateNotice() {
  useT();
  const [stale, setStale] = useState(false);
  useEffect(() => {
    const mine = ownBuild();
    if (!mine || stale) return;
    let last = Date.now();
    const check = async () => {
      if (document.hidden) return;
      last = Date.now();
      try {
        const { build } = await api.get<{ build?: string }>("/health");
        if (build && build !== mine) setStale(true);
      } catch {
        /* restarting or unreachable: the next check tries again */
      }
    };
    const back = () => {
      if (!document.hidden && Date.now() - last > 60_000) void check();
    };
    const timer = window.setInterval(check, EVERY);
    document.addEventListener("visibilitychange", back);
    window.addEventListener("focus", back);
    return () => {
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", back);
      window.removeEventListener("focus", back);
    };
  }, [stale]);
  if (!stale) return null;
  return (
    <div className="update-note" role="status">
      <Icon name="refresh" size={16} />
      <span>{t("update.ready")}</span>
      <button className="btn sm primary" onClick={() => location.reload()}>
        {t("update.reload")}
      </button>
    </div>
  );
}
