import assert from "node:assert/strict";
import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
const focusIsVisible = async (locator) => locator.evaluate((el) => {
  const style = getComputedStyle(el);
  return style.outlineStyle !== "none" && style.outlineWidth !== "0px";
});
const auditAccessibility = async (page, language, viewport) => {
  // Load axe from the same-origin production preview. This preserves the app's
  // production CSP (script-src 'self') instead of injecting an inline script.
  await page.addScriptTag({ url: "http://127.0.0.1:4173/a4/axe.min.js" });
  const results = await page.evaluate(async () => window.axe.run(document, {
    runOnly: {
      type: "tag",
      values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]
    }
  }));
  const violations = results.violations.map((item) => ({
    id: item.id,
    impact: item.impact,
    help: item.help,
    nodes: item.nodes.map((node) => ({ target: node.target, summary: node.failureSummary }))
  }));
  assert.deepEqual(violations, [],
    `axe-core accessibility violations in ${language} at ${viewport.width}px: ${JSON.stringify(violations)}`);
  console.log(`PASS axe-core WCAG 2.2 AA and best-practice scan: ${language}, ${viewport.width}px`);
};

try {
  for (const viewport of [{ width: 1280, height: 800 }, { width: 360, height: 800 }]) {
    const page = await browser.newPage({ viewport });
    await page.goto("http://127.0.0.1:4173/", { waitUntil: "networkidle" });

    await page.keyboard.press("Tab");
    assert.equal(await page.locator(".skip-link").evaluate((el) => el === document.activeElement), true,
      "The first Tab must focus the skip link.");
    assert.ok(await page.locator(".skip-link").evaluate((el) => getComputedStyle(el).top === "12px"),
      "The focused skip link must become visible.");
    assert.equal(await focusIsVisible(page.locator(".skip-link")), true,
      "The skip link must have a visible keyboard focus indicator.");

    await page.keyboard.press("Tab");
    assert.equal(await page.locator(".brand").evaluate((el) => el === document.activeElement), true,
      "The second Tab must focus the brand/home link.");
    assert.equal(await focusIsVisible(page.locator(".brand")), true,
      "The brand link must have a visible keyboard focus indicator.");

    await page.keyboard.press("Tab");
    assert.equal(await page.locator(".language").evaluate((el) => el === document.activeElement), true,
      "The third Tab must focus the language control.");
    assert.equal(await focusIsVisible(page.locator(".language")), true,
      "The language control must have a visible keyboard focus indicator.");

    await page.keyboard.press("Tab");
    assert.equal(await page.locator(".search-button").evaluate((el) => el === document.activeElement), true,
      "The next Tab must reach the guest action.");
    assert.equal(await focusIsVisible(page.locator(".search-button")), true,
      "The guest action must have a visible keyboard focus indicator.");

    await page.keyboard.press("Shift+Tab");
    assert.equal(await page.locator(".language").evaluate((el) => el === document.activeElement), true,
      "Shift+Tab must return to the language control.");

    await page.locator(".skip-link").focus();
    await page.keyboard.press("Enter");
    assert.equal(await page.locator("#main-content").evaluate((el) => el === document.activeElement), true,
      "Activating the skip link must move focus to the main landmark.");

    await page.getByRole("button", { name: "Switch language to English" }).click();
    await page.waitForFunction(() => document.documentElement.lang === "en");
    assert.equal(await page.getByRole("heading", { name: "Plan your journey responsibly." }).count(), 1);
    await auditAccessibility(page, "English", viewport);

    await page.getByRole("button", { name: "ቋንቋውን ወደ አማርኛ ቀይር" }).click();
    await page.waitForFunction(() => document.documentElement.lang === "am");
    assert.equal(await page.getByRole("heading", { name: "ጉዞዎን በኃላፊነት ያቅዱ።" }).count(), 1);
    await auditAccessibility(page, "Amharic", viewport);

    await page.getByRole("button", { name: "እንደ እንግዳ ይቀጥሉ" }).click();
    assert.equal(await page.getByRole("status").count(), 1,
      "Guest action must announce its resulting status to assistive technology.");

    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    assert.equal(overflow, false, "The page must not overflow horizontally at the tested viewport.");
    console.log(`PASS keyboard focus, skip navigation, language, guest status and viewport ${viewport.width}x${viewport.height}`);
    await page.close();
  }
} finally {
  await browser.close();
}
