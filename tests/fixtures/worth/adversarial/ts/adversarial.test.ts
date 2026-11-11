// Fixture: adversarial cases written by an independent tester to probe
// worth-check.py. The verdict each test is owed is in
// tests/fixtures/worth/adversarial.tsv, written before the tool was run.
import { readFileSync } from "node:fs";
import { beforeAll, expect, test } from "vitest";
import { buildSite } from "../src/build";
import { formatLabel } from "../src/format";
import { resolve, router } from "../src/router";
import { BRAND_COLOUR, COOKIE_BANNER, SHOW_BANNER, SUBMIT_LABEL } from "../src/labels";

beforeAll(() => {
  buildSite("dist");
});

// --- logic between the read and the literal --------------------------------

test("label after formatting", () => {
  const label = formatLabel(SUBMIT_LABEL);
  expect(label).toBe("Send");
});

test("label trimmed and upper-cased", () => {
  const label = SUBMIT_LABEL.trim().toUpperCase();
  expect(label).toBe("SEND");
});

test("label against a joined literal", () => {
  const expected = ["Se", "nd"].join("");
  expect(SUBMIT_LABEL).toBe(expected);
});

// --- false-negative probes ---------------------------------------------------

test.each([["Send"]])("label is %s", (want) => {
  expect(SUBMIT_LABEL).toBe(want);
});

test("label snapshot", () => {
  expect(SUBMIT_LABEL).toMatchSnapshot();
});

test("label inline snapshot", () => {
  expect(SUBMIT_LABEL).toMatchInlineSnapshot(`"Send"`);
});

test("primary colour is #0055ff", () => {
  expect(BRAND_COLOUR).toBe("#0055ff");
});

test("banner hidden by default", () => {
  expect(SHOW_BANNER).toBe(false);
});

test("cookie banner text", () => {
  expect(COOKIE_BANNER).toBe("We use cookies to keep you signed in");
});

test("async label", async () => {
  expect(SUBMIT_LABEL).toBe("Send");
});

// --- false-positive probes ---------------------------------------------------

test("route precedence through resolve", () => {
  expect(resolve("/submit/new")).toBe("submitNew");
});

test("route precedence through router.match", () => {
  expect(router.match("/submit/new")).toBe("submitNew");
});

test("built page carries the label", () => {
  const html = readFileSync("dist/submit.html", "utf8");
  expect(html).toContain('value="Send"');
});
