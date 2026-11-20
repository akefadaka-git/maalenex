import assert from "node:assert/strict";
import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
try {
  for (const viewport of [{ width: 1280, height: 800 }, { width: 360, height: 800 }]) {
    const page = await browser.newPage({ viewport });
    await page.goto("http://127.0.0.1:4173/", { waitUntil: "networkidle" });

    await page.keyboard.press("Tab");
    assert.equal(await page.locator(".skip-link").evaluate((el) => el === document.activeElement), true,
      "The first Tab must focus the skip link.");
    assert.ok(await page.locator(".skip-link").evaluate((el) => getComputedStyle(el).top === "12px"),
      "The focused skip link must become visible.");

    await page.keyboard.press("Tab");
    assert.equal(await page.locator(".brand").evaluate((el) => el === document.activeElement), true,
      "The second Tab must focus the brand/home link.");

    await page.keyboard.press("Tab");
    assert.equal(await page.locator(".language").evaluate((el) => el === document.activeElement), true,
      "The third Tab must focus the language control.");
    const outlineWidth = await page.locator(".language").evaluate((el) => getComputedStyle(el).outlineWidth);
    assert.notEqual(outlineWidth, "0px", "Keyboard focus must have a visible outline.");

    await page.keyboard.press("Tab");
    assert.equal(await page.locator(".search-button").evaluate((el) => el === document.activeElement), true,
      "The next Tab must reach the guest action.");

    await page.keyboard.press("Shift+Tab");
    assert.equal(await page.locator(".language").evaluate((el) => el === document.activeElement), true,
      "Shift+Tab must return to the language control.");

    await page.locator(".skip-link").focus();
    await page.keyboard.press("Enter");
    assert.equal(await page.locator("#main-content").evaluate((el) => el === document.activeElement), true,
      "Activating the skip link must move focus to the main landmark.");

    await page.getByRole("button", { name: "Switch language to English" }).click();
    assert.equal(await page.locator("html").getAttribute("lang"), "en",
      "The language control must update the document language.");
    assert.equal(await page.getByRole("heading", { name: "Plan your journey responsibly." }).count(), 1);

    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    assert.equal(overflow, false, "The page must not overflow horizontally at the tested viewport.");
    console.log(`PASS keyboard focus, skip navigation, language and viewport ${viewport.width}x${viewport.height}`);
    await page.close();
  }
} finally {
  await browser.close();
}
