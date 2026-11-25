/** @vitest-environment jsdom */
import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import InternalGeoMap from "./InternalGeoMap";

vi.mock("maplibre-gl", () => {
  class FakeMap {
    sources = new Map<string, { setData: (data: unknown) => void }>();
    constructor() {}
    addControl() { return this; }
    once(event: string, callback: () => void) {
      if (event === "load") callback();
      return this;
    }
    on() { return this; }
    addSource(id: string) {
      this.sources.set(id, { setData: () => undefined });
      return this;
    }
    addLayer() { return this; }
    getSource(id: string) { return this.sources.get(id); }
    remove() { return this; }
  }
  return {
    default: {
      Map: FakeMap,
      NavigationControl: class {},
      ScaleControl: class {},
    },
  };
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("InternalGeoMap", () => {
  it("loads tenant positions only through the authenticated API", async () => {
    const organizationId = "a3300000-0000-4000-8000-000000000001";
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/auth/sessions/current")) {
        return { ok: true, status: 200 } as Response;
      }
      if (url.includes("/geo/internal/vehicles/positions")) {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            positions: [{
              vehicle_id: "a3300000-0000-4000-8000-000000000011",
              longitude: 36.798589,
              latitude: 5.767863,
              recorded_at: "2026-11-25T07:00:00Z",
              received_at: "2026-11-25T07:00:05Z",
              speed_kph: 22.5,
              heading_degrees: 45,
              accuracy_meters: 5,
              is_synthetic: true,
            }],
          }),
        } as Response;
      }
      throw new Error(`Unexpected fetch: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<InternalGeoMap />);
    await screen.findByText(/Staff session verified/);

    fireEvent.change(screen.getByLabelText("Organization ID"), {
      target: { value: organizationId },
    });
    fireEvent.click(screen.getByRole("button", { name: "Load positions" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining(`organization_id=${organizationId}`),
        expect.objectContaining({
          credentials: "include",
          cache: "no-store",
        }),
      );
    });
    expect(await screen.findByText(/Showing 1 recent vehicle position/)).toBeTruthy();
  });

  it("does not request positions without a staff session", async () => {
    const fetchMock = vi.fn(async () => ({ ok: false, status: 401 }) as Response);
    vi.stubGlobal("fetch", fetchMock);

    render(<InternalGeoMap />);
    await screen.findByText("Staff sign-in is required.");
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(String(fetchMock.mock.calls[0][0])).toContain("/auth/sessions/current");
  });
});
