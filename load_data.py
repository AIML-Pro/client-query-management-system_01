"""
Load the synthetic_client_queries.csv dataset into the database.

Steps:
  1. Initialize the schema (users, queries).
  2. Clean the CSV data with pandas.
  3. Insert the cleaned rows into the `queries` table using cursor-based SQL.
  4. Seed a couple of demo users so the app can be tried immediately.

Run:  python load_data.py
"""

import os

import pandas as pd

import auth
import config
import database


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Basic data cleaning for the query log."""
    # Normalise column names.
    df.columns = [c.strip().lower() for c in df.columns]

    # Drop fully empty rows and duplicates.
    df = df.dropna(how="all").drop_duplicates()

    # Strip whitespace from text fields.
    text_cols = [
        "mail_id",
        "mobile_number",
        "query_heading",
        "query_description",
        "category",
        "status",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Normalise status to the expected 'Open'/'Closed' spelling.
    if "status" in df.columns:
        df["status"] = df["status"].str.capitalize()
        df.loc[~df["status"].isin([config.STATUS_OPEN, config.STATUS_CLOSED]), "status"] = (
            config.STATUS_OPEN
        )

    # Default category when missing.
    if "category" not in df.columns:
        df["category"] = "General"
    df["category"] = df["category"].replace({"": "General", "nan": "General"})

    # Empty / NaN closed times -> None (NULL).
    def norm_closed(v):
        s = str(v).strip()
        if s in ("", "nan", "NaT", "None"):
            return None
        return s

    df["query_closed_time"] = df["query_closed_time"].apply(norm_closed)

    # Open queries must not have a closed time.
    df.loc[df["status"] == config.STATUS_OPEN, "query_closed_time"] = None

    return df


def load():
    # 1. Schema
    database.init_db()

    # 2. Read + clean CSV
    if not os.path.exists(config.DATASET_CSV):
        raise FileNotFoundError(
            f"{config.DATASET_CSV} not found. Run `python generate_dataset.py` first."
        )
    df = pd.read_csv(config.DATASET_CSV)
    df = clean_dataframe(df)

    # 3. Reset the queries table so loading is idempotent.
    database.run_write("DELETE FROM queries")

    inserted = 0
    for _, r in df.iterrows():
        database.run_write(
            """
            INSERT INTO queries
                (mail_id, mobile_number, query_heading, query_description,
                 category, status, query_created_time, query_closed_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                r.get("mail_id"),
                r.get("mobile_number"),
                r.get("query_heading"),
                r.get("query_description"),
                r.get("category"),
                r.get("status"),
                r.get("query_created_time"),
                r.get("query_closed_time"),
            ),
        )
        inserted += 1

    # 4. Seed demo users (ignored if they already exist).
    auth.register_user("client1", "client123", "Client")
    auth.register_user("support1", "support123", "Support")

    print(f"Loaded {inserted} queries into the '{config.DB_TYPE}' database.")
    print("Demo users: client1/client123 (Client), support1/support123 (Support)")


if __name__ == "__main__":
    load()
