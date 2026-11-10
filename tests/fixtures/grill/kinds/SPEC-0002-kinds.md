# SPEC-0002 — submit form (contract kinds)

## 0. Metadata
- **Status:** active
- **Contract form:** kinds

## 4. Functional contracts

### Contract: SUBMIT_RETURNS_2XX
- **Given:** a valid form / **When:** it is submitted / **Then:** 2xx
- **Check:** test

### Contract: SUBMIT_LABEL_IS_SEND
- **Given:** the form / **When:** it renders / **Then:** the button reads Send
- **Check:** run — `make build && grep -c Send dist/index.html`

### Contract: ERROR_COPY_READS_CLEARLY
- **Given:** a rejected form / **When:** it renders / **Then:** the copy reads clearly
- **Check:** review — pending

### Contract: LEGACY_ROUTE_REDIRECTS
- **Given:** the old route / **When:** it is requested / **Then:** it redirects
- **Check:** covered — tests/routes_test.py::test_legacy_redirect

## 10. Test design for risks

| Risk (what breaks, for whom) | Test (file::name, lowest level) | Covers | Origin | Status |
|---|---|---|---|---|
| A valid submission is refused and the customer loses the form | tests/submit_test.py::test_valid_submit_accepted | SUBMIT_RETURNS_2XX | design | pending |
