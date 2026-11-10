// Fixture: regression tests for bugs. The second has the shape of a
// read-back, and it stays: a bug reproduction is always written and kept.
import { expect, test } from "vitest";
import { DEFAULT_CURRENCY, FakeGateway, pay } from "../src/billing";

// Bug: the retry after a timeout charged the card twice (issue #412).
test("retry after timeout charges once", async () => {
  const gateway = new FakeGateway({ failFirst: true });
  await pay(gateway, 500);
  expect(gateway.charges).toBe(1);
});

// Regression: a release shipped USD as the default currency (bug #388).
test("default currency stays EUR", () => {
  expect(DEFAULT_CURRENCY).toBe("EUR");
});
