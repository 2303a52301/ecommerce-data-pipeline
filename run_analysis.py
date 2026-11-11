"""Run the analytical queries in sql/analysis.sql and print results."""
import os
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(os.getenv("DB_URL", "sqlite:///warehouse.db"))
with open("sql/analysis.sql") as f:
    queries = [q.strip() for q in f.read().split(";") if "SELECT" in q]
for q in queries:
    print("\n" + q.splitlines()[0])
    print(pd.read_sql(q, engine).to_string(index=False))
