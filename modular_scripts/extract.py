import pandas as pd
from prefect import task, get_run_logger

csv_path = '../sheets/wfp_food_prices_ken.csv'

@task(name="extract_raw_data", retries=2, retry_delay_seconds=10)
def extract_raw_data(csv_path: str = csv_path) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info(f"Extracting the data")
 
    df = pd.read_csv(csv_path)
 
    if df.empty:
        raise ValueError(f"No data found in the CSV")
 
    logger.info(f"Extracted {len(df):,} rows, {len(df.columns)} columns")
    return df