import pandas as pd
from prefect import task, get_run_logger


def quality_checks(df: pd.DataFrame) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info("Running data quality checks")
 
    failures = []
 
    # check for required cols
    required_cols = ["date", "market", "commodity", "unit", "price"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        failures.append(f"Missing required columns: {missing_cols}")
 
    if not failures:
        # check for no nulls in required cols
        null_counts = df[required_cols].isnull().sum()
        bad_nulls = null_counts[null_counts > 0]
        if not bad_nulls.empty:
            failures.append(f"Null values found: {bad_nulls.to_dict()}")
 
        #Ensure date column is not a future value
        future_dates = (df["date"] > pd.Timestamp.now()).sum()
        if future_dates > 0:
            failures.append(f"{future_dates} rows have future dates")
 
    if failures:
        for f in failures:
            logger.error(f"DQ CHECK FAILED: {f}")
        raise ValueError(
            f"{len(failures)} data quality check(s) failed: {failures}"
        )
 
    logger.info(f"All data quality checks passed on {len(df):,} rows")
    return df