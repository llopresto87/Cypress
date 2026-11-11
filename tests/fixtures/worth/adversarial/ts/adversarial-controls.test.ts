// Fixture: a second round of adversarial cases by the independent tester, in a
// file with no setup hook, written with their verdicts in
// tests/fixtures/worth/adversarial.tsv before worth-check.py ran over them.
import { readFileSync } from "node:fs";
import { expect, test } from "vitest";
import { HEADERS } from "../src/settings";
import { store } from "../src/uploads";

test("nav has no drafts link", () => {
  const nav = readFileSync("web/nav.html", "utf8");
  expect(nav).not.toContain("/drafts");
});

test("oversized upload throws", () => {
  expect(() => store("x".repeat(10_000_000))).toThrow();
});

test("policy header held in a keyed setting", () => {
  expect(HEADERS["Content-Security-Policy"]).toBe("default-src 'self'");
});
