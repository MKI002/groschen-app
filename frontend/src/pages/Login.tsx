import { useEffect, useState, type FormEvent } from "react";
import { Icon, Logo } from "../components/Icons";
import { LangPicker } from "../components/LangPicker";
import { Spinner } from "../components/UI";
import { useT } from "../i18n";
import { api } from "../lib/api";
import { cancelled, loginWithPasskey, passkeysPossible } from "../lib/passkey";
import type { Status } from "../lib/types";

export default function Login({ onLoggedIn }: { onLoggedIn: () => void }) {
  const t = useT();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<null | "password" | "passkey">(null);
  const [status, setStatus] = useState<Pick<Status, "passkeys" | "password_login"> | null>(null);

  useEffect(() => {
    api.get<Status>("/status").then(setStatus, () => setStatus(null));
  }, []);

  const passkey = passkeysPossible() && !!status?.passkeys;
  const passwordOn = status?.password_login !== false;

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy("password");
    setError(null);
    try {
      await api.post("/login", { username, password });
      onLoggedIn();
    } catch (err) {
      setError((err as Error).message);
      setBusy(null);
    }
  }

  async function withPasskey() {
    setBusy("passkey");
    setError(null);
    try {
      await loginWithPasskey();
      onLoggedIn();
    } catch (err) {
      if (!cancelled(err)) setError((err as Error).message);
      setBusy(null);
    }
  }

  return (
    <div className="center-screen">
      <form className="login" onSubmit={submit}>
        <div className="brand">
          <Logo />
          Groschen
        </div>
        <h2>{t("login.title")}</h2>
        {passkey && (
          <button type="button" className="btn primary" onClick={withPasskey} disabled={!!busy} style={{ justifyContent: "center" }}>
            {busy === "passkey" ? <Spinner /> : <Icon name="lock" size={15} />}
            {t("login.passkey")}
          </button>
        )}
        {passkey && passwordOn && <div className="login-or">{t("login.or")}</div>}
        {passwordOn ? (
          <>
            <div className="field">
              <label htmlFor="login-user">{t("login.username")}</label>
              <input className="input" id="login-user" autoComplete="username webauthn" autoFocus={!passkey} value={username} onChange={(e) => setUsername(e.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="login-pass">{t("login.password")}</label>
              <input className="input" id="login-pass" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
          </>
        ) : (
          !passkey && <p className="muted small">{t("login.passwordOff")}</p>
        )}
        {error && <p className="err" role="alert">{error}</p>}
        {passwordOn && (
          <button className={passkey ? "btn" : "btn primary"} type="submit" disabled={!!busy || !username || !password} style={{ justifyContent: "center" }}>
            {busy === "password" && <Spinner />}
            {t("login.submit")}
          </button>
        )}
        <LangPicker />
      </form>
    </div>
  );
}
