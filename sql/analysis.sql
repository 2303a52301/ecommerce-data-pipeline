-- Q1: Monthly revenue + month-over-month growth (CTE + LAG)
WITH monthly AS (
    SELECT d.year, d.month, SUM(f.revenue) AS revenue
    FROM fact_sales f JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month
)
SELECT year, month, ROUND(revenue, 2) AS revenue,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY year, month)) * 100.0
             / LAG(revenue) OVER (ORDER BY year, month), 2) AS mom_growth_pct
FROM monthly ORDER BY year, month;

-- Q2: Top 10 customers by lifetime revenue (RANK)
SELECT * FROM (
    SELECT c.name, c.city, ROUND(SUM(f.revenue), 2) AS total_spent,
           RANK() OVER (ORDER BY SUM(f.revenue) DESC) AS rnk
    FROM fact_sales f JOIN dim_customer c ON f.customer_key = c.customer_key
    GROUP BY c.name, c.city
) t WHERE rnk <= 10;

-- Q3: Category revenue share (window SUM over whole result)
SELECT p.category, ROUND(SUM(f.revenue), 2) AS revenue,
       ROUND(SUM(f.revenue) * 100.0 / SUM(SUM(f.revenue)) OVER (), 2) AS pct_of_total
FROM fact_sales f JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category ORDER BY revenue DESC;

-- Q4: Best-selling product per category (ROW_NUMBER + PARTITION BY)
WITH ranked AS (
    SELECT p.category, p.name, SUM(f.quantity) AS units,
           ROW_NUMBER() OVER (PARTITION BY p.category ORDER BY SUM(f.quantity) DESC) AS rn
    FROM fact_sales f JOIN dim_product p ON f.product_key = p.product_key
    GROUP BY p.category, p.name
)
SELECT category, name, units FROM ranked WHERE rn = 1;
