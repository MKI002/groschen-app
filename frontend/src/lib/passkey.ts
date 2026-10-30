// Passkeys (WebAuthn) in the browser. Groschen sends the options as JSON with base64url
// strings; the browser wants bytes, and the answer goes back as base64url strings again.

import { api } from "./api";

const IP = /^(\d{1,3}(\.\d{1,3}){3}|\[[0-9a-f:.]+\])$/i;

// Browsers only allow passkeys on HTTPS with a name (http://localhost aside), never on a bare IP address.
export function passkeysPossible() {
  return typeof window !== "undefined" && window.isSecureContext && "PublicKeyCredential" in window && !IP.test(location.hostname);
}

// Why passkeys can't be used here, for the Settings page: "ip" (opened by address), "http" (no HTTPS) or "browser".
export function passkeyBlocker(): null | "ip" | "http" | "browser" {
  if (IP.test(location.hostname)) return "ip";
  if (!window.isSecureContext) return "http";
  if (!("PublicKeyCredential" in window)) return "browser";
  return null;
}

function fromB64(s: string): ArrayBuffer {
  const b = atob(s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4));
  const out = new Uint8Array(b.length);
  for (let i = 0; i < b.length; i++) out[i] = b.charCodeAt(i);
  return out.buffer;
}

function toB64(buf: ArrayBuffer | null | undefined): string | null {
  if (!buf) return null;
  const bytes = new Uint8Array(buf);
  let s = "";
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

type Descriptor = { id: string; type: "public-key"; transports?: AuthenticatorTransport[] };
type Json = Record<string, unknown>;

const descriptors = (list: unknown) => ((list as Descriptor[] | undefined) ?? []).map((d) => ({ ...d, id: fromB64(d.id) }));

function creationOptions(o: Json): PublicKeyCredentialCreationOptions {
  const user = o.user as { id: string; name: string; displayName: string };
  return {
    ...(o as unknown as PublicKeyCredentialCreationOptions),
    challenge: fromB64(o.challenge as string),
    user: { ...user, id: fromB64(user.id) },
    excludeCredentials: descriptors(o.excludeCredentials),
  };
}

function requestOptions(o: Json): PublicKeyCredentialRequestOptions {
  return {
    ...(o as unknown as PublicKeyCredentialRequestOptions),
    challenge: fromB64(o.challenge as string),
    allowCredentials: descriptors(o.allowCredentials),
  };
}

function credentialJson(c: PublicKeyCredential) {
  const response: Json = { clientDataJSON: toB64(c.response.clientDataJSON) };
  if ("attestationObject" in c.response) {
    const r = c.response as AuthenticatorAttestationResponse;
    response.attestationObject = toB64(r.attestationObject);
    response.transports = typeof r.getTransports === "function" ? r.getTransports() : [];
  } else {
    const r = c.response as AuthenticatorAssertionResponse;
    response.authenticatorData = toB64(r.authenticatorData);
    response.signature = toB64(r.signature);
    response.userHandle = toB64(r.userHandle);
  }
  return {
    id: c.id,
    rawId: toB64(c.rawId),
    type: c.type,
    response,
    authenticatorAttachment: c.authenticatorAttachment ?? undefined,
    clientExtensionResults: c.getClientExtensionResults(),
  };
}

// True when the user closed the browser's passkey dialog: not an error worth showing.
export function cancelled(e: unknown) {
  return e instanceof DOMException && (e.name === "NotAllowedError" || e.name === "AbortError");
}

export async function addPasskey(name = "") {
  const start = await api.post<{ challenge_id: string; options: Json }>("/passkeys/options");
  const cred = (await navigator.credentials.create({ publicKey: creationOptions(start.options) })) as PublicKeyCredential | null;
  if (!cred) throw new DOMException("cancelled", "AbortError");
  return api.post("/passkeys", { challenge_id: start.challenge_id, credential: credentialJson(cred), name });
}

export async function loginWithPasskey() {
  const start = await api.post<{ challenge_id: string; options: Json }>("/login/passkey/options");
  const cred = (await navigator.credentials.get({ publicKey: requestOptions(start.options) })) as PublicKeyCredential | null;
  if (!cred) throw new DOMException("cancelled", "AbortError");
  return api.post("/login/passkey", { challenge_id: start.challenge_id, credential: credentialJson(cred) });
}
