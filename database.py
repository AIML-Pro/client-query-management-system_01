"""
Database access layer for the Client Query Management System.

All SQL is executed with a cursor (no SQLAlchemy / ORM), as required by the
project spec. The same cursor-based code works against MySQL
(mysql-connector-python) and SQLite; a small helper rewrites the `%s`
placeholder to `?` when running on SQLite.
"""

import config


# ---------------------------------------------------------------------------
# Connection handling
# ---------------------------------------------------------------------------
def get_connection():
    """Return a new DB-API connection based on config.DB_TYPE."""
    if config.DB_TYPE == "mysql":
        import mysql.connector

        # Ensure the target database exists before connecting to it.
        server_cfg = {k: v for k, v in config.MYSQL_CONFIG.items() if k != "database"}
        tmp = mysql.connector.connect(**server_cfg)
        cur = tmp.cursor()
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{config.MYSQL_CONFIG['database']}`"
        )
        tmp.commit()
        cur.close()
        tmp.close()
        return mysql.connector.connect(**config.MYSQL_CONFIG)

    # Default: SQLite
    import sqlite3

    conn = sqlite3.connect(config.SQLITE_PATH)
    return conn


def _adapt(sql: str) -> str:
    """Convert `%s` placeholders to `?` when running on SQLite."""
    if config.DB_TYPE == "sqlite":
        return sql.replace("%s", "?")
    return sql


def run_write(sql: str, params=()):
    """Execute an INSERT/UPDATE/DELETE and commit. Returns lastrowid."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(_adapt(sql), params)
        conn.commit()
        last_id = cur.lastrowid
        cur.close()
        return last_id
    finally:
        conn.close()


def run_query(sql: str, params=()):
    """Execute a SELECT and return (columns, rows)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(_adapt(sql), params)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        cur.close()
        return columns, rows
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
def init_db():
    """Create the `users` and `queries` tables if they do not exist."""
    conn = get_connection()
    try:
        cur = conn.cursor()

        if config.DB_TYPE == "mysql":
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS queries (
                    query_id INT AUTO_INCREMENT PRIMARY KEY,
                    mail_id VARCHAR(255) NOT NULL,
                    mobile_number VARCHAR(20),
                    query_heading VARCHAR(255) NOT NULL,
                    query_description TEXT,
                    category VARCHAR(50),
                    status VARCHAR(20) NOT NULL DEFAULT 'Open',
                    query_created_time DATETIME NOT NULL,
                    query_closed_time DATETIME NULL
                )
                """
            )
        else:  # sqlite
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS queries (
                    query_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mail_id TEXT NOT NULL,
                    mobile_number TEXT,
                    query_heading TEXT NOT NULL,
                    query_description TEXT,
                    category TEXT,
                    status TEXT NOT NULL DEFAULT 'Open',
                    query_created_time TEXT NOT NULL,
                    query_closed_time TEXT
                )
                """
            )

        conn.commit()
        cur.close()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized using DB_TYPE={config.DB_TYPE}.")
