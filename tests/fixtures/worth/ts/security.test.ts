// Fixture: security negative controls. Each asserts that something is
// refused or absent; worth-check.py flags none of them.
import { readFileSync } from "node:fs";
import { expect, test } from "vitest";
import { PRODUCTION } from "../src/settings";
import { safeUploadPath } from "../src/uploads";

test("upload name with traversal is refused", () => {
  expect(() => safeUploadPath("../../etc/passwd")).toThrow();
});

test("admin page is not linked from the public nav", () => {
  const nav = readFileSync("web/nav.html", "utf8");
  expect(nav).not.toContain("/admin");
});

test("debug is off in production", () => {
  expect(PRODUCTION.debug).toBe(false);
});
