const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim() ?? "";

export function normalizeApiBaseUrl(value: string, allowLocalHttp = true): string {
  const candidate = value.trim();
  if (!candidate) return "";
  let parsed: URL;
  try {
    parsed = new URL(candidate);
  } catch {
    throw new Error("VITE_API_BASE_URL must be an absolute HTTPS URL.");
  }
  const localHttp = allowLocalHttp && parsed.protocol === "http:" &&
    ["localhost", "127.0.0.1", "[::1]"].includes(parsed.hostname);
  if (parsed.protocol !== "https:" && !localHttp) {
    throw new Error("VITE_API_BASE_URL must use HTTPS (HTTP is allowed only for local development).");
  }
  if (parsed.username || parsed.password || parsed.search || parsed.hash ||
      (parsed.pathname !== "/" && parsed.pathname !== "")) {
    throw new Error("VITE_API_BASE_URL must contain only an origin, without credentials, path, query, or fragment.");
  }
  if (/YOUR-TEST-API-HOST|example\.(com|org|net)|\.invalid$/i.test(parsed.hostname)) {
    throw new Error("VITE_API_BASE_URL still contains a documentation placeholder.");
  }
  return parsed.origin;
}

export const API_BASE_URL = normalizeApiBaseUrl(rawApiBaseUrl, import.meta.env.DEV);

export function apiUrl(path: string, base = API_BASE_URL): string {
  if (!path.startsWith("/") || path.startsWith("//")) {
    throw new Error("API paths must be absolute-path references on the configured API origin.");
  }
  return `${base}${path}`;
}

export function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  return fetch(apiUrl(path), { credentials: "include", ...init });
}
