// Fixture: read-back tests in TypeScript. Each test's only assertions read
// back a literal the change under test adds; worth-check.py flags all three.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it, test } from "vitest";
import { SUBMIT_LABEL } from "../src/labels";

const page = readFileSync(join(__dirname, "../web/submit.html"), "utf8");

test("submit label is Send", () => {
  expect(SUBMIT_LABEL).toBe("Send");
});

describe("submit page", () => {
  it("carries the label", () => {
    expect(page).toContain('value="Send"');
  });

  it("names the route", () => {
    const routes = readFileSync(join(__dirname, "../api/routes.yaml"), "utf8");
    expect(routes).toMatch(/\/submit/);
    expect(routes.includes("submit_form")).toBe(true);
  });
});
