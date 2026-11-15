"""
Client Query Management System - Streamlit app.

Two role-based pages:
  * Client  -> submit new queries (Query Insertion page)
  * Support -> monitor, filter and close queries (Query Management dashboard)

Run:  streamlit run app.py
"""

import re

import pandas as pd
import streamlit as st

import auth
import config
import database
import queries as q

st.set_page_config(page_title="Client Query Management System", page_icon="📨", layout="wide")

# Make sure tables exist before anything else.
database.init_db()


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------
def _init_state():
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("username", "")
    st.session_state.setdefault("role", "")


def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MOBILE_RE = re.compile(r"^\d{10}$")


# ---------------------------------------------------------------------------
# Authentication UI
# ---------------------------------------------------------------------------
def auth_page():
    st.title("📨 Client Query Management System")
    st.caption("Organizing, Tracking, and Closing Support Queries")

    login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
        if submitted:
            ok, role, msg = auth.login_user(username, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username = username.strip()
                st.session_state.role = role
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Choose a username")
            new_password = st.text_input("Choose a password", type="password")
            role = st.selectbox("Role", config.ROLES)
            submitted = st.form_submit_button("Register")
        if submitted:
            ok, msg = auth.register_user(new_username, new_password, role)
            st.success(msg) if ok else st.error(msg)


# ---------------------------------------------------------------------------
# Client page - submit queries
# ---------------------------------------------------------------------------
def client_page():
    st.header("Submit a New Query")
    st.write(f"Logged in as **{st.session_state.username}** (Client)")

    with st.form("query_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            mail_id = st.text_input("Email ID")
        with col2:
            mobile_number = st.text_input("Mobile Number (10 digits)")
        category = st.selectbox("Category", config.CATEGORIES)
        query_heading = st.text_input("Query Heading")
        query_description = st.text_area("Query Description", height=140)
        submitted = st.form_submit_button("Submit Query")

    if submitted:
        errors = []
        if not EMAIL_RE.match(mail_id.strip()):
            errors.append("Please enter a valid email address.")
        if not MOBILE_RE.match(mobile_number.strip()):
            errors.append("Mobile number must be exactly 10 digits.")
        if not query_heading.strip():
            errors.append("Query heading is required.")
        if not query_description.strip():
            errors.append("Query description is required.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            new_id = q.create_query(
                mail_id, mobile_number, query_heading, query_description, category
            )
            st.success(f"✅ Query submitted successfully! Your query ID is {new_id}.")

    st.divider()
    st.subheader("Your Submitted Queries")
    df = q.get_queries()
    if not df.empty:
        mine = df[df["mail_id"] == mail_id.strip()] if mail_id.strip() else df
        st.caption("Showing all queries (enter your email above to filter to yours).")
        st.dataframe(mine, use_container_width=True, hide_index=True)
    else:
        st.info("No queries yet.")


# ---------------------------------------------------------------------------
# Support page - manage queries
# ---------------------------------------------------------------------------
def support_page():
    st.header("Support Dashboard")
    st.write(f"Logged in as **{st.session_state.username}** (Support)")

    # --- Metrics ------------------------------------------------------------
    m = q.get_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Queries", m["total"])
    c2.metric("Open", m["open"])
    c3.metric("Closed", m["closed"])
    avg = m["avg_resolution_hours"]
    c4.metric("Avg Resolution (hrs)", avg if avg is not None else "—")

    if m["by_category"]:
        st.subheader("Queries by Category")
        cat_df = (
            pd.DataFrame(
                {"Category": list(m["by_category"].keys()),
                 "Count": list(m["by_category"].values())}
            )
            .sort_values("Count", ascending=False)
            .set_index("Category")
        )
        st.bar_chart(cat_df)

    st.divider()

    # --- Filters ------------------------------------------------------------
    st.subheader("Manage Queries")
    f1, f2 = st.columns(2)
    with f1:
        status_filter = st.selectbox(
            "Filter by status", ["All", config.STATUS_OPEN, config.STATUS_CLOSED]
        )
    with f2:
        category_filter = st.selectbox("Filter by category", ["All"] + config.CATEGORIES)

    df = q.get_queries(status=status_filter, category=category_filter)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- Close an open query ------------------------------------------------
    st.subheader("Close an Open Query")
    open_df = q.get_queries(status=config.STATUS_OPEN, category=category_filter)
    if open_df.empty:
        st.info("No open queries to close for the current filter.")
    else:
        open_df = open_df.copy()
        open_df["label"] = (
            "#" + open_df["query_id"].astype(str)
            + " — " + open_df["query_heading"].astype(str)
            + " (" + open_df["category"].astype(str) + ")"
        )
        choice = st.selectbox("Select an open query", open_df["label"].tolist())
        if st.button("Close Selected Query"):
            qid = int(open_df.loc[open_df["label"] == choice, "query_id"].iloc[0])
            q.close_query(qid)
            st.success(f"Query #{qid} has been closed.")
            st.rerun()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    _init_state()

    if not st.session_state.logged_in:
        auth_page()
        return

    with st.sidebar:
        st.write(f"👤 **{st.session_state.username}**")
        st.write(f"Role: {st.session_state.role}")
        st.caption(f"DB: {config.DB_TYPE}")
        if st.button("Logout"):
            logout()
            st.rerun()

    if st.session_state.role == "Client":
        client_page()
    elif st.session_state.role == "Support":
        support_page()
    else:
        st.error("Unknown role. Please log out and register again.")


if __name__ == "__main__":
    main()
