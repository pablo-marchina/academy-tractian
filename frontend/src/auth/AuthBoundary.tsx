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
    const payload = (await response.json()) as { message?: unknown; error?: { message?: unknown } | string };
    if (typeof payload.message === "string" && payload.message.trim()) return payload.message;
    if (typeof payload.error === "string" && payload.error.trim()) return payload.error;
    if (payload.error && typeof payload.error === "object" && typeof payload.error.message === "string" && payload.error.message.trim()) {
      return payload.error.message;
    }
  } catch {
    // Keep a status-only technical detail when the identity service returns no public JSON.
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
  const [showPassword, setShowPassword] = useState(false);
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

  const changeMode = (next: AuthMode) => {
    setMode(next);
    setError(null);
    setPassword("");
    setShowPassword(false);
  };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submitting || state === "unavailable") return;
    const normalizedEmail = email.trim().toLowerCase();
    const normalizedName = name.trim();
    if (!normalizedEmail || password.length < 8 || (mode === "sign-up" && !normalizedName)) return;

    setSubmitting(true);
    setError(null);
    try {
      const response = await authRequest(mode === "sign-in" ? "/sign-in/email" : "/sign-up/email", {
        method: "POST",
        body: JSON.stringify(mode === "sign-in"
          ? { email: normalizedEmail, password, rememberMe: true }
          : { email: normalizedEmail, password, name: normalizedName }),
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
    return (
      <div className="auth-shell" aria-live="polite" aria-busy="true">
        <div className="auth-card">
          <p className="eyebrow">ACADEMY × TRACTIAN</p>
          <h1>Opening your workspace…</h1>
          <p className="auth-copy">We are checking your secure session. You do not need to do anything.</p>
        </div>
      </div>
    );
  }

  if (state === "anonymous" || state === "unavailable") {
    return (
      <div className="auth-shell">
        <section className="auth-card" aria-labelledby="auth-heading">
          <p className="eyebrow">ACADEMY × TRACTIAN</p>
          <h1 id="auth-heading">Equipment analysis assistant</h1>
          <p className="auth-copy">Sign in to see analyses for your organization and start a new equipment investigation.</p>

          {state === "unavailable" ? (
            <div className="error-banner friendly-error auth-recovery" role="alert">
              <strong>Sign-in is temporarily unavailable.</strong>
              <span>Your organization’s data remains protected. Try the secure session check again before entering credentials.</span>
              <button type="button" className="ghost-button" onClick={() => { setState("checking"); void refreshSession(); }}>Try again</button>
              {error && <details><summary>Technical detail</summary><code>{error}</code></details>}
            </div>
          ) : (
            <>
              <div className="auth-mode" role="group" aria-label="Choose sign in or account creation">
                <button type="button" aria-pressed={mode === "sign-in"} className={mode === "sign-in" ? "active" : ""} onClick={() => changeMode("sign-in")}>Sign in</button>
                <button type="button" aria-pressed={mode === "sign-up"} className={mode === "sign-up" ? "active" : ""} onClick={() => changeMode("sign-up")}>Create account</button>
              </div>
              <form className="auth-form" onSubmit={submit} aria-busy={submitting}>
                {mode === "sign-up" && (
                  <label>Your name
                    <input value={name} onChange={(event) => setName(event.target.value)} autoComplete="name" maxLength={120} required />
                  </label>
                )}
                <label>Email
                  <input type="email" inputMode="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" maxLength={320} required />
                </label>
                <label>Password
                  <span className="password-field">
                    <input type={showPassword ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} autoComplete={mode === "sign-in" ? "current-password" : "new-password"} minLength={8} maxLength={128} required aria-describedby="password-help" />
                    <button type="button" className="password-toggle" aria-pressed={showPassword} onClick={() => setShowPassword((current) => !current)}>{showPassword ? "Hide" : "Show"}</button>
                  </span>
                  <small id="password-help">Use at least 8 characters. You can paste from a password manager.</small>
                </label>
                <button type="submit" disabled={submitting}>{submitting ? "Please wait…" : mode === "sign-in" ? "Sign in" : "Create account"}</button>
              </form>
              {error && (
                <div className="error-banner friendly-error" role="alert">
                  <strong>{mode === "sign-in" ? "We could not sign you in." : "We could not create the account."}</strong>
                  <span>Check the information above and try again. Your password has not been cleared so you can correct another field without retyping it.</span>
                  <details><summary>Technical detail</summary><code>{error}</code></details>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    );
  }

  return (
    <>
      <div className="auth-session-bar">
        <span><b>{user?.name}</b><small>{user?.email}</small></span>
        <button type="button" onClick={signOut} disabled={submitting}>{submitting ? "Signing out…" : "Sign out"}</button>
      </div>
      {error && (
        <div className="auth-session-error error-banner friendly-error" role="alert">
          <strong>We could not complete the account action.</strong>
          <span>Your current session is still open.</span>
          <details><summary>Technical detail</summary><code>{error}</code></details>
        </div>
      )}
      {children}
    </>
  );
}
