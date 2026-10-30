import { useEffect } from "react";
import { Seg } from "../components/UI";
import { useT } from "../i18n";
import { navigate, redirect, usePath, useSearch } from "../lib/router";
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
  const view: View = asked === "calendar" || asked === "orbit" ? asked : "list";
  const switcher = (
    <Seg<View>
      label={t("rec.view")}
      value={view}
      onChange={(v) => redirect(v === "list" ? "/recurring" : `/recurring?view=${v}`)}
      options={[
        ["list", t("rec.list")],
        ["calendar", t("rec.calendar")],
        ["orbit", t("rec.orbit")],
      ]}
    />
  );
  return (
    <>
      <PageHeader title={t("rec.title")} actions={switcher} />
      <SpendSwitch />
      {view === "calendar" ? <Calendar /> : view === "orbit" ? <SubscriptionOrbit /> : <Subscriptions />}
    </>
  );
}

// On a phone the bottom bar has room for Spending only; this switch at the top of both pages
// reaches fixed costs, which sit under Spending in the sidebar.
export function SpendSwitch() {
  const t = useT();
  const path = usePath();
  return (
    <div className="phone-only spend-switch">
      <Seg
        label={t("nav.spending")}
        value={path.startsWith("/recurring") ? "/recurring" : "/spending"}
        onChange={(v) => navigate(v)}
        options={[
          ["/spending", t("nav.spending")],
          ["/recurring", t("nav.recurring")],
        ]}
      />
    </div>
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
