import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";

const locations = [
  { id: "origin", name: "Jinka", type: "city" },
  { id: "destination", name: "Wolaita Sodo", type: "city" },
];

describe("passenger trip search shell", () => {
  afterEach(() => {
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
    await waitFor(() => expect(screen.getByRole("option", { name: "Wolaita Sodo" })).toBeTruthy());
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
    await waitFor(() => expect(screen.getByRole("option", { name: "Wolaita Sodo" })).toBeTruthy());
    fireEvent.click(screen.getByRole("button", { name: "ጉዞ ፈልግ" }));
    await waitFor(() => expect(screen.getByText("Jinka Bus Terminal · ባዶ ወንበሮች: 12")).toBeTruthy());
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
