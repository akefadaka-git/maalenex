import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import App from "./App";

afterEach(() => {
  cleanup();
});

describe("application shell", () => {
  it("renders Amharic by default", () => {
    render(<App />);
    expect(
      screen.getByRole("heading", { name: "ማአሌኔክስ ሞቶ" }),
    ).toBeTruthy();
  });

  it("switches to English", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "EN" }));
    expect(
      screen.getByRole("heading", { name: "MaaleNex Moto" }),
    ).toBeTruthy();
  });
});
