---
status: active
status_date: 2026-11-10
---

# SPEC-0401-kinds

## 0. Metadata
- **Status:** see frontmatter (single home)
- **Contract form:** kinds
- **Sign-offs:** product [x] · architect [x] · tester [x] · security [ ]

## 4. Functional contracts

### Contract: SUBMIT_VALID_FORM_RETURNS_2XX
- **Given:** a valid form
- **When:** it is submitted
- **Then:** the reply is 2xx
- **Check:** test

### Contract: SUBMIT_BUTTON_LABEL_IS_SEND
- **Given:** the form page
- **When:** it renders
- **Then:** the button reads Send
- **Check:** run — `make build && grep -c Send dist/index.html` → pass (2026-11-12)

### Contract: ERROR_COPY_READS_CLEARLY
- **Given:** a rejected form
- **When:** the error shows
- **Then:** the copy names the field
- **Check:** review — confirmed by reviewer spawn rev-0001 (2026-11-12)

### Contract: LEGACY_ROUTE_STILL_REDIRECTS
- **Given:** the old route
- **When:** it is requested
- **Then:** it redirects
- **Check:** covered — tests/routes_test.py::test_legacy_redirect

### Declared values
| Value | Kind | Where |
|---|---|---|
| submit button label "Send" | label | web/submit.html |
| route /submit | route | api/routes.yaml |
- **Check:** run — `make routes-check` → pass (2026-11-12)

## 7. Failure modes

### Failure: FAIL_LOG_WORDING
- **Trigger:** a log line reads oddly

## 9. Acceptance criteria
- [ ] AC-1: a valid form is accepted — maps to SUBMIT_VALID_FORM_RETURNS_2XX
- [ ] AC-2: the label reads Send — maps to DV:submit button label

## 10. Test design for risks

| Risk (what breaks, for whom) | Test (file::name, lowest level) | Covers | Origin | Status |
|---|---|---|---|---|
| A valid form is refused and the customer cannot submit | tests/submit_test.py::test_valid_form_accepted | SUBMIT_VALID_FORM_RETURNS_2XX | design | green |
| Cosmetic log wording differs in an error path | accepted, untested — nobody is hurt, a log line is not a contract | FAIL_LOG_WORDING | | |
