"""
Generate the synthetic_client_queries.csv dataset.

Columns (per spec):
    query_id, mail_id, mobile_number, query_heading, query_description,
    status (Open/Closed), query_created_time, query_closed_time
plus an extra `category` column used by the support-side filter.

Closed queries get a realistic query_closed_time after their created time; open
queries have an empty query_closed_time.
"""

import random
from datetime import datetime, timedelta

import pandas as pd

import config

random.seed(42)

N_RECORDS = 200

FIRST_NAMES = [
    "john", "sara", "amit", "priya", "david", "lena", "raj", "maria",
    "ken", "nina", "omar", "lucy", "sam", "tara", "leo", "mia",
]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "company.com", "mail.com"]

# Category -> list of (heading, description) templates.
TEMPLATES = {
    "Billing": [
        ("Incorrect invoice amount", "I was charged more than the agreed amount on my latest invoice."),
        ("Refund not received", "I requested a refund two weeks ago but have not received it yet."),
        ("Double payment", "My card was charged twice for the same order."),
        ("Subscription renewal issue", "My subscription renewed even though I had cancelled it."),
    ],
    "Technical": [
        ("Login not working", "I am unable to log in to my account even with the correct password."),
        ("App keeps crashing", "The mobile app crashes every time I open the dashboard."),
        ("Page not loading", "The reports page shows a blank screen and never loads."),
        ("Error during checkout", "I get an error message when I try to complete my purchase."),
    ],
    "Account": [
        ("Cannot reset password", "The password reset email never arrives in my inbox."),
        ("Update email address", "I need to change the email address linked to my account."),
        ("Account locked", "My account is locked after a few failed login attempts."),
        ("Delete my account", "Please help me permanently delete my account and data."),
    ],
    "Shipping": [
        ("Delayed delivery", "My order was supposed to arrive last week but is still in transit."),
        ("Wrong item delivered", "I received a different product than the one I ordered."),
        ("Package damaged", "The package arrived damaged and the item is broken."),
        ("Tracking not updating", "The tracking number has not updated for several days."),
    ],
    "Product": [
        ("Product not working", "The device I purchased stopped working after two days."),
        ("Missing parts", "The box was missing some parts listed in the manual."),
        ("Warranty question", "I would like to know if my product is still under warranty."),
        ("Feature request", "It would be great if the product supported dark mode."),
    ],
    "General": [
        ("How to use feature", "Can you explain how to use the export feature?"),
        ("Business hours", "What are your customer support working hours?"),
        ("Partnership inquiry", "I am interested in a business partnership opportunity."),
        ("General feedback", "I wanted to share some feedback about your service."),
    ],
}


def random_mobile() -> str:
    return "9" + "".join(str(random.randint(0, 9)) for _ in range(9))


def random_email(name: str, idx: int) -> str:
    return f"{name}{random.randint(1, 99)}@{random.choice(DOMAINS)}"


def generate() -> pd.DataFrame:
    rows = []
    start = datetime.now() - timedelta(days=90)

    for i in range(1, N_RECORDS + 1):
        category = random.choice(config.CATEGORIES)
        heading, description = random.choice(TEMPLATES[category])
        name = random.choice(FIRST_NAMES)

        created = start + timedelta(
            days=random.randint(0, 89),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        # ~65% of historical queries are closed.
        is_closed = random.random() < 0.65
        if is_closed:
            status = config.STATUS_CLOSED
            closed = created + timedelta(
                hours=random.randint(1, 120), minutes=random.randint(0, 59)
            )
            closed_str = closed.strftime("%Y-%m-%d %H:%M:%S")
        else:
            status = config.STATUS_OPEN
            closed_str = ""

        rows.append(
            {
                "query_id": i,
                "mail_id": random_email(name, i),
                "mobile_number": random_mobile(),
                "query_heading": heading,
                "query_description": description,
                "category": category,
                "status": status,
                "query_created_time": created.strftime("%Y-%m-%d %H:%M:%S"),
                "query_closed_time": closed_str,
            }
        )

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate()
    df.to_csv(config.DATASET_CSV, index=False)
    print(f"Wrote {len(df)} rows to {config.DATASET_CSV}")
    print(df["status"].value_counts().to_string())
