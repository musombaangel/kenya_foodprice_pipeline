import re
import pandas as pd
from prefect import task, get_run_logger
 
# Matches units with numeric prefix
unit_pattern = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([A-Za-z]+)\s*$")
csv_path = '../sheets/wfp_food_prices_ken.csv'
 
 
def standardize_units(units: str):
    """
    Accepts a unit string, returns (divisor, non-numeric_unit_section).
    """
    #confirm string
    if not isinstance(units, str):
        return 1.0, units
    #check for match
    match = unit_pattern.match(units)
    if match:
        quantity = float(match.group(1))
        clean_unit = match.group(2).upper()
        return quantity, clean_unit
 
    return 1.0, units.strip().upper()
 
 
@task(name="clean_data")
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    '''Cleans the raw data:
    - drops exact duplicate rows
    - handles null values (Tana River Hola)
    - normalizes units and prices'''
    
    logger = get_run_logger()
    logger.info("Starting data cleaning")
 
    df = df.copy()
 
    #drop exact duplicate rows from raw extract
    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"Dropped {before - len(df):,} exact duplicate rows")

    #handle Tana River Hola
    df['market'] = df['market'].str.strip()
    df.loc[df['market']== 'Hola (Tana River)', ['admin2', 'admin1', 'longitude', 'latitude']] = ['Central', 'Tana River', 40.33, -2.5990]
    

    #normalize unit and price
    divisors, clean_units = zip(*df["unit"].map(standardize_units))
    df["unit_divisor"] = divisors
    df["unit"] = clean_units
    df["price"] = df["price"] / df["unit_divisor"]
    df = df.drop(columns=["unit_divisor"])

 
    # convert date column
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
 
    logger.info(f"{len(df):,} rows remain after cleaning")

    #to check cleaning results
    #df.to_csv('../sheets/wfp_cleaned.csv', index=False)

    return df