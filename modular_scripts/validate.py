import pandas as pd
from prefect import task, get_run_logger


def quality_checks(df: pd.DataFrame) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info("Running data quality checks")
 
    failures = []
 
    # 1. Required columns must exist
    required_cols = ["date", "market", "commodity", "unit", "price"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        failures.append(f"Missing required columns: {missing_cols}")
 
    if not failures:
        # 2. No nulls in key business columns
        null_counts = df[required_cols].isnull().sum()
        bad_nulls = null_counts[null_counts > 0]
        if not bad_nulls.empty:
            failures.append(f"Null values found: {bad_nulls.to_dict()}")
 
        # 3. Prices must be positive
        non_positive = (df["price"] <= 0).sum()
        if non_positive > 0:
            failures.append(f"{non_positive} rows have price <= 0")
 
        # 4. Dates must be parseable and not in the future
        bad_dates = df["date"].isnull().sum()
        if bad_dates > 0:
            failures.append(f"{bad_dates} rows have unparseable dates")
 
        future_dates = (df["date"] > pd.Timestamp.now()).sum()
        if future_dates > 0:
            failures.append(f"{future_dates} rows have future dates")
 
        # 5. Row count sanity check (catches silent truncation)
        if len(df) < 100:
            failures.append(f"Row count suspiciously low: {len(df)}")
 
    if failures:
        for f in failures:
            logger.error(f"DQ CHECK FAILED: {f}")
        raise ValueError(
            f"{len(failures)} data quality check(s) failed: {failures}"
        )
 
    logger.info(f"All data quality checks passed on {len(df):,} rows")
    return df