/// <reference types="vite/client" />

const configuredBase = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
const API_ROOT = configuredBase ? `${configuredBase}/api/v1` : window.location.origin === "https://appassets.androidplatform.net" ? "" : "/api/v1";

function csrfToken(): string | undefined {
  const entry = document.cookie.split("; ").find((part) => part.startsWith("mnm_csrf="));
  return entry ? decodeURIComponent(entry.slice("mnm_csrf=".length)) : undefined;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (!API_ROOT) throw new Error("Staff account service is not configured for this app build.");
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (init.method && !["GET", "HEAD", "OPTIONS"].includes(init.method.toUpperCase())) {
    const csrf = csrfToken();
    if (csrf) headers.set("X-CSRF-Token", csrf);
  }
  const response = await fetch(`${API_ROOT}${path}`, { ...init, headers, credentials: "include" });
  if (!response.ok) {
    let message = "The staff service could not complete this request.";
    try { const payload = await response.json() as { detail?: string }; if (payload.detail) message = payload.detail; } catch { /* safe generic error */ }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return await response.json() as T;
}

export type StaffRole = {
  assignment_id?: string; id?: string; role_code?: string; code?: string;
  role_description?: string; description?: string; organization_id?: string | null;
  scope?: "platform" | "organization"; permissions?: string[]; assigned_at?: string;
};
export type StaffSession = {
  id: string; display_name: string; login_identifier: string; expires_at: string;
  roles: StaffRole[]; permissions: string[];
};
export type StaffDashboard = {
  staff: { id: string; display_name: string; login_identifier: string };
  roles: StaffRole[]; permissions: string[];
  modules: Array<{ key: string; label: string }>;
  scope: "platform" | "organization"; stats: Record<string, number>;
  safety_boundaries: {
    synthetic_data_only: boolean; real_money_enabled: boolean;
    ticketing_enabled: boolean; boarding_authorized: boolean;
    production_operations_enabled: boolean;
  };
};
export type SchedulerStatus = {
  job_name: string; health: "not_configured" | "healthy" | "degraded" | "stale";
  worker_enabled_by_default: boolean; worker_mode: string;
  backlog: { due_holds: number; oldest_due_at: string | null; oldest_due_age_seconds: number };
  lease: null | {
    owner_id: string; lease_expires_at: string; heartbeat_at: string;
    heartbeat_age_seconds: number; last_success_at: string | null;
    last_failure_at: string | null; last_error_code: string | null;
    consecutive_failures: number; batches_completed: number;
    records_processed: number; last_duration_ms: number | null;
  };
  runs: Array<{ id: string; worker_id: string; status: string; started_at: string;
    finished_at: string | null; records_processed: number; duration_ms: number | null; error_code: string | null }>;
  runtime: { app_env: string; synthetic_data_only: boolean; scheduler_enabled: boolean;
    remote_database_allowed: boolean; production_operations_enabled: boolean };
};
export type StaffRoleDefinition = { id: string; code: string; description: string; scope: "platform" | "organization"; permissions: string[] };
export type StaffUser = { id: string; display_name: string; login_identifier: string; status: string; roles: StaffRole[] };
export type AuditItem = { id: string; event_type: string; occurred_at: string; actor_type: string; actor_id: string | null; resource_type: string; resource_id: string | null; action: string; outcome: string; reason_code: string | null; metadata: Record<string, unknown> };

export function staffLogin(login_identifier: string, password: string): Promise<StaffSession> {
  return request("/auth/sessions", { method: "POST", body: JSON.stringify({ login_identifier, password }) });
}
export function getStaffSession(): Promise<StaffSession> { return request("/auth/sessions/current"); }
export function staffLogout(): Promise<void> { return request("/auth/sessions/current", { method: "DELETE" }); }
export function getStaffDashboard(): Promise<StaffDashboard> { return request("/admin/dashboard"); }
export function getSchedulerStatus(): Promise<SchedulerStatus> { return request("/admin/operations/scheduler"); }
export function runSchedulerOnce(): Promise<{ status: string; records_processed?: number; duration_ms?: number }> {
  return request("/admin/operations/scheduler/run-once", { method: "POST" });
}
export function getStaffRoles(): Promise<{ items: StaffRoleDefinition[] }> { return request("/admin/access/roles"); }
export function getStaffUsers(): Promise<{ items: StaffUser[] }> { return request("/admin/access/users"); }
export function assignStaffRole(userId: string, role_code: string, organization_id: string | null): Promise<unknown> {
  return request(`/admin/access/users/${encodeURIComponent(userId)}/roles`, {
    method: "POST", body: JSON.stringify({ role_code, organization_id }),
  });
}
export function revokeStaffRole(assignmentId: string): Promise<{ revoked: boolean }> {
  return request(`/admin/access/role-assignments/${encodeURIComponent(assignmentId)}`, { method: "DELETE" });
}
export function getStaffAudit(): Promise<AuditItem[]> { return request("/audit/events?limit=30"); }

export type StaffOrganization = { id: string; display_name: string; status: string };
export type StaffInvitation = { id: string; organization_id: string; organization_name: string;
  login_identifier: string; display_name: string; role_code: string; created_at: string; expires_at: string };
export function getStaffOrganizations(): Promise<{ items: StaffOrganization[] }> { return request("/admin/access/organizations"); }
export function getStaffInvitations(): Promise<{ items: StaffInvitation[] }> { return request("/admin/access/invitations"); }
export function createStaffInvitation(organizationId: string, input: {
  login_identifier: string; display_name: string; role_code: string;
}): Promise<{ invitation_id: string; login_identifier: string; expires_at: string;
  delivery: string; synthetic_invitation_token: string }> {
  return request(`/operators/${encodeURIComponent(organizationId)}/invitations`, {
    method: "POST", body: JSON.stringify(input),
  });
}
export function revokeStaffInvitation(organizationId: string, invitationId: string): Promise<{ revoked: boolean }> {
  return request(`/operators/${encodeURIComponent(organizationId)}/invitations/${encodeURIComponent(invitationId)}/revoke`, { method: "POST" });
}
