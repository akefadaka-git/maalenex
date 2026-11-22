import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { PassengerGoogleMap } from "./PassengerGoogleMap";

afterEach(() => cleanup());

describe("PassengerGoogleMap", () => {
  it("shows an explicit configuration state instead of drawing a fabricated map", async () => {
    render(<PassengerGoogleMap locations={[]} routes={[]} originId="" destinationId="" language="en" onSelectLocation={() => undefined} />);
    expect(await screen.findByText("Google Maps key not configured")).toBeTruthy();
    expect(screen.getByText(/restricted VITE_GOOGLE_MAPS_API_KEY/)).toBeTruthy();
  });
});
