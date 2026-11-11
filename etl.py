"""E-commerce ETL: extract CSVs -> clean/validate -> star schema -> load to PostgreSQL.

Usage:
    python etl.py                     # uses DB_URL env var, default = local SQLite file
    DB_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce python etl.py
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DB_URL", "sqlite:///warehouse.db")


# ---------- EXTRACT ----------
def extract(path="data/raw"):
    return {n: pd.read_csv(f"{path}/{n}.csv") for n in ("customers", "products", "orders")}


# ---------- CLEAN + DATA QUALITY ----------
def clean_customers(df, report):
    before = len(df)
    df = df.drop_duplicates(subset="customer_id")
    report["customers_duplicates"] = before - len(df)
    report["customers_missing_email"] = int(df["email"].isna().sum())
    df = df.assign(name=df["name"].str.strip().str.title(),
                   email=df["email"].str.strip().str.lower().fillna("unknown"),
                   signup_date=pd.to_datetime(df["signup_date"], errors="coerce"))
    return df


def clean_products(df, report):
    bad = (df["price"] <= 0) | df["price"].isna()
    report["products_invalid_price"] = int(bad.sum())
    return df[~bad].drop_duplicates(subset="product_id")


def clean_orders(df, customers, products, report):
    n0 = len(df)
    df = df.drop_duplicates(subset="order_id")
    report["orders_duplicates"] = n0 - len(df)
    df = df.assign(order_date=pd.to_datetime(df["order_date"], errors="coerce"))
    checks = {
        "orders_missing_customer": df["customer_id"].isna(),
        "orders_invalid_quantity": df["quantity"] <= 0,
        "orders_invalid_date": df["order_date"].isna(),
        "orders_orphan_customer": ~df["customer_id"].isin(customers["customer_id"]) & df["customer_id"].notna(),
        "orders_orphan_product": ~df["product_id"].isin(products["product_id"]),
    }
    reject = pd.Series(False, index=df.index)
    for name, mask in checks.items():
        report[name] = int(mask.sum()); reject |= mask
    report["orders_rejected_total"] = int(reject.sum())
    return df[~reject].astype({"customer_id": int})


# ---------- TRANSFORM ----------
def transform(customers, products, orders):
    dim_customer = customers.rename(columns={"customer_id": "customer_key"}).assign(
        signup_date=lambda d: d["signup_date"].dt.strftime("%Y-%m-%d"))
    dim_product = products.rename(columns={"product_id": "product_key"})
    dates = pd.DataFrame({"full_date": orders["order_date"].dt.normalize().unique()}).sort_values("full_date")
    dim_date = pd.DataFrame({
        "date_key": dates["full_date"].dt.strftime("%Y%m%d").astype(int),
        "full_date": dates["full_date"].dt.strftime("%Y-%m-%d"),
        "year": dates["full_date"].dt.year, "month": dates["full_date"].dt.month,
        "month_name": dates["full_date"].dt.month_name()})
    fact = orders.merge(products[["product_id", "price"]], on="product_id")
    fact_sales = pd.DataFrame({
        "order_id": fact["order_id"], "customer_key": fact["customer_id"],
        "product_key": fact["product_id"],
        "date_key": fact["order_date"].dt.strftime("%Y%m%d").astype(int),
        "quantity": fact["quantity"], "revenue": (fact["quantity"] * fact["price"]).round(2)})
    return dim_customer, dim_product, dim_date, fact_sales


# ---------- LOAD ----------
def load(engine, dim_customer, dim_product, dim_date, fact_sales):
    with open("sql/schema.sql") as f:
        stmts = [s.strip() for s in f.read().split(";") if s.strip()]
    with engine.begin() as conn:
        for s in stmts:
            conn.execute(text(s))
    for name, df in [("dim_customer", dim_customer), ("dim_product", dim_product),
                     ("dim_date", dim_date), ("fact_sales", fact_sales)]:
        df.to_sql(name, engine, if_exists="append", index=False, chunksize=1000)


def run():
    report = {}
    raw = extract()
    customers = clean_customers(raw["customers"], report)
    products = clean_products(raw["products"], report)
    orders = clean_orders(raw["orders"], customers, products, report)
    tables = transform(customers, products, orders)
    load(create_engine(DB_URL), *tables)
    print("=== Data quality report ===")
    for k, v in report.items():
        print(f"{k:28s}{v}")
    print(f"\nLoaded {len(tables[3])} fact rows into {DB_URL.split('@')[-1]}")


if __name__ == "__main__":
    run()
