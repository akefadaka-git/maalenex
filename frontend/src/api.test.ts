import { afterEach, describe, expect, it, vi } from "vitest";
import { apiUrl } from "./api";

describe("API origin configuration", () => {
  afterEach(() => vi.unstubAllEnvs());

  it("uses same-origin API paths when no external origin is configured", () => {
    vi.stubEnv("VITE_API_BASE_URL", "");
    expect(apiUrl("/api/v1/catalog/locations")).toBe("/api/v1/catalog/locations");
  });

  it("uses the configured HTTPS API origin for packaged clients", () => {
    vi.stubEnv("VITE_API_BASE_URL", "https://api-test.example.org");
    expect(apiUrl("/api/v1/trips/search")).toBe("https://api-test.example.org/api/v1/trips/search");
  });

  it("rejects insecure non-local API origins", () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://api-test.example.org");
    expect(() => apiUrl("/api/v1/catalog/locations")).toThrow(/HTTPS/);
  });

  it("rejects API origins containing a path or credentials", () => {
    vi.stubEnv("VITE_API_BASE_URL", "https://user:secret@api-test.example.org/v1");
    expect(() => apiUrl("/api/v1/catalog/locations")).toThrow(/only an origin/);
  });

  it("rejects non-API paths", () => {
    vi.stubEnv("VITE_API_BASE_URL", "https://api-test.example.org");
    expect(() => apiUrl("/admin")).toThrow(/rooted under \/api\//);
  });
});
