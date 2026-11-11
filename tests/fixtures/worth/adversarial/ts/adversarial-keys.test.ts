// Fixture: a third round of adversarial cases by the independent tester,
// written with their verdicts in tests/fixtures/worth/adversarial.tsv before
// worth-check.py ran over them.
import { readFileSync } from "node:fs";
import { before, describe, test } from "node:test";
import assert from "node:assert";
import { beforeAll, expect, it } from "vitest";
import { buildSite } from "../src/build";
import { config, headers, HEADERS, LABELS, SETTINGS } from "../src/settings";

test("lower-case headers keyed by a string", () => {
  expect(headers["Content-Security-Policy"]).toBe("default-src 'self'");
});

test("nested security property", () => {
  expect(config.security.csp).toBe("default-src 'self'");
});

test("frame header keyed by a string", () => {
  expect(HEADERS["X-Frame-Options"]).toBe("DENY");
});

test("map setting read through get", () => {
  expect(SETTINGS.get("sessionCookieSecure")).toBe(true);
});

test("plain label under a plain key", () => {
  expect(LABELS["submit"]).toBe("Send");
});

describe("built in beforeAll inside describe", () => {
  beforeAll(async () => {
    await buildSite("inner");
  });

  it("page built in a nested beforeAll carries the label", () => {
    expect(readFileSync("inner/submit.html", "utf8")).toContain('value="Send"');
  });
});

describe("built in a node:test before hook", () => {
  before(() => buildSite("node"));

  test("page built in a node before hook carries the label", () => {
    assert.ok(readFileSync("node/submit.html", "utf8").includes('value="Send"'));
  });
});
