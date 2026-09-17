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
