// Fixture: cases written with their verdicts in
// tests/fixtures/worth/adversarial.tsv before worth-check.py ran over them, on
// the rule that a string key shaped like an HTTP header name declares a
// security control, and that a header-shaped string used as a compared value
// is content.
import { expect, test } from "vitest";
import { HEADERS, LABELS, referrerPolicy, response } from "../src/settings";

test("content type options under a subscript", () => {
  expect(HEADERS["X-Content-Type-Options"]).toBe("nosniff");
});

test("referrer policy as a property", () => {
  expect(HEADERS).toHaveProperty("Referrer-Policy", "no-referrer");
});

test("permissions policy in an object literal", () => {
  expect(HEADERS).toEqual({ "Permissions-Policy": "camera=()" });
});

test("opener policy under a response subscript", () => {
  expect(response.headers["Cross-Origin-Opener-Policy"]).toBe("same-origin");
});

test("hint names a header", () => {
  expect(LABELS["headerHint"]).toBe("Cross-Origin-Opener-Policy");
});

test("referrer constant", () => {
  expect(referrerPolicy).toBe("no-referrer");
});
