import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import App from "./App";
import { getIrokaProvider } from "./iroka/provider";

afterEach(() => {
  cleanup();
  document.documentElement.lang = "am";
});

describe("MaaleNex NEXUS passenger preview", () => {
  it("renders the Amharic welcome page by default", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "መንገድዎን በእርጋታ። ወደፊትዎን በእምነት።" })).toBeTruthy();
    expect(screen.getByText("እንኳን ወደ MaaleNex በደህና መጡ")).toBeTruthy();
    expect(screen.getByRole("navigation")).toBeTruthy();
  });

  it("switches language and updates the document language", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "ቋንቋውን ወደ እንግሊዝኛ ቀይር" }));
    expect(screen.getByRole("heading", { name: "Move with ease. Move forward with confidence." })).toBeTruthy();
    expect(document.documentElement.lang).toBe("en");
  });

  it("connects Home, About and IROKA views through primary navigation", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /ስለ እኛ/ }));
    expect(screen.getByRole("heading", { name: "ስለ MaaleNex" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "IROKA" }));
    expect(screen.getByRole("heading", { name: "IROKA የኢንተለጀንስ ንብርብር" })).toBeTruthy();
    fireEvent.click(within(screen.getByRole("navigation")).getByRole("button", { name: /መነሻ/ }));
    expect(screen.getByRole("heading", { name: "መንገድዎን በእርጋታ። ወደፊትዎን በእምነት።" })).toBeTruthy();
  });

  it("clearly reports that the IROKA runtime is not connected", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "IROKA" }));
    expect(screen.getByText(/ገና አልተገናኘም/)).toBeTruthy();
    expect(getIrokaProvider().status).toBe("not-connected");
  });

  it("provides guest preview without collecting credentials or personal data", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "እንደ እንግዳ ይቀጥሉ" }));
    expect(screen.getByRole("status")).toBeTruthy();
    expect(screen.queryByRole("textbox")).toBeNull();
    expect(screen.queryByLabelText(/password|email|phone|full name|የይለፍ ቃል|ስልክ|ሙሉ ስም/i)).toBeNull();
  });

  it("does not expose driver, cargo, fleet or public administration workspaces", () => {
    render(<App />);
    for (const term of [/motorcycle driver/i, /heavy.load/i, /fleet operator/i, /admin workspace/i, /የሞተር ሳይክል ሹፌር/, /የከባድ ጭነት/]) {
      expect(screen.queryByText(term)).toBeNull();
    }
  });

  it("shows an empty journey-information state instead of inventing routes or schedules", () => {
    render(<App />);
    expect(screen.getByText("ገና የታተመ የጉዞ መረጃ የለም")).toBeTruthy();
    expect(screen.getByText(/የተረጋገጠ መረጃ እስኪገኝ ድረስ/)).toBeTruthy();
  });

  it("retains a clear development-only operating boundary", () => {
    render(<App />);
    expect(screen.getByText(/የልማት ማሳያ ነው/)).toBeTruthy();
    expect(screen.queryByRole("button", { name: /book|payment|ticket|ክፍያ|ቦታ ማስያዣ/i })).toBeNull();
  });
});
