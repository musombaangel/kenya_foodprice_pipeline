import os
import dotenv

loaded = dotenv.load_dotenv()
 
# connection details
host = 'localhost'
port = 5432
db ="food_project"
user = "postgres"
password = os.getenv("pg_password")
 
sql_connection_string = (
    f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
)
 
#clean data
CSV_PATH = os.getenv("csv_path")
 
# staging
staging_schema = "staging"
staging_tb = "raw_food_prices"
 
# dbt
dbt_project_dir = os.getenv("dbt_dir")
dbt_profiles_dir = os.getenv("dbt_profiles_dir")