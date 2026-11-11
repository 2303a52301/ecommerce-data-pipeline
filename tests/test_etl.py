import pandas as pd
import etl


def test_orders_validation_rejects_bad_rows():
    cust = pd.DataFrame({"customer_id": [1, 2]})
    prod = pd.DataFrame({"product_id": [1]})
    orders = pd.DataFrame({
        "order_id": [1, 1, 2, 3, 4, 5],
        "customer_id": [1, 1, None, 2, 99, 2],
        "product_id": [1] * 6,
        "quantity": [1, 1, 1, -2, 1, 3],
        "order_date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "bad"],
    })
    report = {}
    out = etl.clean_orders(orders, cust, prod, report)
    assert len(out) == 1 and out.iloc[0]["order_id"] == 1
    assert report["orders_duplicates"] == 1
    assert report["orders_invalid_quantity"] == 1


def test_customer_cleaning():
    df = pd.DataFrame({"customer_id": [1, 1], "name": [" bob ", " bob "],
                       "email": [None, None], "signup_date": ["2024-01-01"] * 2})
    out = etl.clean_customers(df, {})
    assert len(out) == 1 and out.iloc[0]["name"] == "Bob" and out.iloc[0]["email"] == "unknown"
