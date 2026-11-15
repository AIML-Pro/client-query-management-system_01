# Code Explanation (Simple) — Client Query Management System

A plain-English guide to every file. Read this before your evaluation.

---

## The big picture (one line)
Clients submit support questions → the support team tracks and closes them → all data is stored in a SQL database → shown on a web page built with Streamlit.

**How files work together:**
`config` (settings) → `database` (storage) → `auth` (login) → `queries` (the work) → `generate_dataset` + `load_data` (fill data) → `app` (the screen).

---

## 1. config.py — the settings file
Holds all settings in one place so nothing is hard-coded elsewhere.

- `import os` → lets us read settings from the environment.
- `load_dotenv()` (in try/except) → loads secrets from a `.env` file; the try/except stops a crash if that library is missing.
- `DB_TYPE` → **the key line.** Chooses the database: `sqlite` (default, no setup) or `mysql`. Switching this one word switches the whole app.
- `MYSQL_CONFIG` → a box of MySQL connection details (host, port, user, password, database name).
- `SQLITE_PATH` → the file name for the SQLite database.
- `DATASET_CSV` → the name of the data file.
- `ROLES`, `STATUS_OPEN`, `STATUS_CLOSED` → fixed words used everywhere, defined once to avoid typos.
- `CATEGORIES` → list of query types, used for sample data and the filter dropdown.

**Say this:** "config.py is my central settings file. One variable, `DB_TYPE`, switches between MySQL and SQLite."

---

## 2. database.py — talks to the database
Opens the database and runs the SQL commands.

- `get_connection()` → opens a connection to MySQL or SQLite (based on `DB_TYPE`). For MySQL it first creates the database if it doesn't exist.
- `_adapt()` → small helper that fixes the placeholder symbol (`%s` for MySQL, `?` for SQLite) so the same SQL works on both.
- `run_write()` → runs INSERT / UPDATE / DELETE and saves (commits) the change.
- `run_query()` → runs SELECT and returns the rows it found.
- `init_db()` → creates the two tables if they don't exist:
  - **users** (username, hashed_password, role)
  - **queries** (query_id, mail_id, mobile, heading, description, category, status, created_time, closed_time)

**Say this:** "database.py handles all database access with plain cursor-based SQL — connect, run the command, commit. No ORM, as the spec required."

---

## 3. auth.py — login and security
Handles users and keeps passwords safe.

- `hash_password()` → turns a password into a scrambled SHA-256 code. The real password is never stored.
- `register_user()` → adds a new user; rejects duplicate usernames and saves the hashed password.
- `login_user()` → scrambles what the user typed and checks if it matches the stored code; returns the user's role if correct.

**Say this:** "I never store real passwords. I store a SHA-256 hash and compare hashes at login, so even a database leak won't expose passwords."

---

## 4. queries.py — the main work
Creates, closes, and counts queries.

- `create_query()` → saves a new query. Sets `status = Open`, stamps `created_time = now()`, leaves `closed_time` empty.
- `close_query()` → changes status to `Closed` and stamps `closed_time = now()`.
- `get_queries()` → fetches queries, with optional filters by status and category.
- `get_metrics()` → counts total / open / closed and calculates the **average resolution time** (closed time minus created time).

**Say this:** "This is the engine. When a query is closed, I stamp the time — the difference between created and closed time powers the resolution-speed metric."

---

## 5. generate_dataset.py — makes sample data
Creates 200 realistic fake queries and saves them to `synthetic_client_queries.csv`.

- Uses templates per category to build believable headings and descriptions.
- About 65% are marked Closed (with a closed time), the rest Open.
- Columns match the spec: query_id, mail_id, mobile_number, query_heading, query_description, category, status, created_time, closed_time.

**Say this:** "This generates the synthetic dataset that simulates initial query logs."

---

## 6. load_data.py — cleans and loads the data
Reads the CSV, cleans it, and puts it into the database.

- `clean_dataframe()` → the **data cleaning** step with Pandas:
  - removes blank rows and duplicates
  - trims extra spaces
  - fixes status spelling to exactly `Open` / `Closed`
  - turns empty closed-times into NULL
  - makes sure Open queries have no closed time
- `load()` → creates tables, clears old data, inserts each cleaned row, and seeds two demo users.

**Say this:** "I clean the raw CSV with Pandas before loading — removing blanks, duplicates, and fixing the status values — then insert row by row."

---

## 7. app.py — the web page (Streamlit)
What the user actually sees and clicks.

- **Login / Register screen** → enter username, password, role.
- After login, the **role decides the page**:
  - **Client page** → a form to submit a query (email, mobile, category, heading, description). It validates the email and 10-digit mobile before saving.
  - **Support dashboard** → shows metric cards (total/open/closed/avg resolution), a bar chart by category, filters for status and category, and a button to **close** any open query.
- A sidebar shows who is logged in and a Logout button.

**Say this:** "app.py is the interface. The user's role routes them to either the submit form or the support dashboard. I do a live demo here."

---

## 5 mock questions — quick answers
1. **Why hash passwords?** → "So real passwords are never stored; I save a SHA-256 code and compare codes."
2. **How is a query closed?** → "Support selects it, status becomes Closed, and datetime.now() stamps the closing time."
3. **How did you clean the data?** → "With Pandas — removed blanks and duplicates, fixed status spelling, handled empty closed-times."
4. **Why Streamlit?** → "It builds a web dashboard quickly in pure Python, with forms and tables."
5. **What is the resolution metric?** → "Closed time minus created time, averaged — it shows how fast support resolves queries."

---

## How to present (to score 7+)
- Start with the **problem**, not the code.
- List the **5 business use cases**.
- Explain the **flow** (login → client submits → support closes).
- Do a **live demo** — this wins big marks.
- Don't read code aloud — explain **why** you wrote it.
- Point to your **README** and **modular file structure** (separate files = code reusability marks).
