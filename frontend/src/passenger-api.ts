/// <reference types="vite/client" />

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

function csrfToken(cookieName = "mnm_passenger_csrf"): string | undefined {
  const prefix = `${cookieName}=`;
  const entry = document.cookie.split("; ").find((part) => part.startsWith(prefix));
  return entry ? decodeURIComponent(entry.slice(prefix.length)) : undefined;
}

async function request<T>(path: string, init: RequestInit = {}, csrfCookieName = "mnm_passenger_csrf"): Promise<T> {
  if (!API_ROOT) throw new Error("Passenger account service is not configured for this app build.");
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (init.method && !["GET", "HEAD", "OPTIONS"].includes(init.method.toUpperCase())) {
    const csrf = csrfToken(csrfCookieName);
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

export type PassengerLocation = {
  id: string;
  name: string;
  type: string;
};

export type PassengerTrip = {
  id: string;
  departure_at: string;
  arrival_estimate_at: string | null;
  boarding_model: string;
  available_seats: number;
  availability_as_of: string;
  fare: { amount_minor_units: number; currency_code: "ETB" };
  reservation_only: boolean;
  ticketing_enabled: boolean;
  payment_enabled: boolean;
};

export function listPassengerLocations(): Promise<PassengerLocation[]> {
  return request("/catalog/locations");
}

export function searchPassengerTrips(input: {
  origin_id: string;
  destination_id: string;
  travel_date: string;
  passenger_count: number;
}): Promise<PassengerTrip[]> {
  const query = new URLSearchParams({
    origin_id: input.origin_id,
    destination_id: input.destination_id,
    travel_date: input.travel_date,
    passenger_count: String(input.passenger_count),
  });
  return request(`/trips/search?${query.toString()}`);
}

export type PassengerSeat = {
  trip_seat_id: string;
  seat_code: string;
  available: boolean;
};

export type BookingHold = {
  booking_id: string;
  booking_reference: string;
  status: string;
  hold_expires_at: string;
  fare: { amount_minor_units: number; currency_code: "ETB" } | null;
  payment_enabled: false;
  ticketing_enabled: false;
  next_step: string;
};

export type BookingChallenge = {
  challenge_id: string;
  accepted: boolean;
  expires_in_seconds: number;
  synthetic_test_code?: string;
};

export type BookingDetails = {
  booking_id: string;
  booking_reference: string;
  status: string;
  contact_name: string | null;
  contact_phone_masked: string | null;
  passengers: Array<{ name: string; seat: string }>;
  fare: { amount_minor_units: number; currency_code: "ETB" } | null;
  payment_enabled: false;
  ticketing_enabled: false;
  boarding_authorized: false;
  reservation: {
    reservation_reference: string;
    qr_payload_version: number;
    qr_payload_reference: string;
    status: string;
    payment_collected: false;
    travel_ticket_issued: false;
    boarding_authorized: false;
  } | null;
};

export function listTripSeats(tripId: string): Promise<PassengerSeat[]> {
  return request(`/trips/${encodeURIComponent(tripId)}/seats`);
}

export function createBookingHold(
  payload: {
    trip_id: string;
    booking_contact_name: string;
    booking_contact_phone: string;
    passengers: Array<{ name: string }>;
    seat_ids: string[];
  },
  idempotencyKey: string,
): Promise<BookingHold> {
  return request("/bookings/holds", {
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey },
    body: JSON.stringify(payload),
  });
}

export function requestBookingChallenge(
  booking_reference: string,
  contact_phone: string,
): Promise<BookingChallenge> {
  return request("/passenger-access/challenges", {
    method: "POST",
    body: JSON.stringify({ booking_reference, contact_phone }),
  });
}

export function verifyBookingChallenge(challenge_id: string, code: string): Promise<{ booking_id: string; scope: string; expires_at: string }> {
  return request(`/passenger-access/challenges/${encodeURIComponent(challenge_id)}/verify`, {
    method: "POST",
    body: JSON.stringify({ code }),
  });
}

export function getGuestBooking(bookingId: string): Promise<BookingDetails> {
  return request(`/bookings/${encodeURIComponent(bookingId)}`);
}

export function acceptGuestReservation(bookingId: string): Promise<{
  reservation_reference: string;
  qr_payload_version: number;
  qr_payload_reference: string;
  status: string;
  payment_collected: false;
  travel_ticket_issued: false;
  boarding_authorized: false;
}> {
  return request(`/bookings/${encodeURIComponent(bookingId)}/reservation`, { method: "POST" }, "mnm_booking_csrf");
}


export type PassengerSupportFaq = {
  id: string;
  category: string;
  question: string;
  answer: string;
};

export type PassengerSupportCase = {
  case_reference: string;
  category: string;
  subject: string;
  message: string;
  status: "open" | "in_progress" | "resolved" | "closed";
  resolution_note: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
};

export function listPassengerSupportFaqs(language: "am" | "en"): Promise<{ language: string; items: PassengerSupportFaq[] }> {
  return request(`/passenger/support/faqs?language=${language}`);
}

export async function listPassengerSupportCases(): Promise<PassengerSupportCase[]> {
  const result = await request<{ items: PassengerSupportCase[] }>("/passenger/support/cases");
  return result.items;
}

export function createPassengerSupportCase(input: {
  category: PassengerSupportCase["category"];
  subject: string;
  message: string;
}): Promise<PassengerSupportCase> {
  return request("/passenger/support/cases", {
    method: "POST",
    body: JSON.stringify(input),
  });
}


export type PassengerReport = {
  report_reference: string;
  report_type: "report" | "complaint";
  category: "app_issue" | "journey" | "booking" | "wallet" | "payment" | "safety" | "driver_vehicle" | "accessibility" | "fraud" | "other";
  severity: "low" | "normal" | "high" | "urgent";
  subject: string;
  description: string;
  status: "submitted" | "under_review" | "action_required" | "resolved" | "dismissed";
  resolution_note: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  attachments: Array<{ id: string; file_name: string; content_type: string; size_bytes: number; sha256: string }>;
};

export function listPassengerReports(): Promise<{ items: PassengerReport[] }> {
  return request("/passenger/reports");
}

export function createPassengerReport(input: {
  report_type: PassengerReport["report_type"];
  category: PassengerReport["category"];
  severity: PassengerReport["severity"];
  subject: string;
  description: string;
}): Promise<PassengerReport> {
  return request("/passenger/reports", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function uploadPassengerReportAttachment(reportReference: string, file: File): Promise<{
  id: string; file_name: string; content_type: string; size_bytes: number; sha256: string;
}> {
  const bytes = new Uint8Array(await file.arrayBuffer());
  let binary = "";
  for (let offset = 0; offset < bytes.length; offset += 0x8000) {
    binary += String.fromCharCode(...bytes.subarray(offset, offset + 0x8000));
  }
  return request(`/passenger/reports/${encodeURIComponent(reportReference)}/attachments`, {
    method: "POST",
    body: JSON.stringify({
      file_name: file.name,
      content_type: file.type,
      content_base64: btoa(binary),
    }),
  });
}


export function passengerReportAttachmentUrl(reportReference: string, attachmentId: string): string {
  const root = API_ROOT || "/api/v1";
  return `${root}/passenger/reports/${encodeURIComponent(reportReference)}/attachments/${encodeURIComponent(attachmentId)}`;
}


export type PassengerWalletTransaction = {
  reference: string;
  transaction_type: string;
  status: "posted" | "reversed";
  direction: "credit" | "debit" | "neutral";
  amount_minor_units: number;
  currency_code: "ETB";
  description: string;
  posted_at: string;
};

export type PassengerWallet = {
  wallet_id: string;
  account_status: "active" | "frozen" | "closed";
  balance_minor_units: number;
  currency_code: "ETB";
  history: PassengerWalletTransaction[];
  funding_enabled: false;
  withdrawals_enabled: false;
  transfers_enabled: false;
};

export function getPassengerWallet(): Promise<PassengerWallet> {
  return request("/passenger/wallet");
}


export type PassengerNotification = {
  id: string;
  notification_type: string;
  title: string;
  body: string;
  resource_type: string | null;
  resource_reference: string | null;
  read: boolean;
  created_at: string;
};

export type PassengerNotificationInbox = {
  items: PassengerNotification[];
  unread_count: number;
};

export function getPassengerNotifications(): Promise<PassengerNotificationInbox> {
  return request("/passenger/notifications");
}

export function markPassengerNotificationRead(id: string): Promise<PassengerNotification> {
  return request(`/passenger/notifications/${encodeURIComponent(id)}/read`, { method: "POST" });
}


export function claimPassengerBooking(
  bookingId: string,
  challengeId: string,
  code: string,
): Promise<{ booking_id: string; linked: boolean; status: string }> {
  return request(`/passenger/bookings/${encodeURIComponent(bookingId)}/claim`, {
    method: "POST",
    body: JSON.stringify({ challenge_id: challengeId, code }),
  });
}
