# Client Query Management System

Organizing, Tracking, and Closing Support Queries.

A real-time web application where **clients** submit support queries and a
**support team** tracks, filters and closes them. Built with **Python, Pandas,
Streamlit** and **MySQL** (with a zero-setup **SQLite** fallback). All database
access uses plain cursor-based SQL — no SQLAlchemy / ORM.

---

## Features

- 🔐 **Login & registration** for two roles (Client / Support). Passwords are
  hashed with **SHA-256** (`hashlib`) before storage.
- 📝 **Client Submission page** — submit a query (email, mobile, heading,
  description, category). `query_created_time` is auto-set, `status` defaults to
  `Open`, `query_closed_time` stays `NULL`.
- 🧭 **Support Dashboard** — metrics (total / open / closed / avg resolution
  time), queries-by-category chart, filter by status & category, and
  **close an open query** (sets `status=Closed` and stamps `query_closed_time`).
- 📊 Synthetic dataset generator + data-cleaning loader (Pandas).

---

## Project structure

| File | Purpose |
|------|---------|
| `config.py` | Central configuration (DB choice, credentials, constants) |
| `database.py` | Connections + schema (`users`, `queries`), cursor-based SQL |
| `auth.py` | Password hashing, registration, login |
| `queries.py` | Create / close / fetch queries, dashboard metrics |
| `generate_dataset.py` | Create `synthetic_client_queries.csv` |
| `load_data.py` | Clean the CSV and load it into the database |
| `app.py` | Streamlit UI (2 pages) |

---

## Setup

```bash
# 1. (optional) create a virtual environment
python -m venv .venv && source .venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. configure (optional) — copy env template
cp .env.example .env
```

### Database choice

- **SQLite (default):** nothing to install. Leave `DB_TYPE=sqlite`.
- **MySQL:** set `DB_TYPE=mysql` and the `MYSQL_*` values in `.env`. The database
  and tables are created automatically on first run.

---

## Run

```bash
# 1. generate the synthetic dataset
python generate_dataset.py

# 2. create tables, clean & load the data, seed demo users
python load_data.py

# 3. launch the app
streamlit run app.py
```

Open the URL Streamlit prints (default http://localhost:8501).

### Demo credentials (created by `load_data.py`)

| Role | Username | Password |
|------|----------|----------|
| Client | `client1` | `client123` |
| Support | `support1` | `support123` |

You can also register new users from the **Register** tab.

---

## Dataset — `synthetic_client_queries.csv`

Columns: `query_id`, `mail_id`, `mobile_number`, `query_heading`,
`query_description`, `category`, `status` (`Open`/`Closed`),
`query_created_time`, `query_closed_time`.

---

## Tech stack

Python · Pandas · Streamlit · MySQL (`mysql-connector-python`) / SQLite ·
`hashlib` · `datetime`
