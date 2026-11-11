"""Generate synthetic (deliberately messy) e-commerce data into data/raw/."""
import os
import random
import numpy as np
import pandas as pd

random.seed(42); np.random.seed(42)
os.makedirs("data/raw", exist_ok=True)
cities = ["Hyderabad", "Warangal", "Bengaluru", "Chennai", "Mumbai", "Delhi"]
cats = {"Electronics": (999, 45000), "Clothing": (299, 3000), "Home": (199, 8000), "Books": (99, 999)}

customers = pd.DataFrame({
    "customer_id": range(1, 201),
    "name": [f"customer {i}" for i in range(1, 201)],
    "email": [f"user{i}@mail.com" for i in range(1, 201)],
    "city": np.random.choice(cities, 200),
    "signup_date": pd.date_range("2023-01-01", periods=200, freq="2D").strftime("%Y-%m-%d"),
})
customers.loc[[5, 17, 42], "email"] = None                 # missing values
customers = pd.concat([customers, customers.iloc[:5]])    # duplicates

rows = []
for pid in range(1, 51):
    c = random.choice(list(cats)); lo, hi = cats[c]
    rows.append((pid, f"{c} Item {pid}", c, round(random.uniform(lo, hi), 2)))
products = pd.DataFrame(rows, columns=["product_id", "name", "category", "price"])

n = 3000
orders = pd.DataFrame({
    "order_id": range(1, n + 1),
    "customer_id": np.random.randint(1, 201, n),
    "product_id": np.random.randint(1, 51, n),
    "quantity": np.random.randint(1, 6, n),
    "order_date": pd.to_datetime("2024-01-01") + pd.to_timedelta(np.random.randint(0, 365, n), unit="D"),
})
orders["order_date"] = orders["order_date"].dt.strftime("%Y-%m-%d")
orders.loc[[10, 99], "customer_id"] = None                # missing FK
orders.loc[[20, 300], "quantity"] = -1                    # invalid qty
orders.loc[[50], "order_date"] = "not-a-date"             # invalid date
orders.loc[[70], "customer_id"] = 9999                    # orphan customer
orders = pd.concat([orders, orders.iloc[:10]])            # duplicates

customers.to_csv("data/raw/customers.csv", index=False)
products.to_csv("data/raw/products.csv", index=False)
orders.to_csv("data/raw/orders.csv", index=False)
print("Raw data written to data/raw/")
