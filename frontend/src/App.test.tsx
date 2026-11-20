import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";

afterEach(() => { cleanup(); vi.unstubAllGlobals(); document.documentElement.lang = "am"; });

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

  it("keeps internal provider labels out of public UI", () => {
    render(<App />);
    expect(screen.queryByText(/internal provider/i)).toBeNull();
  });
});
