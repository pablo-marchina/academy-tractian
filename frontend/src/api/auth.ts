export type AccessTokenProvider = () => string | null | Promise<string | null>;

let accessTokenProvider: AccessTokenProvider | null = null;

export function setAccessTokenProvider(provider: AccessTokenProvider | null): void {
  accessTokenProvider = provider;
}

export function clearAccessTokenProvider(): void {
  accessTokenProvider = null;
}

function validateBearerToken(value: string): string {
  const token = value.trim();
  if (!token || token !== value || token.length > 16_384) {
    throw new Error("invalid_access_token");
  }
  if (/\s/.test(token)) {
    throw new Error("invalid_access_token");
  }
  try {
    if (new TextEncoder().encode(token).length !== token.length) {
      throw new Error("invalid_access_token");
    }
  } catch {
    throw new Error("invalid_access_token");
  }
  return token;
}

export async function authorizationHeaders(): Promise<Record<string, string>> {
  if (accessTokenProvider === null) return {};
  const supplied = await accessTokenProvider();
  if (supplied === null) return {};
  if (typeof supplied !== "string") throw new Error("invalid_access_token");
  return { Authorization: `Bearer ${validateBearerToken(supplied)}` };
}
