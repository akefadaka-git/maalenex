import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import App from "./App";

describe("application shell", () => {
  afterEach(() => {
    cleanup();
    document.documentElement.lang = "am";
  });

  it("renders Amharic by default", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "ማአሌኔክስ ሞቶ" })).toBeTruthy();
    expect(document.documentElement.lang).toBe("am");
  });

  it("switches visible content and document language to English", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Switch language to English" }));
    expect(screen.getByRole("heading", { name: "MaaleNex Moto" })).toBeTruthy();
    expect(document.documentElement.lang).toBe("en");
  });

  it("switches back to Amharic", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Switch language to English" }));
    fireEvent.click(screen.getByRole("button", { name: "ቋንቋውን ወደ አማርኛ ቀይር" }));
    expect(screen.getByRole("heading", { name: "ማአሌኔክስ ሞቶ" })).toBeTruthy();
    expect(document.documentElement.lang).toBe("am");
  });
});
