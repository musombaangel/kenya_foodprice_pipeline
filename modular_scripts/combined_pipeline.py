import sys
import os
 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
from prefect import flow, get_run_logger
from extract import extract_raw_data
from clean import clean_data    
from validate import quality_checks
from dbt_runner import perform_staging, run_dbt_build
 
 
@flow(name="wfp-food-prices-pipeline", log_prints=True)
def food_prices_pipeline(csv_path: str = None):
    """
    Extracts, transforms, validates, and loads WFP food prices data into a staging table, then runs dbt build to process the data.
    Steps: 
    1. Extract raw CSV data from local file
    2. Transform: standardize units, clean data
    3. Validate: run data quality checks
    4. Load: load cleaned data into staging table
    5. Process: run dbt build to process the data
    """
    logger = get_run_logger()
    logger.info("Starting the pipeline")
 
    # Extracting raw csv data from local
    if csv_path:
        raw_df = extract_raw_data(csv_path)
    else:
        raw_df = extract_raw_data()
 
    # Transformations
    clean_df = clean_data(raw_df)
 
    # Data Quality confirmation
    validated_df = quality_checks(clean_df)
 
    # Load
    row_count = perform_staging(validated_df)
 
    # dbt build, test
    run_dbt_build()
 
    logger.info(f"Pipeline completed successfully!")
    return row_count
 
 
if __name__ == "__main__":
    food_prices_pipeline('../sheets/wfp_food_prices_ken.csv')