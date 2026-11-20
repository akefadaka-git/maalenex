import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { BookingFlow } from "./BookingFlow";

afterEach(() => { cleanup(); vi.unstubAllGlobals(); document.cookie = "mnm_booking_csrf=; Max-Age=0; path=/"; document.documentElement.lang = "am"; });

describe("MaaleNex full-platform interface foundation", () => {
  it("renders an Amharic-first dashboard and branded shell", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "ወደ MaaleNex እንኳን በደህና መጡ" })).toBeTruthy();
    expect(screen.getByRole("navigation")).toBeTruthy();
    expect(screen.getAllByText("MaaleNex").length).toBeGreaterThan(0);
  });
  it("switches language to English", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    expect(screen.getByRole("heading", { name: "Welcome to MaaleNex" })).toBeTruthy();
    expect(document.documentElement.lang).toBe("en");
  });
  it("opens map and displays verified-data boundary", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Map/ }));
    expect(screen.getAllByText(/No verified operating routes/).length).toBeGreaterThan(0);
  });
  it("shows wallet preview without enabling real-money movement", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Wallet/ }));
    expect(screen.getByText(/Real-money transactions are not enabled/)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /Add funds/ }));
    expect(screen.getByRole("status")).toBeTruthy();
  });
  it("provides login and registration screens", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Profile/ }));
    fireEvent.click(screen.getByRole("button", { name: /Log in/ }));
    expect(screen.getByLabelText("Email or international phone number")).toBeTruthy();
  });
  it("captures a report locally and explains that it is not transmitted", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Report/ }));
    fireEvent.change(screen.getByLabelText("Your message"), { target: { value: "Test issue" } });
    fireEvent.click(screen.getByRole("button", { name: /Submit report/ }));
    expect(screen.getByRole("status")).toBeTruthy();
  });
  it("makes dashboard summary widgets navigable", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(screen.getByRole("button", { name: /Wallet balance/ }));
    expect(screen.getByRole("heading", { name: "Wallet" })).toBeTruthy();
  });
  it("provides password visibility and a recovery entry point", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Profile/ }));
    fireEvent.click(screen.getByRole("button", { name: /Log in/ }));
    const password = screen.getByLabelText("Password") as HTMLInputElement;
    expect(password.type).toBe("password");
    fireEvent.click(screen.getByRole("button", { name: "Show password" }));
    expect(password.type).toBe("text");
    fireEvent.click(screen.getByRole("button", { name: "Forgot password?" }));
    expect(screen.getByRole("heading", { name: "Recover password" })).toBeTruthy();
  });
  it("allows profile details to be edited in the preview without claiming server persistence", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Profile/ }));
    fireEvent.click(screen.getByRole("button", { name: "Edit profile" }));
    fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "Synthetic Passenger" } });
    fireEvent.click(screen.getByRole("button", { name: "Save profile" }));
    expect(screen.getAllByRole("status").some((item) => /preview changes are local only/i.test(item.textContent ?? ""))).toBe(true);
    expect(screen.getByRole("heading", { name: "Synthetic Passenger" })).toBeTruthy();
  });

  it("submits passenger login to the real account API and restores the signed-in state", async () => {
    const account = {
      id: "passenger-test-id",
      display_name: "Test Passenger",
      login_identifier: "rider@example.test",
      expires_at: "2026-11-21T00:00:00+00:00",
    };
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      if (String(input).endsWith("/passenger/auth/sessions/current")) {
        return { ok: false, status: 401, json: async () => ({ detail: "Authentication required" }) } as Response;
      }
      return { ok: true, status: 200, json: async () => account } as Response;
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Profile/ }));
    fireEvent.click(screen.getByRole("button", { name: /Log in/ }));
    fireEvent.change(screen.getByLabelText("Email or international phone number"), { target: { value: "rider@example.test" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "synthetic-password" } });
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));
    await waitFor(() => expect(screen.getByRole("heading", { name: "Welcome to MaaleNex" })).toBeTruthy());
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/passenger/auth/sessions",
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
    expect(screen.getByRole("status").textContent).toMatch(/signed in/i);
  });

  it("searches only published journeys through the passenger catalog API", async () => {
    const trip = {
      id: "trip-test-id",
      departure_at: "2026-11-21T06:00:00+00:00",
      arrival_estimate_at: "2026-11-21T10:00:00+00:00",
      boarding_model: "Koybe Terminal",
      available_seats: 8,
      availability_as_of: "2026-11-20T16:00:00+00:00",
      fare: { amount_minor_units: 125000, currency_code: "ETB" },
      reservation_only: true,
      ticketing_enabled: false,
      payment_enabled: false,
    };
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/passenger/auth/sessions/current")) {
        return { ok: false, status: 401, json: async () => ({ detail: "Authentication required" }) } as Response;
      }
      if (url.endsWith("/catalog/locations")) {
        return { ok: true, status: 200, json: async () => [
          { id: "origin-id", name: "Koybe", type: "town" },
          { id: "destination-id", name: "Jinka", type: "town" },
        ] } as Response;
      }
      if (url.includes("/trips/search?")) {
        return { ok: true, status: 200, json: async () => [trip] } as Response;
      }
      throw new Error("Unexpected API request: " + url);
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Map/ }));
    await waitFor(() => expect(screen.getByRole("option", { name: "Koybe" })).toBeTruthy());
    fireEvent.change(screen.getByLabelText("Origin"), { target: { value: "origin-id" } });
    fireEvent.change(screen.getByLabelText("Destination"), { target: { value: "destination-id" } });
    fireEvent.click(screen.getByRole("button", { name: "Search journeys" }));
    await waitFor(() => expect(screen.getByText(/Koybe Terminal/)).toBeTruthy());
    expect(fetchMock.mock.calls.some(([input]) => String(input).includes("origin_id=origin-id") && String(input).includes("destination_id=destination-id"))).toBe(true);
  });

  it("holds seats, verifies booking contact and confirms a reservation without payment", async () => {
    let reservationAccepted = false;
    const booking = {
      booking_id: "booking-id",
      booking_reference: "MN-TEST-1234",
      status: reservationAccepted ? "reserved" : "held",
      contact_name: "Test Rider",
      contact_phone_masked: "*******123",
      passengers: [{ name: "Test Passenger", seat: "A1" }],
      fare: { amount_minor_units: 125000, currency_code: "ETB" as const },
      payment_enabled: false as const,
      ticketing_enabled: false as const,
      boarding_authorized: false as const,
      reservation: null as null | {
        reservation_reference: string;
        qr_payload_version: number;
        qr_payload_reference: string;
        status: string;
        payment_collected: false;
        travel_ticket_issued: false;
        boarding_authorized: false;
      },
    };
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/trips/trip-id/seats")) {
        return { ok: true, status: 200, json: async () => [
          { trip_seat_id: "seat-a1", seat_code: "A1", available: true },
        ] } as Response;
      }
      if (url.endsWith("/bookings/holds")) {
        return { ok: true, status: 201, json: async () => ({
          booking_id: "booking-id", booking_reference: "MN-TEST-1234",
          status: "held", hold_expires_at: "2026-11-20T16:20:00Z",
          fare: { amount_minor_units: 125000, currency_code: "ETB" },
          payment_enabled: false, ticketing_enabled: false, next_step: "verify_booking_contact",
        }) } as Response;
      }
      if (url.endsWith("/passenger-access/challenges")) {
        return { ok: true, status: 202, json: async () => ({
          challenge_id: "challenge-id", accepted: true, expires_in_seconds: 600,
          synthetic_test_code: "654321",
        }) } as Response;
      }
      if (url.endsWith("/passenger-access/challenges/challenge-id/verify")) {
        document.cookie = "mnm_booking_csrf=csrf-test; path=/";
        return { ok: true, status: 200, json: async () => ({
          booking_id: "booking-id", scope: "manage", expires_at: "2026-11-20T18:00:00Z",
        }) } as Response;
      }
      if (url.endsWith("/bookings/booking-id/reservation") && init?.method === "POST") {
        reservationAccepted = true;
        booking.status = "reserved";
        booking.reservation = {
          reservation_reference: "RSV-TEST-1234", qr_payload_version: 1,
          qr_payload_reference: "qr-test-reference", status: "active",
          payment_collected: false, travel_ticket_issued: false, boarding_authorized: false,
        };
        return { ok: true, status: 200, json: async () => ({
          reservation_reference: "RSV-TEST-1234", qr_payload_version: 1,
          qr_payload_reference: "qr-test-reference", status: "reserved",
          payment_collected: false, travel_ticket_issued: false, boarding_authorized: false,
        }) } as Response;
      }
      if (url.endsWith("/bookings/booking-id")) {
        return { ok: true, status: 200, json: async () => ({ ...booking }) } as Response;
      }
      throw new Error("Unexpected API request: " + url);
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<BookingFlow
      trip={{
        id: "trip-id", departure_at: "2026-11-21T06:00:00Z",
        arrival_estimate_at: null, boarding_model: "Koybe Terminal",
        available_seats: 1, availability_as_of: "2026-11-20T16:00:00Z",
        fare: { amount_minor_units: 125000, currency_code: "ETB" },
        reservation_only: true, ticketing_enabled: false, payment_enabled: false,
      }}
      passengerCount={1}
      language="en"
      onClose={() => undefined}
    />);
    await waitFor(() => expect(screen.getByLabelText("A1")).toBeTruthy());
    fireEvent.click(screen.getByLabelText("A1"));
    fireEvent.change(screen.getByLabelText("Booking contact name"), { target: { value: "Test Rider" } });
    fireEvent.change(screen.getByLabelText("Contact phone"), { target: { value: "+251911111123" } });
    fireEvent.change(screen.getByLabelText("Passenger 1"), { target: { value: "Test Passenger" } });
    fireEvent.click(screen.getByRole("button", { name: "Hold selected seats" }));
    await waitFor(() => expect(screen.getByText(/654321/)).toBeTruthy());
    fireEvent.change(screen.getByLabelText("Verification code"), { target: { value: "654321" } });
    fireEvent.click(screen.getByRole("button", { name: "Verify contact" }));
    await waitFor(() => expect(screen.getByRole("heading", { name: "Review reservation" })).toBeTruthy());
    fireEvent.click(screen.getByRole("button", { name: "Confirm reservation" }));
    await waitFor(() => expect(screen.getByRole("heading", { name: "Reservation confirmed" })).toBeTruthy());
    expect(screen.getByText(/RSV-TEST-1234/)).toBeTruthy();
    expect(screen.getByText(/No payment was collected and no travel ticket was issued/i)).toBeTruthy();
    expect(fetchMock.mock.calls.some(([input, init]) => String(input).endsWith("/bookings/booking-id/reservation") && init?.headers && new Headers(init.headers).get("X-CSRF-Token") === "csrf-test")).toBe(true);
  });

  it("loads bilingual Help content and submits a support case through the passenger API", async () => {
    document.cookie = "mnm_passenger_csrf=support-csrf-test; path=/";
    const account = {
      id: "passenger-support-test",
      display_name: "Support Test Rider",
      login_identifier: "support-rider@example.test",
      contact_verified: true,
      expires_at: "2026-11-21T00:00:00+00:00",
    };
    const supportCase = {
      case_reference: "MN-SUP-TEST-0001",
      category: "technical",
      subject: "Connection issue",
      message: "The app does not reconnect after internet returns.",
      status: "open",
      resolution_note: null,
      created_at: "2026-11-20T17:00:00+00:00",
      updated_at: "2026-11-20T17:00:00+00:00",
      resolved_at: null,
    };
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/passenger/auth/sessions/current")) {
        return { ok: true, status: 200, json: async () => account } as Response;
      }
      if (url.includes("/passenger/support/faqs?language=en")) {
        return { ok: true, status: 200, json: async () => ({
          language: "en",
          items: [{ id: "help-test", category: "technical", question: "How do I get help?", answer: "Send a support request here." }],
        }) } as Response;
      }
      if (url.endsWith("/passenger/support/cases") && init?.method === "POST") {
        return { ok: true, status: 201, json: async () => supportCase } as Response;
      }
      if (url.endsWith("/passenger/support/cases")) {
        return { ok: true, status: 200, json: async () => ({ items: [] }) } as Response;
      }
      throw new Error("Unexpected API request: " + url);
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/passenger/auth/sessions/current",
      expect.objectContaining({ credentials: "include" }),
    ));
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Help/ }));
    expect(await screen.findByText("How do I get help?")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("Request category"), { target: { value: "technical" } });
    fireEvent.change(screen.getByLabelText("Subject"), { target: { value: "Connection issue" } });
    fireEvent.change(screen.getByLabelText("Message"), { target: { value: "The app does not reconnect after internet returns." } });
    fireEvent.click(screen.getByRole("button", { name: "Submit request" }));
    expect((await screen.findAllByText(/MN-SUP-TEST-0001/)).length).toBeGreaterThanOrEqual(2);
    const submission = fetchMock.mock.calls.find(([input, init]) =>
      String(input).endsWith("/passenger/support/cases") && init?.method === "POST",
    );
    expect(submission).toBeTruthy();
    expect(new Headers(submission?.[1]?.headers).get("X-CSRF-Token")).toBe("support-csrf-test");
  });

  it("keeps internal provider labels out of public UI", () => {
    render(<App />);
    expect(screen.queryByText(/internal provider/i)).toBeNull();
  });
});
