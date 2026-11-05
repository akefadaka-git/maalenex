import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";
describe("application shell", () => { it("renders Amharic by default", () => { render(<App />); expect(screen.getByRole("heading", { name: "ማአሌኔክስ ሞቶ" })).toBeTruthy(); }); it("switches to English", () => { render(<App />); fireEvent.click(screen.getByRole("button")); expect(screen.getByRole("heading", { name: "MaaleNex Moto" })).toBeTruthy(); }); });
