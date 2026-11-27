import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { PassengerGoogleMap } from "./PassengerGoogleMap";

afterEach(() => {
  cleanup();
  Reflect.deleteProperty(window, "google");
  vi.unstubAllEnvs();
});

describe("PassengerGoogleMap", () => {
  it("shows an explicit configuration state instead of drawing a fabricated map", async () => {
    vi.stubEnv("VITE_GOOGLE_MAPS_API_KEY", "");
    render(<PassengerGoogleMap locations={[]} routes={[]} originId="" destinationId="" language="en" onSelectLocation={() => undefined} />);
    expect(await screen.findByText("Google Maps key not configured")).toBeTruthy();
    expect(screen.getByText(/restricted VITE_GOOGLE_MAPS_API_KEY/)).toBeTruthy();
    expect(document.querySelector(".passenger-map")?.getAttribute("data-map-status")).toBe("missing-key");
  });

  it("initializes map, verified markers and published route geometry when the Maps API is available", async () => {
    vi.stubEnv("VITE_GOOGLE_MAPS_API_KEY", "unit-test-key");
    const fitBounds = vi.fn();
    const extend = vi.fn();
    const addListener = vi.fn();
    const setMap = vi.fn();
    const mapConstructor = vi.fn(() => ({ panTo: vi.fn(), fitBounds }));
    const markerConstructor = vi.fn(() => ({ addListener }));
    const polylineConstructor = vi.fn(() => ({ setMap }));
    const boundsConstructor = vi.fn(() => ({ extend, isEmpty: () => false }));

    Reflect.set(window, "google", {
      maps: {
        Map: mapConstructor,
        Marker: markerConstructor,
        Polyline: polylineConstructor,
        LatLngBounds: boundsConstructor,
      },
    });

    const locations = [
      { id: "origin", name: "Koybe", type: "boarding_point", coordinates: { latitude: 5.767863, longitude: 36.798589, source: "operator_confirmed_terminal_pin" } },
      { id: "destination", name: "Jinka", type: "town", coordinates: { latitude: 5.780, longitude: 36.570, source: "verified_test_fixture" } },
    ];
    const routes = [{
      id: "route-1",
      code: "TEST-1",
      origin: locations[0],
      destination: locations[1],
      stops: [],
      geometry: { type: "LineString" as const, coordinates: [[36.798589, 5.767863], [36.570, 5.780]] as [number, number][] },
      geometry_status: "published" as const,
    }];

    render(<PassengerGoogleMap locations={locations} routes={routes} originId="origin" destinationId="destination" language="en" onSelectLocation={() => undefined} />);

    await waitFor(() => expect(document.querySelector(".passenger-map")?.getAttribute("data-map-status")).toBe("ready"));
    expect(mapConstructor).toHaveBeenCalledOnce();
    expect(markerConstructor).toHaveBeenCalledTimes(2);
    expect(polylineConstructor).toHaveBeenCalledOnce();
    expect(fitBounds).toHaveBeenCalledOnce();
    expect(screen.getByRole("application", { name: "Google Map" })).toBeTruthy();
  });
});
