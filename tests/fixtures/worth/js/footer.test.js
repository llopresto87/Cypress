// Fixture: a read-back test in JavaScript under node:test and node:assert,
// and a test beside it that computes a value. worth-check.py flags the first.
const assert = require("node:assert");
const fs = require("node:fs");
const test = require("node:test");
const { formatYear } = require("../src/footer");

test("footer text", () => {
  const html = fs.readFileSync("web/footer.html", "utf8");
  assert.ok(html.includes("All rights reserved"));
  assert.match(html, /Example Ltd/);
});

test("footer year", () => {
  assert.strictEqual(formatYear(new Date(2026, 0, 1)), "2026");
});
