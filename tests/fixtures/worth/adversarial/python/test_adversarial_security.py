"""Fixture: a fourth round of adversarial cases by the independent tester:
security controls in shapes not tried before, written with their verdicts in
tests/fixtures/worth/adversarial.tsv before worth-check.py ran over them."""
from app.auth import generate_token, hash_password, safe_redirect
from app.settings import (ALLOWED_HOSTS, ALLOWED_ORIGINS, CSRF_COOKIE_NAME, JWT_ALGORITHMS,
                          LOCKOUT_THRESHOLD, RATE_LIMITS, ROLE_REQUIRED, TOKEN_LENGTH)


def test_generated_token_length():
    assert len(generate_token()) == 32


def test_token_length_setting():
    assert TOKEN_LENGTH == 32


def test_billing_needs_the_owner_role():
    assert ROLE_REQUIRED["/billing"] == "owner"


def test_sign_in_rate_limit():
    assert RATE_LIMITS["login"] == 5


def test_lockout_threshold():
    assert LOCKOUT_THRESHOLD == 5


def test_password_hash_prefix():
    assert hash_password("correct horse").startswith("$argon2id$")


def test_allowed_origins_list():
    assert ALLOWED_ORIGINS == ["https://app.example.com"]


def test_allowed_host_membership():
    assert "app.example.com" in ALLOWED_HOSTS


def test_foreign_host_not_allowed():
    assert "evil.example" not in ALLOWED_HOSTS


def test_redirect_to_another_host_is_refused():
    assert safe_redirect("//evil.example/x") == "/"


def test_csrf_cookie_name():
    assert CSRF_COOKIE_NAME == "csrftoken"


def test_jwt_algorithms_allowed():
    assert JWT_ALGORITHMS == ["RS256"]
