# E-Commerce Data Engineering Pipeline

End-to-end ETL pipeline that extracts messy e-commerce data (customers, products, orders),
cleans and validates it, models it as a **star schema**, loads it into **PostgreSQL**, and answers
business questions with **SQL (joins, CTEs, window functions)**.

## Architecture
```
raw CSVs ──► Extract ──► Clean + Data-quality checks ──► Transform (dims + fact) ──► PostgreSQL ──► SQL analysis / Power BI
```

## Star schema
`fact_sales` (order_id, customer_key, product_key, date_key, quantity, revenue)
joined to `dim_customer`, `dim_product`, `dim_date`.

## Data-quality checks
Duplicate records · missing values · invalid quantities · unparseable dates · orphan foreign keys
(a report with counts is printed on every run).

## Run it
```bash
pip install -r requirements.txt
python generate_data.py          # create synthetic raw data
python etl.py                    # runs on SQLite by default

# PostgreSQL:
docker compose up -d
export DB_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce
python etl.py && python run_analysis.py
pytest
```

## Analysis (sql/analysis.sql)
Monthly revenue with MoM growth (`LAG`) · top customers (`RANK`) · category share (`SUM() OVER()`) ·
best product per category (`ROW_NUMBER() OVER (PARTITION BY ...)`).

## Dashboard
Connect Power BI to PostgreSQL (Get Data → PostgreSQL) and use the fact/dimension tables.
Add a screenshot here: `docs/dashboard.png`.
