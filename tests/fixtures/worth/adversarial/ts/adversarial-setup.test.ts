// Fixture: a second round of adversarial cases by the independent tester,
// written with their verdicts in tests/fixtures/worth/adversarial.tsv before
// worth-check.py ran over them.
import { readFileSync } from "node:fs";
import { beforeEach, describe, expect, test } from "vitest";
import { isEligible, renderPage } from "../src/forms";
import { SUBMIT_LABEL } from "../src/labels";

test.each([
  [18, true],
  [17, false],
])("eligible at %i is %s", (age, ok) => {
  expect(isEligible(age)).toBe(ok);
});

describe("rendered in beforeEach", () => {
  let html = "";
  beforeEach(async () => {
    html = await renderPage("submit");
  });

  test("page rendered in beforeEach carries the label", () => {
    expect(html).toContain('value="Send"');
  });
});

describe("rendered in the describe body", () => {
  const page = renderPage("submit");

  test("page rendered in the describe body carries the label", () => {
    expect(page).toContain('value="Send"');
  });
});

describe("read in the describe body", () => {
  const page = readFileSync("web/submit.html", "utf8");

  test("page read in the describe body carries the label", () => {
    expect(page).toContain('value="Send"');
  });
});

test("label held in a local const", () => {
  const label = SUBMIT_LABEL;
  expect(label).toBe("Send");
});
