// Fixture: a fourth round of adversarial cases by the independent tester:
// security controls in shapes not tried before, written with their verdicts in
// tests/fixtures/worth/adversarial.tsv before worth-check.py ran over them.
import { expect, test } from "vitest";
import { generateToken, isAllowedRedirect } from "../src/auth";
import {
  ALLOWED_ORIGINS, CSRF_COOKIE, JWT_ALGORITHMS, LOCKOUT_THRESHOLD, RATE_LIMITS, ROLE_REQUIRED,
} from "../src/settings";

test("generated token length", () => {
  expect(generateToken()).toHaveLength(32);
});

test("billing needs the owner role", () => {
  expect(ROLE_REQUIRED["/billing"]).toBe("owner");
});

test("sign-in rate limit", () => {
  expect(RATE_LIMITS.login).toBe(5);
});

test("lockout threshold", () => {
  expect(LOCKOUT_THRESHOLD).toBe(5);
});

test("allowed origins contain the app", () => {
  expect(ALLOWED_ORIGINS).toContain("https://app.example.com");
});

test("redirect to another host is refused", () => {
  expect(isAllowedRedirect("//evil.example/x")).toBe(false);
});

test("csrf cookie name", () => {
  expect(CSRF_COOKIE).toBe("XSRF-TOKEN");
});

test("jwt algorithms allowed", () => {
  expect(JWT_ALGORITHMS).toEqual(["RS256"]);
});
