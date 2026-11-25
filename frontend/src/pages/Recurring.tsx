import { useEffect } from "react";
import { useNarrow } from "../components/Charts";
import { Seg } from "../components/UI";
import { useT } from "../i18n";
import { redirect, useSearch } from "../lib/router";
import Calendar from "./Calendar";
import { PageHeader } from "./Shell";
import Subscriptions, { SubscriptionOrbit } from "./Subscriptions";

type View = "list" | "calendar" | "orbit";

// Fixed costs: everything that comes back regularly, as a list (with what changed and the yes/no
// questions), a month calendar, or an orbit. The view is kept in the address, so a reload or a
// link opens the same one.
export default function Recurring() {
  const t = useT();
  const asked = useSearch().get("view");
  // On a phone the orbit is too small to read or tap, so it isn't offered there; an orbit link opens the list.
  const phone = useNarrow("(max-width: 820px)");
  const view: View = asked === "calendar" || (asked === "orbit" && !phone) ? asked : "list";
  const switcher = (
    <Seg<View>
      label={t("rec.view")}
      value={view}
      onChange={(v) => redirect(v === "list" ? "/recurring" : `/recurring?view=${v}`)}
      options={[
        ["list", t("rec.list")],
        ["calendar", t("rec.calendar")],
        ...(phone ? [] : [["orbit", t("rec.orbit")] as [View, string]]),
      ]}
    />
  );
  return (
    <>
      <PageHeader title={t("rec.title")} actions={switcher} />
      {view === "calendar" ? <Calendar /> : view === "orbit" ? <SubscriptionOrbit /> : <Subscriptions />}
    </>
  );
}

// The old Subscriptions and Fixed costs addresses open the matching view.
export function OldAddress({ to }: { to: string }) {
  // Deferred: on first load this runs before the shell starts listening for address changes.
  useEffect(() => {
    const id = window.setTimeout(() => redirect(to), 0);
    return () => window.clearTimeout(id);
  }, [to]);
  return null;
}
