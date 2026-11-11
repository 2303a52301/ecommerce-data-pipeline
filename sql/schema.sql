-- Star schema: 1 fact table + 3 dimensions
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_customer (customer_key INTEGER PRIMARY KEY, name TEXT, email TEXT, city TEXT, signup_date DATE);
CREATE TABLE dim_product (product_key INTEGER PRIMARY KEY, name TEXT, category TEXT, price NUMERIC(10,2));
CREATE TABLE dim_date (date_key INTEGER PRIMARY KEY, full_date DATE, year INTEGER, month INTEGER, month_name TEXT);
CREATE TABLE fact_sales (
    order_id INTEGER PRIMARY KEY,
    customer_key INTEGER REFERENCES dim_customer(customer_key),
    product_key INTEGER REFERENCES dim_product(product_key),
    date_key INTEGER REFERENCES dim_date(date_key),
    quantity INTEGER,
    revenue NUMERIC(12,2)
);
