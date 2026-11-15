import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import App from "./App";

afterEach(() => {
  cleanup();
  document.documentElement.lang = "am";
});

describe("MaaleNex passenger-only public preview", () => {
  it("renders the Amharic passenger guest preview by default", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "ጉዞዎን በኃላፊነት ያቅዱ።" })).toBeTruthy();
    expect(screen.getByRole("link", { name: "MaaleNex home" })).toBeTruthy();
  });

  it("keeps public guest access available without registration", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "እንደ እንግዳ ይቀጥሉ" }));
    expect(screen.getByRole("status")).toBeTruthy();
    expect(screen.queryByRole("textbox")).toBeNull();
  });

  it("does not expose driver, cargo, or fleet registration/workspaces", () => {
    render(<App />);
    for (const term of [/motorcycle driver/i, /heavy.load/i, /fleet operator/i, /የሞተር ሳይክል ሹፌር/, /የከባድ ጭነት/, /የተሽከርካሪ አስተዳዳሪ/]) {
      expect(screen.queryByText(term)).toBeNull();
    }
    expect(screen.queryByRole("button", { name: /register|create account|መለያ ይፍጠሩ/i })).toBeNull();
  });

  it("does not expose public administration or privileged controls", () => {
    render(<App />);
    expect(screen.queryByText(/administration|admin workspace|አስተዳደር/i)).toBeNull();
    expect(screen.queryByRole("button", { name: /admin|administration|አስተዳደር/i })).toBeNull();
  });

  it("does not collect credentials or personal data and does not claim authentication", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Switch language to English" }));
    expect(screen.queryByRole("textbox")).toBeNull();
    expect(screen.queryByLabelText(/password|email|phone|full name|የይለፍ ቃል|ስልክ|ሙሉ ስም/i)).toBeNull();
    expect(screen.queryByRole("button", { name: /sign in|login|submit|ይግቡ/i })).toBeNull();
    expect(screen.getByText(/no sign-in, registration, personal-data form/i)).toBeTruthy();
  });

  it("removes unsupported route distance and fare claims", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Switch language to English" }));
    expect(screen.queryByText(/\b\d+\s?km\b/i)).toBeNull();
    expect(screen.queryByText(/\b\d+\s?ETB\b/i)).toBeNull();
    expect(screen.getByText(/No verified schedules, fares, or operating services/i)).toBeTruthy();
  });

  it("switches to English and updates document language", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Switch language to English" }));
    expect(screen.getByRole("heading", { name: "Plan your journey responsibly." })).toBeTruthy();
    expect(document.documentElement.lang).toBe("en");
  });
});
