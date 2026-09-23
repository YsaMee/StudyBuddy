"""
Accounts — validation rules for real-style (email + password) sign-up.
Kept separate from both storage (data.py) and the model (models.py) so the
rules themselves (what counts as a valid email/password) can be changed or
tightened without touching how a User is stored or rendered.

Note: this is prototype-level validation only (format + strength checks).
It does not hash passwords or provide real security — that's out of scope
for this course project, but the separation here is where that would plug
in later (e.g. swapping check_password for a hashed comparison).
"""

import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

MIN_PASSWORD_LENGTH = 8


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email.strip())) if email else False


def password_issues(password: str) -> list:
    """Returns a list of human-readable problems with the password (empty = valid)."""
    issues = []
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        issues.append(f"at least {MIN_PASSWORD_LENGTH} characters")
    if not any(c.isdigit() for c in password):
        issues.append("at least one number")
    if not any(c.isupper() for c in password):
        issues.append("at least one uppercase letter")
    return issues


def is_valid_password(password: str) -> bool:
    return not password_issues(password)
