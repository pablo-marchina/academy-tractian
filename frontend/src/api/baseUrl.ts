const RAW_API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim() ?? "";

const LOCAL_HOST_ALIASES = new Set([
  "localhost",
  "localhost.localdomain",
  "host.docker.internal",
  "gateway.docker.internal",
  "kubernetes.docker.internal",
]);

function isLocalHostname(hostname: string): boolean {
  const normalized = hostname
    .replace(/^\[/, "")
    .replace(/\]$/, "")
    .replace(/\.$/, "")
    .toLowerCase();
  if (LOCAL_HOST_ALIASES.has(normalized) || normalized.endsWith(".localhost")) return true;
  if (normalized === "::" || normalized === "::1" || normalized === "0.0.0.0") return true;
  const ipv4 = normalized.split(".").map((part) => Number(part));
  return ipv4.length === 4 && ipv4.every(Number.isInteger) && ipv4[0] === 127;
}

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

export function normalizeHostedApiBaseUrl(value: string | undefined): string {
  const normalized = normalizeApiBaseUrl(value);
  if (!normalized) return "";

  const parsed = new URL(normalized);
  if (parsed.protocol !== "https:") {
    throw new Error("hosted_api_base_url_https_required");
  }
  if (isLocalHostname(parsed.hostname)) {
    throw new Error("hosted_api_base_url_local_forbidden");
  }
  return normalized;
}

export const API_BASE_URL = import.meta.env.PROD
  ? normalizeHostedApiBaseUrl(RAW_API_BASE_URL)
  : normalizeApiBaseUrl(RAW_API_BASE_URL);

export function resolveApiUrl(path: string, baseUrl: string): string {
  if (!path.startsWith("/")) {
    throw new Error("api_path_must_be_absolute");
  }
  return baseUrl ? `${baseUrl}${path}` : path;
}

export function apiUrl(path: string): string {
  return resolveApiUrl(path, API_BASE_URL);
}
