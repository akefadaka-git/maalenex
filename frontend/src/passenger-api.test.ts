import { afterEach, describe, expect, it, vi } from "vitest";
import { listPassengerLocations } from "./passenger-api";

afterEach(() => vi.unstubAllGlobals());

describe("passenger API offline handling", () => {
  it("rejects current-service requests before issuing a network call while offline", async () => {
    vi.stubGlobal("navigator", { onLine: false });
    await expect(listPassengerLocations()).rejects.toThrow(/You are offline/);
  });
});
