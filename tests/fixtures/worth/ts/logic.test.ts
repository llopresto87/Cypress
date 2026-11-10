// Fixture: tests that look like read-backs but feed inputs to logic: a
// pattern, a condition, an order of precedence, a computed value, and a page
// the code under test rendered. worth-check.py flags none of them.
import { expect, test } from "@playwright/test";
import { EMAIL_RE, isEligible, orderTotal, renderLabel, resolveHandler } from "../src/forms";

test("submit label is Send", () => {
  expect(renderLabel("en")).toBe("Send");
});

test("email pattern accepts plus addresses", () => {
  expect(EMAIL_RE.test("a+b@example.com")).toBe(true);
});

test("eligibility boundary", () => {
  expect(isEligible(18)).toBe(true);
  expect(isEligible(17)).toBe(false);
});

test("route precedence", () => {
  expect(resolveHandler("/submit/new")).toBe("submitNew");
});

test("total with discount", () => {
  expect(orderTotal([{ sku: "pen", qty: 2, cents: 150 }], 0.1)).toBe(270);
});

test("rendered page carries the label", async ({ page }) => {
  await page.goto("/submit");
  await expect(page.locator("button")).toHaveText("Send");
});
