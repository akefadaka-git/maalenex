import { describe, expect, it } from "vitest";
import { resolveApiUrl } from "./api";

describe("API origin configuration", () => {
  it("uses same-origin API paths when no external origin is configured", () => {
    expect(resolveApiUrl("/api/v1/catalog/locations")).toBe("/api/v1/catalog/locations");
  });

  it("uses the configured HTTPS API origin for packaged clients", () => {
    expect(resolveApiUrl("/api/v1/trips/search", "https://api-test.example.org"))
      .toBe("https://api-test.example.org/api/v1/trips/search");
  });

  it("allows HTTP only for local development origins", () => {
    expect(resolveApiUrl("/api/v1/health", "http://localhost:8000"))
      .toBe("http://localhost:8000/api/v1/health");
  });

  it("rejects insecure non-local API origins", () => {
    expect(() => resolveApiUrl("/api/v1/catalog/locations", "http://api-test.example.org"))
      .toThrow(/HTTPS/);
  });

  it("rejects API origins containing a path or credentials", () => {
    expect(() => resolveApiUrl("/api/v1/catalog/locations", "https://user:secret@api-test.example.org/v1"))
      .toThrow(/only an origin/);
  });

  it("rejects non-API paths", () => {
    expect(() => resolveApiUrl("/admin", "https://api-test.example.org"))
      .toThrow(/rooted under \/api\//);
  });
});
