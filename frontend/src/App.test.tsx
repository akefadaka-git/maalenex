import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";

const locations = [
  { id: "origin", name: "Jinka", type: "city" },
  { id: "destination", name: "Wolaita Sodo", type: "city" },
];

describe("passenger trip search shell", () => {
  afterEach(() => {
    cleanup();
    sessionStorage.clear();
    vi.unstubAllGlobals();
    document.documentElement.lang = "am";
  });

  it("renders Amharic passenger search by default", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true, json: async () => locations,
    }));
    render(<App />);
    expect(screen.getByRole("heading", { name: "ጉዞዎን ያቅዱ።" })).toBeTruthy();
    await waitFor(() => expect(screen.getByRole("option", { name: "Jinka" })).toBeTruthy());
    expect(document.documentElement.lang).toBe("am");
  });

  it("switches visible content and document language to English", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true, json: async () => locations,
    }));
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Switch language to English" }));
    expect(screen.getByRole("heading", { name: "Plan your journey." })).toBeTruthy();
    expect(document.documentElement.lang).toBe("en");
    await waitFor(() => expect(screen.getAllByRole("option", { name: "Wolaita Sodo" }).length).toBeGreaterThan(0));
  });

  it("loads and searches synthetic published trips", async () => {
    const trip = {
      id: "trip-1", departure_at: "2026-11-08T06:00:00+00:00",
      arrival_estimate_at: null, boarding_model: "Jinka Bus Terminal",
      available_seats: 12, availability_as_of: "2026-11-07T00:00:00+00:00",
      fare: { amount_minor_units: 250000, currency_code: "ETB" },
      reservation_only: true, ticketing_enabled: false, payment_enabled: false,
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => locations })
      .mockResolvedValueOnce({ ok: true, json: async () => [trip] });
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    await waitFor(() => expect(screen.getAllByRole("option", { name: "Wolaita Sodo" }).length).toBeGreaterThan(0));
    fireEvent.click(screen.getByRole("button", { name: "ጉዞ ፈልግ" }));
    await waitFor(() => expect(screen.getByText(/Jinka Bus Terminal.*12/)).toBeTruthy());
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("loads seat inventory and allows selecting only available seats", async () => {
  const trip = {
    id: "trip-1", departure_at: "2026-11-08T06:00:00+00:00",
    arrival_estimate_at: null, boarding_model: "Jinka Bus Terminal",
    available_seats: 2, availability_as_of: "2026-11-07T00:00:00+00:00",
    fare: { amount_minor_units: 250000, currency_code: "ETB" },
    reservation_only: true, ticketing_enabled: false, payment_enabled: false,
  };
  const fetchMock = vi.fn()
    .mockResolvedValueOnce({ ok: true, json: async () => locations })
    .mockResolvedValueOnce({ ok: true, json: async () => [trip] })
    .mockResolvedValueOnce({ ok: true, json: async () => [
      { trip_seat_id: "seat-1", seat_code: "A1", available: true },
      { trip_seat_id: "seat-2", seat_code: "A2", available: false },
    ] });
  vi.stubGlobal("fetch", fetchMock);
  render(<App />);
  await waitFor(() => expect(screen.getAllByRole("option", { name: "Wolaita Sodo" }).length).toBeGreaterThan(0));
  fireEvent.click(screen.getByRole("button", { name: "ጉዞ ፈልግ" }));
  await waitFor(() => expect(screen.getByRole("button", { name: "ወንበሮችን ይምረጡ" })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: "ወንበሮችን ይምረጡ" }));
  await waitFor(() => expect(screen.getByRole("button", { name: "A1" })).toBeTruthy());
  expect((screen.getByRole("button", { name: "A2" }) as HTMLButtonElement).disabled).toBe(true);
  fireEvent.click(screen.getByRole("button", { name: "A1" }));
  expect(screen.getByRole("button", { name: "A1" }).getAttribute("aria-pressed")).toBe("true");
});
  it("restores a verified booking after refresh and shows its support history", async () => {
    sessionStorage.setItem("mnm_active_booking_id", "booking-restore-1");
    const booking = {
      booking_id: "booking-restore-1", booking_reference: "SYNTHETIC-REF",
      status: "held", passengers: [{ name: "Synthetic Passenger", seat: "A1" }],
      fare: { amount_minor_units: 250000, currency_code: "ETB" },
      payment_enabled: false, ticketing_enabled: false, boarding_authorized: false,
      reservation: null,
    };
    const cases = [{
      case_reference: "MNM-SUP-TEST", category: "reservation_status",
      subject: "Synthetic support", message: "Synthetic test support message",
      status: "open", resolution_code: null, resolution_note: null,
    }];
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => locations })
      .mockResolvedValueOnce({ ok: true, json: async () => booking })
      .mockResolvedValueOnce({ ok: true, json: async () => cases });
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    await waitFor(() => expect(screen.getByText("SYNTHETIC-REF")).toBeTruthy());
    expect(screen.getByRole("heading", { name: "የድጋፍ ጥያቄ" })).toBeTruthy();
    expect(screen.getByText("MNM-SUP-TEST")).toBeTruthy();
  });

});
