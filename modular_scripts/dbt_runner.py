import subprocess
 
import pandas as pd
from prefect import task, get_run_logger
from sqlalchemy import create_engine, text
 
from config import (
    sql_connection_string,
    staging_schema,
    staging_tb,
    dbt_project_dir,
    dbt_profiles_dir,
)
 
 
@task(name="perform_staging", retries=1)
def perform_staging(df: pd.DataFrame) -> int:
    '''Performs staging of the data by creating a schema if it doesn't 
    exist and loading the DataFrame into a specified table within that schema.'''

    logger = get_run_logger()
    engine = create_engine(sql_connection_string)
 
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {staging_schema}"))
 
    logger.info(
        f"Loading {len(df):,} rows into {staging_schema}.{staging_tb}"
    )
    df.to_sql(
        staging_tb,
        engine,
        schema=staging_schema,
        if_exists="replace",
        index=False,
        chunksize=5000,
    )
 
    logger.info("Staging load complete")
    return len(df)
 
 
@task(name="run_dbt_build", retries=1)
def run_dbt_build() -> str:
    """
    Runs dbt build, which runs and tests all the models
    Similar to running 'dbt run' then 'dbt test'
    """
    logger = get_run_logger()
    logger.info(f"Running `dbt build` in {dbt_project_dir}")
 
    result = subprocess.run(
        ["dbt", "build", "--project-dir", dbt_project_dir, "--profiles-dir", dbt_profiles_dir],
        capture_output=True,
        text=True,
    )
 
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(result.stderr)
        raise RuntimeError(
            f"dbt build failed with exit code {result.returncode}. "
            f"See logs above for the failing model/test."
        )
 
    return result.stdout