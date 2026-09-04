const RAW_API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim() ?? "";

export function normalizeApiBaseUrl(value: string | undefined): string {
  const raw = value?.trim() ?? "";
  if (!raw) return "";

  let parsed: URL;
  try {
    parsed = new URL(raw);
  } catch {
    throw new Error("invalid_api_base_url");
  }

  if (!["http:", "https:"].includes(parsed.protocol)) {
    throw new Error("invalid_api_base_url_protocol");
  }
  if (parsed.username || parsed.password) {
    throw new Error("api_base_url_credentials_forbidden");
  }
  if (parsed.search || parsed.hash) {
    throw new Error("api_base_url_query_or_hash_forbidden");
  }

  const pathname = parsed.pathname.replace(/\/+$/, "");
  return `${parsed.origin}${pathname}`;
}

export const API_BASE_URL = normalizeApiBaseUrl(RAW_API_BASE_URL);

export function resolveApiUrl(path: string, baseUrl: string): string {
  if (!path.startsWith("/")) {
    throw new Error("api_path_must_be_absolute");
  }
  return baseUrl ? `${baseUrl}${path}` : path;
}

export function apiUrl(path: string): string {
  return resolveApiUrl(path, API_BASE_URL);
}
