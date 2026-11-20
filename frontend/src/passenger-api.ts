export type PassengerSession = {
  id: string;
  display_name: string;
  login_identifier: string;
  contact_verified?: boolean;
  expires_at: string;
};

type Credentials = { login_identifier: string; password: string };
type Registration = Credentials & { display_name: string };

const configuredBase = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
const API_ROOT = configuredBase ? `${configuredBase}/api/v1` : window.location.origin === "https://appassets.androidplatform.net" ? "" : "/api/v1";

function csrfToken(): string | undefined {
  const entry = document.cookie.split("; ").find((part) => part.startsWith("mnm_passenger_csrf="));
  return entry ? decodeURIComponent(entry.slice("mnm_passenger_csrf=".length)) : undefined;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (!API_ROOT) throw new Error("Passenger account service is not configured for this app build.");
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (init.method && !["GET", "HEAD", "OPTIONS"].includes(init.method.toUpperCase())) {
    const csrf = csrfToken();
    if (csrf) headers.set("X-CSRF-Token", csrf);
  }
  const response = await fetch(`${API_ROOT}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });
  if (!response.ok) {
    let message = "The account service could not complete this request.";
    try {
      const payload = await response.json() as { detail?: string };
      if (payload.detail) message = payload.detail;
    } catch {
      // Keep the safe generic error when the response is not JSON.
    }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return await response.json() as T;
}

export function registerPassenger(payload: Registration): Promise<PassengerSession> {
  return request("/passenger/auth/register", { method: "POST", body: JSON.stringify(payload) });
}

export function loginPassenger(payload: Credentials): Promise<PassengerSession> {
  return request("/passenger/auth/sessions", { method: "POST", body: JSON.stringify(payload) });
}

export function getCurrentPassenger(): Promise<PassengerSession> {
  return request("/passenger/auth/sessions/current");
}

export function updatePassengerProfile(display_name: string): Promise<PassengerSession> {
  return request("/passenger/auth/profile", { method: "PATCH", body: JSON.stringify({ display_name }) });
}

export function logoutPassenger(): Promise<void> {
  return request("/passenger/auth/sessions/current", { method: "DELETE" });
}
