import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()
conn = psycopg2.connect(
    dbname="food_project",
    user="postgres",
    password=os.getenv("pg_password"),
    host="localhost",
    port="5432"
)

cur = conn.cursor()

with open("../sheets/wfp_food_prices_ken.csv", "r") as f:
    next(f)
    cur.copy_expert(
        "COPY raw_food_prices(date, admin1, admin2, market, market_id, latitude, category, commodity_id, unit, priceflag, pricetype, currency, price, usdprice, longitude, commodity) FROM STDIN WITH CSV",
        f
    )

conn.commit()
cur.close()
conn.close()

print("Data copied successfully!")
