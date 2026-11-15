"""
Central configuration for the Client Query Management System.

Reads settings from environment variables (optionally via a .env file) so the
project is portable across environments. Two database back-ends are supported:

    DB_TYPE = "mysql"   -> uses mysql-connector-python (project default)
    DB_TYPE = "sqlite"  -> uses the built-in sqlite3 module (zero-setup fallback)

Using SQLite requires no running server, which makes the app runnable out of the
box; switch to MySQL by setting DB_TYPE=mysql and the MYSQL_* variables.
"""

import os

try:
    # Optional: load variables from a local .env file if python-dotenv is present.
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


# ---------------------------------------------------------------------------
# Database selection
# ---------------------------------------------------------------------------
# Default to sqlite so the project runs with no external server. Set DB_TYPE to
# "mysql" (and the MYSQL_* variables below) to use MySQL as described in the spec.
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower().strip()

# MySQL connection settings (used only when DB_TYPE == "mysql")
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "client_query_db"),
}

# SQLite database file (used only when DB_TYPE == "sqlite")
SQLITE_PATH = os.getenv("SQLITE_PATH", "client_query.db")

# Path to the synthetic dataset CSV.
DATASET_CSV = os.getenv("DATASET_CSV", "synthetic_client_queries.csv")

# Valid roles / statuses used across the app.
ROLES = ("Client", "Support")
STATUS_OPEN = "Open"
STATUS_CLOSED = "Closed"

# Query categories used for generation and for the support-side filter.
CATEGORIES = [
    "Billing",
    "Technical",
    "Account",
    "Shipping",
    "Product",
    "General",
]
