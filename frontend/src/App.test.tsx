import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import App from "./App";

afterEach(() => { cleanup(); document.documentElement.lang = "am"; });

describe("MaaleNex full-platform interface foundation", () => {
  it("renders an Amharic-first dashboard and branded shell", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "ወደ MaaleNex እንኳን በደህና መጡ" })).toBeTruthy();
    expect(screen.getByRole("navigation")).toBeTruthy();
    expect(screen.getAllByText("MaaleNex").length).toBeGreaterThan(0);
  });
  it("switches language to English", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    expect(screen.getByRole("heading", { name: "Welcome to MaaleNex" })).toBeTruthy();
    expect(document.documentElement.lang).toBe("en");
  });
  it("opens map and displays verified-data boundary", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Map/ }));
    expect(screen.getAllByText(/No verified operating routes/).length).toBeGreaterThan(0);
  });
  it("shows wallet preview without enabling real-money movement", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Wallet/ }));
    expect(screen.getByText(/Real-money transactions are not enabled/)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /Add funds/ }));
    expect(screen.getByRole("status")).toBeTruthy();
  });
  it("provides login and registration screens", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Profile/ }));
    fireEvent.click(screen.getByRole("button", { name: /Log in/ }));
    expect(screen.getByLabelText("Phone number")).toBeTruthy();
  });
  it("captures a report locally and explains that it is not transmitted", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Report/ }));
    fireEvent.change(screen.getByLabelText("Your message"), { target: { value: "Test issue" } });
    fireEvent.click(screen.getByRole("button", { name: /Submit report/ }));
    expect(screen.getByRole("status")).toBeTruthy();
  });
  it("makes dashboard summary widgets navigable", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Wallet balance/ }));
    expect(screen.getByRole("heading", { name: "Wallet" })).toBeTruthy();
  });
  it("provides password visibility and a recovery entry point", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Profile/ }));
    fireEvent.click(screen.getByRole("button", { name: /Log in/ }));
    const password = screen.getByLabelText("Password") as HTMLInputElement;
    expect(password.type).toBe("password");
    fireEvent.click(screen.getByRole("button", { name: "Show password" }));
    expect(password.type).toBe("text");
    fireEvent.click(screen.getByRole("button", { name: "Forgot password?" }));
    expect(screen.getByRole("heading", { name: "Recover password" })).toBeTruthy();
  });
  it("allows profile details to be edited in the preview without claiming server persistence", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /EN/ }));
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /Profile/ }));
    fireEvent.click(screen.getByRole("button", { name: "Edit profile" }));
    fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "Synthetic Passenger" } });
    fireEvent.click(screen.getByRole("button", { name: "Save preview" }));
    expect(screen.getByText(/not saved to an account/i)).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Synthetic Passenger" })).toBeTruthy();
  });

  it("keeps internal provider labels out of public UI", () => {
    render(<App />);
    expect(screen.queryByText(/internal provider/i)).toBeNull();
  });
});
