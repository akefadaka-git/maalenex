import { describe, expect, it } from "vitest";
import { apiUrl, normalizeApiBaseUrl } from "./api";

describe("API origin configuration", () => {
  it("accepts a configured HTTPS origin and removes a trailing slash", () => {
    expect(normalizeApiBaseUrl("https://api-test.maalenex.example", false)).toBe("https://api-test.maalenex.example");
  });

  it("allows an empty origin for same-origin local development only", () => {
    expect(normalizeApiBaseUrl("")).toBe("");
  });

  it("rejects insecure non-local origins", () => {
    expect(() => normalizeApiBaseUrl("http://api-test.maalenex.example", false)).toThrow(/HTTPS/);
  });

  it("rejects placeholder origins", () => {
    expect(() => normalizeApiBaseUrl("https://YOUR-TEST-API-HOST", false)).toThrow(/placeholder/);
    expect(() => normalizeApiBaseUrl("https://api.example.org", false)).toThrow(/placeholder/);
  });

  it("rejects credentials, paths, queries and fragments", () => {
    expect(() => normalizeApiBaseUrl("https://user:pass@api.test")).toThrow();
    expect(() => normalizeApiBaseUrl("https://api.test/v1")).toThrow();
    expect(() => normalizeApiBaseUrl("https://api.test?debug=1")).toThrow();
    expect(() => normalizeApiBaseUrl("https://api.test#fragment")).toThrow();
  });

  it("joins only safe absolute API paths", () => {
    expect(apiUrl("/api/v1/catalog/locations", "")).toBe("/api/v1/catalog/locations");
  });

  it("rejects protocol-relative paths", () => {
    expect(() => apiUrl("//evil.example/path")).toThrow();
  });
});
