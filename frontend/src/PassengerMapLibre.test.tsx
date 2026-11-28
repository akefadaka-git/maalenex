import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { PassengerMapLibre, setMapLibreLoaderForTests } from "./PassengerMapLibre";
import type { PassengerLocation, PassengerRoute } from "./passenger-api";

afterEach(() => {
  cleanup();
  setMapLibreLoaderForTests();
  vi.unstubAllEnvs();
});

const locations: PassengerLocation[] = [
  { id: "koybe", name: "Koybe", type: "boarding_point", coordinates: { latitude: 5.767863, longitude: 36.798589, source: "operator_confirmed_terminal_pin" } },
  { id: "jinka", name: "Jinka", type: "town", coordinates: { latitude: 5.78, longitude: 36.57, source: "verified_test_fixture" } },
  { id: "addis", name: "Addis Ababa", type: "town", coordinates: { latitude: 9.03, longitude: 38.74, source: "verified_test_fixture" } },
  { id: "hawassa", name: "Hawassa", type: "town", coordinates: { latitude: 7.062, longitude: 38.476, source: "verified_test_fixture" } },
];

function createMapLibreMock() {
  const events = new Map<string, Array<() => void>>();
  const map = {
    on: vi.fn((name: string, callback: () => void) => {
      events.set(name, [...(events.get(name) ?? []), callback]);
    }),
    emit: (name: string) => (events.get(name) ?? []).forEach(callback => callback()),
    fitBounds: vi.fn(),
    addSource: vi.fn(),
    addLayer: vi.fn(),
    getStyle: () => ({ sources: { openmaptiles: { type: "vector", tiles: ["https://tiles.openfreemap.org/data/v3/{z}/{x}/{y}.pbf"] } } }),
    areTilesLoaded: () => true,
    zoomIn: vi.fn(() => (events.get("zoomend") ?? []).forEach(callback => callback())),
    easeTo: vi.fn(),
    remove: vi.fn(),
  };
  let mapOptions: Record<string, unknown> | undefined;
  const MapConstructor = vi.fn(function MapConstructor(options: Record<string, unknown>) { mapOptions = options; return map; });
  const markers: HTMLButtonElement[] = [];
  const MarkerConstructor = vi.fn(function MarkerConstructor(options: { element: HTMLButtonElement }) {
    const element = options.element;
    markers.push(element);
    return {
      setLngLat: vi.fn().mockReturnThis(),
      addTo: vi.fn().mockReturnThis(),
      remove: vi.fn(),
      getElement: () => element,
    };
  });
  const LngLatBoundsConstructor = vi.fn(function LngLatBoundsConstructor() {
    return { extend: vi.fn(), isEmpty: () => false };
  });
  return {
    module: { Map: MapConstructor, Marker: MarkerConstructor, LngLatBounds: LngLatBoundsConstructor },
    getMapOptions: () => mapOptions,
    map, markers, MapConstructor, MarkerConstructor,
  };
}

describe("PassengerMapLibre", () => {
  it("keeps the explicit no-data state and never invents coordinates", async () => {
    render(<PassengerMapLibre locations={[]} routes={[]} originId="" destinationId="" language="en" onSelectLocation={() => undefined} />);
    expect(await screen.findByText("Verified map data not published")).toBeTruthy();
    expect(document.querySelector(".passenger-map")?.getAttribute("data-map-status")).toBe("missing-data");
  });

  it("loads Liberty vector tiles, preserves Ethiopian WGS84 coordinates, draws published geometry and supports marker/zoom interaction", async () => {
    const mock = createMapLibreMock();
    setMapLibreLoaderForTests(async () => mock.module as never);
    const onSelectLocation = vi.fn();
    const route: PassengerRoute = {
      id: "published-route-fixture",
      code: "CI-ETH-01",
      origin: locations[0],
      destination: locations[1],
      stops: [],
      geometry: { type: "LineString", coordinates: [[36.798589, 5.767863], [36.57, 5.78]] },
      geometry_status: "published",
    };

    render(<PassengerMapLibre locations={locations} routes={[route]} originId="koybe" destinationId="jinka" language="en" onSelectLocation={onSelectLocation} />);

    await waitFor(() => expect(mock.MapConstructor).toHaveBeenCalledOnce());
    expect(mock.getMapOptions()).toMatchObject({
      style: "https://tiles.openfreemap.org/styles/liberty",
      center: [36.798589, 5.767863],
    });

    mock.map.emit("load");
    mock.map.emit("idle");
    await waitFor(() => expect(document.querySelector(".passenger-map")?.getAttribute("data-map-status")).toBe("ready"));
    expect(document.querySelector(".passenger-map")?.getAttribute("data-map-style-loaded")).toBe("true");
    expect(document.querySelector(".passenger-map")?.getAttribute("data-map-vector-source-count")).toBe("1");
    expect(document.querySelector(".passenger-map")?.getAttribute("data-map-vector-tiles-loaded")).toBe("true");
    expect(mock.MarkerConstructor).toHaveBeenCalledTimes(4);
    expect(mock.map.addSource).toHaveBeenCalledWith("maalenex-published-route", expect.objectContaining({
      type: "geojson",
      data: expect.objectContaining({ geometry: { type: "LineString", coordinates: [[36.798589, 5.767863], [36.57, 5.78]] } }),
    }));
    expect(mock.map.addLayer).toHaveBeenCalledOnce();

    mock.markers[0].click();
    expect(onSelectLocation).toHaveBeenCalledWith("koybe");
    expect(document.querySelector(".passenger-map")?.getAttribute("data-selected-location")).toBe("koybe");
    mock.map.zoomIn();
    expect(document.querySelector(".passenger-map")?.getAttribute("data-map-interaction-count")).not.toBe("0");
  });

  it("rejects invalid latitude and longitude values", async () => {
    const mock = createMapLibreMock();
    setMapLibreLoaderForTests(async () => mock.module);
    const invalid = [{ id: "bad", name: "Invalid", type: "town", coordinates: { latitude: 95, longitude: 38, source: "test" } }] as PassengerLocation[];
    render(<PassengerMapLibre locations={invalid} routes={[]} originId="" destinationId="" language="en" onSelectLocation={() => undefined} />);
    expect(await screen.findByText("Verified map data not published")).toBeTruthy();
    expect(mock.MapConstructor).not.toHaveBeenCalled();
  });
});
