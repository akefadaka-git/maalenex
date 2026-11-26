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
    expect(screen.getByRole("link", { name: "ወደ ዋና ይዘት ዝለል" }).getAttribute("href")).toBe("#hero-title");
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
      arrival_estimate_at: "2026-11-08T14:00:00+00:00", boarding_model: "Jinka Bus Terminal",
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
    expect(screen.getByText(/የመድረሻ ግምት/)).toBeTruthy();
    expect(screen.getByText(/የመረጃ መጨረሻ ዝመና/)).toBeTruthy();
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

  it("ignores stale seat inventory after a different trip is selected", async () => {
    const tripA = {
      id: "trip-a", departure_at: "2026-11-08T06:00:00+00:00",
      arrival_estimate_at: null, boarding_model: "Jinka Bus Terminal",
      available_seats: 2, availability_as_of: "2026-11-07T00:00:00+00:00",
      fare: { amount_minor_units: 250000, currency_code: "ETB" as const },
      reservation_only: true, ticketing_enabled: false as const, payment_enabled: false as const,
    };
    const tripB = {
      ...tripA, id: "trip-b", boarding_model: "Jinka Central Station",
    };
    type SeatResponse = { ok: boolean; json: () => Promise<Array<{ trip_seat_id: string; seat_code: string; available: boolean }>> };
    let resolveFirstSeats!: (response: SeatResponse) => void;
    const firstSeats = new Promise<SeatResponse>((resolve) => { resolveFirstSeats = resolve; });
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => locations })
      .mockResolvedValueOnce({ ok: true, json: async () => [tripA, tripB] })
      .mockReturnValueOnce(firstSeats)
      .mockResolvedValueOnce({ ok: true, json: async () => [
        { trip_seat_id: "seat-b1", seat_code: "B1", available: true },
      ] });
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    await waitFor(() => expect(screen.getAllByRole("option", { name: "Wolaita Sodo" }).length).toBeGreaterThan(0));
    fireEvent.click(screen.getByRole("button", { name: "ጉዞ ፈልግ" }));
    await waitFor(() => expect(screen.getAllByRole("button", { name: "ወንበሮችን ይምረጡ" })).toHaveLength(2));
    const chooseButtons = screen.getAllByRole("button", { name: "ወንበሮችን ይምረጡ" });
    fireEvent.click(chooseButtons[0]);
    fireEvent.click(chooseButtons[1]);
    await waitFor(() => expect(screen.getByRole("button", { name: "B1" })).toBeTruthy());
    expect((fetchMock.mock.calls[2][1] as RequestInit).signal?.aborted).toBe(true);
    resolveFirstSeats({ ok: true, json: async () => [
      { trip_seat_id: "seat-a1", seat_code: "A1", available: true },
    ] });
    await waitFor(() => expect(screen.queryByRole("button", { name: "A1" })).toBeNull());
    expect(screen.getByRole("button", { name: "B1" })).toBeTruthy();
  });

  it("restores a verified booking after refresh and shows its support history", async () => {
    sessionStorage.setItem("mnm_active_booking_id", "booking-restore-1");
    const booking = {
      booking_id: "booking-restore-1", booking_reference: "SYNTHETIC-REF",
      status: "held", passengers: [{ name: "Synthetic Passenger", seat: "A1" }],
      fare: { amount_minor_units: 250000, currency_code: "ETB" },
      payment_enabled: false, ticketing_enabled: false, boarding_authorized: false,
      reservation: {
        reservation_reference: "SYN-RESERVATION",
        qr_payload_version: 1,
        qr_payload_reference: "opaque-qr-reference",
        status: "active",
        payment_collected: false,
        travel_ticket_issued: false,
        boarding_authorized: false,
      },
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
    await waitFor(() => expect(screen.getByText("SYN-RESERVATION")).toBeTruthy());
    expect(screen.getByRole("heading", { name: "የድጋፍ ጥያቄ" })).toBeTruthy();
    expect(screen.getByRole("img", { name: "የቦታ ማስያዣ QR ኮድ" })).toBeTruthy();
    await waitFor(() => expect(screen.getByText("MNM-SUP-TEST")).toBeTruthy());
  });


  it("opens the bilingual About page and exposes creator contact and social links", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true, json: async () => locations,
    }));
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "ስለ MaaleNex" }));
    expect(screen.getByRole("heading", { name: "ስለ MaaleNex" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Akefa Ayele Daka" })).toBeTruthy();
    expect(screen.getByRole("link", { name: /0916546488/ }).getAttribute("href")).toBe("tel:0916546488");
    expect(screen.getByRole("link", { name: "akefaayele@gmail.com" }).getAttribute("href")).toBe("mailto:akefaayele@gmail.com");
    expect(screen.getByRole("link", { name: "Facebook" }).getAttribute("href")).toBe("https://www.facebook.com/akefa.ayele");
    expect(screen.getByRole("link", { name: "Telegram" }).getAttribute("href")).toBe("https://t.me/akefaayle");
    expect(screen.getByRole("link", { name: "YouTube" }).getAttribute("href")).toBe("https://www.youtube.com/@akefaayele6547");
    fireEvent.click(screen.getByRole("button", { name: "ወደ ጉዞ ፍለጋ ተመለስ" }));
    expect(screen.getByRole("heading", { name: "ጉዞዎን ያቅዱ።" })).toBeTruthy();
  });

  it("switches the About page copy to English", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true, json: async () => locations,
    }));
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "ስለ MaaleNex" }));
    fireEvent.click(screen.getByRole("button", { name: "Switch language to English" }));
    expect(screen.getByRole("heading", { name: "About MaaleNex" })).toBeTruthy();
    expect(screen.getByText(/An Ethiopian mobility technology platform/)).toBeTruthy();
  });

});
