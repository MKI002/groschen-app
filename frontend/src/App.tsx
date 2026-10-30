import { useCallback, useEffect, useState } from "react";
import { api, setUnauthorizedHandler } from "./lib/api";
import { AppProvider } from "./lib/app";
import type { Status } from "./lib/types";
import Login from "./pages/Login";
import Shell from "./pages/Shell";
import Splash from "./pages/Splash";
import Wizard from "./pages/Wizard";

type Phase = "splash" | "wizard" | "login" | "app";

export default function App() {
  const [status, setStatus] = useState<Status | null>(null);
  const [phase, setPhase] = useState<Phase>("splash");
  const [splashDone, setSplashDone] = useState(false);

  const route = useCallback((s: Status) => {
    setStatus(s);
    if (!s.has_user) setPhase("wizard");
    else if (!s.user) setPhase("login");
    else if (!s.setup_complete) setPhase("wizard");
    else setPhase("app");
  }, []);

  const reloadStatus = useCallback(() => api.get<Status>("/status").then(route), [route]);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setStatus((s) => (s ? { ...s, user: null } : s));
      setPhase((p) => (p === "app" ? "login" : p));
    });
  }, []);

  if (!splashDone || !status) {
    return (
      <Splash
        load={() => api.get<Status>("/status")}
        onDone={(s) => {
          route(s);
          setSplashDone(true);
        }}
      />
    );
  }

  if (phase === "login") return <Login onLoggedIn={reloadStatus} />;
  if (phase === "wizard") return <Wizard status={status} onFinished={reloadStatus} />;
  return (
    <AppProvider status={status} onLogout={() => setPhase("login")}>
      <Shell />
    </AppProvider>
  );
}
