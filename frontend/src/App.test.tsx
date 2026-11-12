import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import App from "./App";

afterEach(() => {
  cleanup();
});

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
    fireEvent.change(roleSelect, { target: { value: "heavy_load_driver" } });
    expect(screen.getByLabelText("የጭነት አቅም (ኪ.ግ.)")).toBeTruthy();
    expect(screen.getByLabelText("የሹፌር ፈቃድ ቁጥር")).toBeTruthy();
  });

  it("shows a motorcycle driver-specific dashboard preview", () => {
    render(<App />);
    fireEvent.click(screen.getAllByRole("button", { name: "መለያ ይፍጠሩ" })[0]);
    fireEvent.change(screen.getByLabelText("የአገልግሎት ሚና ይምረጡ"), { target: { value: "motorcycle_driver" } });
    fireEvent.click(screen.getByRole("button", { name: "የእኔ ዳሽቦርድ" }));
    expect(screen.getByText("የሞተር ሳይክል ሹፌር")).toBeTruthy();
    expect(screen.getByText("የጉዞ ጥያቄዎች")).toBeTruthy();
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
