function configuredApiBase(): string {
  const env = (import.meta as ImportMeta & { env?: { VITE_API_BASE_URL?: string } }).env;
  return env?.VITE_API_BASE_URL?.trim() ?? "";
}

export function resolveApiUrl(path: string, configured = ""): string {
  if (!path.startsWith("/api/")) {
    throw new Error("API paths must be rooted under /api/.");
  }
  if (!configured.trim()) return path;

  let base: URL;
  try {
    base = new URL(configured.trim());
  } catch {
    throw new Error("VITE_API_BASE_URL must be a valid absolute URL.");
  }

  const localHttp = base.protocol === "http:" && ["localhost", "127.0.0.1"].includes(base.hostname);
  if (base.protocol !== "https:" && !localHttp) {
    throw new Error("The configured API origin must use HTTPS.");
  }
  if (base.pathname !== "/" || base.search || base.hash || base.username || base.password) {
    throw new Error("VITE_API_BASE_URL must contain only an origin, without credentials, path, query or fragment.");
  }

  return new URL(path, base.origin).toString();
}

export function apiUrl(path: string): string {
  return resolveApiUrl(path, configuredApiBase());
}
