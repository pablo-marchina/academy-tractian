function normalizeBaseUrl(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) return "";
  let parsed: URL;
  try {
    parsed = new URL(trimmed);
  } catch {
    throw new Error("invalid_api_base_url");
  }
  if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
    throw new Error("invalid_api_base_url_protocol");
  }
  if (parsed.pathname !== "/" || parsed.search || parsed.hash) {
    throw new Error("api_base_url_must_be_origin_only");
  }
  return parsed.origin;
}

export const API_BASE_URL = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL ?? "");

export function resolveApiUrl(path: string): string {
  if (!path.startsWith("/")) throw new Error("api_path_must_be_relative");
  return API_BASE_URL ? `${API_BASE_URL}${path}` : path;
}

export function resolveStreamUrl(path: string, afterSequence?: number): string {
  const resolved = resolveApiUrl(path);
  const url = new URL(resolved, window.location.origin);
  if (afterSequence !== undefined) {
    url.searchParams.set("after_sequence", String(afterSequence));
  }
  if (API_BASE_URL) return url.toString();
  return `${url.pathname}${url.search}`;
}

export function normalizeApiBaseUrlForTest(value: string): string {
  return normalizeBaseUrl(value);
}
