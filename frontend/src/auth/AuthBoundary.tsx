import { FormEvent, ReactNode, useCallback, useEffect, useState } from "react";

type AuthMode = "sign-in" | "sign-up";
type AuthState = "checking" | "anonymous" | "authenticated" | "unavailable";

interface AuthUser {
  id: string;
  email: string;
  name: string;
}

interface AuthSessionResponse {
  user?: Partial<AuthUser> | null;
  session?: {
    id?: string;
    userId?: string;
    activeOrganizationId?: string | null;
  } | null;
}

function normalizedSession(payload: unknown): AuthUser | null {
  if (!payload || typeof payload !== "object") return null;
  const response = payload as AuthSessionResponse;
  const user = response.user;
  if (!user || typeof user.id !== "string" || typeof user.email !== "string") return null;
  return {
    id: user.id,
    email: user.email,
    name: typeof user.name === "string" && user.name.trim() ? user.name : user.email,
  };
}

async function authRequest(path: string, init?: RequestInit): Promise<Response> {
  return fetch(`/auth${path}`, {
    ...init,
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
  });
}

async function publicError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as {
      message?: unknown;
      error?: { message?: unknown } | string;
    };
    if (typeof payload.message === "string" && payload.message.trim()) return payload.message;
    if (typeof payload.error === "string" && payload.error.trim()) return payload.error;
    if (
      payload.error &&
      typeof payload.error === "object" &&
      typeof payload.error.message === "string" &&
      payload.error.message.trim()
    ) {
      return payload.error.message;
    }
  } catch {
    // Keep a status-only error when the auth service did not return public JSON.
  }
  return `${response.status} ${response.statusText}`.trim();
}

export function AuthBoundary({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>("checking");
  const [user, setUser] = useState<AuthUser | null>(null);
  const [mode, setMode] = useState<AuthMode>("sign-in");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshSession = useCallback(async () => {
    try {
      const response = await authRequest("/get-session?disableCookieCache=true");
      if (!response.ok) {
        if (response.status === 401) {
          setUser(null);
          setState("anonymous");
          return;
        }
        throw new Error(await publicError(response));
      }
      const payload = (await response.json()) as unknown;
      const nextUser = normalizedSession(payload);
      setUser(nextUser);
      setState(nextUser ? "authenticated" : "anonymous");
      setError(null);
    } catch (cause) {
      setUser(null);
      setState("unavailable");
      setError(cause instanceof Error ? cause.message : "authentication_unavailable");
    }
  }, []);

  useEffect(() => {
    void refreshSession();
  }, [refreshSession]);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submitting) return;
    const normalizedEmail = email.trim().toLowerCase();
    const normalizedName = name.trim();
    if (!normalizedEmail || password.length < 8 || (mode === "sign-up" && !normalizedName)) return;

    setSubmitting(true);
    setError(null);
    try {
      const response = await authRequest(mode === "sign-in" ? "/sign-in/email" : "/sign-up/email", {
        method: "POST",
        body: JSON.stringify(
          mode === "sign-in"
            ? { email: normalizedEmail, password, rememberMe: true }
            : { email: normalizedEmail, password, name: normalizedName },
        ),
      });
      if (!response.ok) throw new Error(await publicError(response));
      setPassword("");
      await refreshSession();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "authentication_failed");
    } finally {
      setSubmitting(false);
    }
  };

  const signOut = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const response = await authRequest("/sign-out", { method: "POST" });
      if (!response.ok) throw new Error(await publicError(response));
      setUser(null);
      setState("anonymous");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "sign_out_failed");
    } finally {
      setSubmitting(false);
    }
  };

  if (state === "checking") {
    return <div className="auth-shell"><div className="auth-card"><p className="eyebrow">ACADEMY × TRACTIAN</p><h1>Checking secure session…</h1></div></div>;
  }

  if (state === "anonymous" || state === "unavailable") {
    return (
      <div className="auth-shell">
        <section className="auth-card">
          <p className="eyebrow">ACADEMY × TRACTIAN</p>
          <h1>Industrial Agent Operations</h1>
          <p className="auth-copy">Authenticate before accessing tenant-bound runs, traces, evaluations and governed actions.</p>
          <div className="auth-mode" role="group" aria-label="Authentication mode">
            <button type="button" className={mode === "sign-in" ? "active" : ""} onClick={() => setMode("sign-in")}>Sign in</button>
            <button type="button" className={mode === "sign-up" ? "active" : ""} onClick={() => setMode("sign-up")}>Create account</button>
          </div>
          <form className="auth-form" onSubmit={submit}>
            {mode === "sign-up" && <label>Name<input value={name} onChange={(event) => setName(event.target.value)} autoComplete="name" maxLength={120} required /></label>}
            <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" maxLength={320} required /></label>
            <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete={mode === "sign-in" ? "current-password" : "new-password"} minLength={8} maxLength={128} required /></label>
            <button type="submit" disabled={submitting}>{submitting ? "Working…" : mode === "sign-in" ? "Sign in" : "Create account"}</button>
          </form>
          {error && <div className="error-banner" role="alert">{error}</div>}
          {state === "unavailable" && <p className="auth-note">The application fails closed when the managed authentication service is unavailable.</p>}
        </section>
      </div>
    );
  }

  return (
    <>
      <div className="auth-session-bar">
        <span><b>{user?.name}</b><small>{user?.email}</small></span>
        <button type="button" onClick={signOut} disabled={submitting}>Sign out</button>
      </div>
      {children}
    </>
  );
}
