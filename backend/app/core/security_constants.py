"""Shared security constants."""

DEFAULT_USER_ROLE = "user"
ALLOWED_ROLES = frozenset({"admin", "hr", "legal", "employee", "user"})
UPLOAD_ROLES = frozenset({"admin", "hr", "legal", "employee"})

INSECURE_SECRET_KEYS = frozenset({
    "super_secret_key_change_in_production",
    "change_this_to_a_secure_random_string",
    "",
})

INSECURE_OPENAI_KEYS = frozenset({"sk-mock-key", "", "your_openai_api_key_here"})
