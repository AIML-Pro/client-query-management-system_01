"""
Authentication helpers: password hashing, registration and login.

Passwords are hashed with SHA-256 (hashlib) before being stored, exactly as the
spec describes. Plain-text passwords are never written to the database.
"""

import hashlib

import database


def hash_password(password: str) -> str:
    """Return the SHA-256 hex digest of the given password."""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, password: str, role: str) -> tuple[bool, str]:
    """Create a new user. Returns (success, message)."""
    username = (username or "").strip()
    if not username or not password:
        return False, "Username and password are required."

    # Reject duplicate usernames.
    _, rows = database.run_query(
        "SELECT id FROM users WHERE username = %s", (username,)
    )
    if rows:
        return False, "Username already exists. Please choose another."

    hashed = hash_password(password)
    database.run_write(
        "INSERT INTO users (username, hashed_password, role) VALUES (%s, %s, %s)",
        (username, hashed, role),
    )
    return True, f"User '{username}' registered successfully as {role}."


def login_user(username: str, password: str) -> tuple[bool, str, str]:
    """
    Validate credentials.

    Returns (success, role, message). On success `role` is the user's role.
    """
    username = (username or "").strip()
    if not username or not password:
        return False, "", "Please enter both username and password."

    hashed = hash_password(password)
    _, rows = database.run_query(
        "SELECT role FROM users WHERE username = %s AND hashed_password = %s",
        (username, hashed),
    )
    if rows:
        return True, rows[0][0], "Login successful."
    return False, "", "Invalid username or password."
