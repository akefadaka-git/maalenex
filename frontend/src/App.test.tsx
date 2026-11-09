import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("MaaleNex Moto multi-role portal", () => {
  it("renders the warm Amharic welcome page by default", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "ጉዞዎ እዚህ ይጀምራል።" })).toBeTruthy();
    expect(screen.getByText(/ደቡብ ኦሞ ዞን/)).toBeTruthy();
  });

  it("switches the welcome page to English", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "EN" }));
    expect(screen.getByRole("heading", { name: "Your journey starts here." })).toBeTruthy();
  });

  it("opens the guest dashboard", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "እንደ እንግዳ ይጎብኙ" }));
    expect(screen.getByRole("heading", { name: "የእንግዳ ዳሽቦርድ" })).toBeTruthy();
  });

  it("offers passenger, motorcycle, heavy-load and fleet registration roles", () => {
    render(<App />);
    fireEvent.click(screen.getAllByRole("button", { name: "መለያ ይፍጠሩ" })[0]);
    const roleSelect = screen.getByLabelText("የአገልግሎት ሚና ይምረጡ");
    expect(roleSelect.querySelectorAll("option")).toHaveLength(4);
    expect(screen.getByRole("option", { name: "የከባድ ጭነት ተሽከርካሪ ሹፌር" })).toBeTruthy();
  });

  it("shows a restricted, non-operational administrator preview", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "አስተዳደር" }));
    expect(screen.getByText(/የአስተዳዳሪ ማረጋገጫና የሰርቨር ፈቃድ/)).toBeTruthy();
  });

  it("keeps login as a non-submitting prototype", () => {
    render(<App />);
    fireEvent.click(screen.getAllByRole("button", { name: "ይግቡ" })[0]);
    expect(screen.getByRole("heading", { name: "ወደ መለያዎ ይግቡ" })).toBeTruthy();
    expect(screen.getByText(/የመለያ ማረጋገጫ እና ፈጠራ አልተገናኙም/)).toBeTruthy();
  });
});
