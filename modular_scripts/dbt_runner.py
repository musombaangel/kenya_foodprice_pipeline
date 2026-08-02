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
    '''Performs staging of the data and incremental logic: 
    - creates the schema/table if non-existent
    - inserts only non-duplicate rows.'''

    logger = get_run_logger()
    engine = create_engine(sql_connection_string)
    temp_tb = f"{staging_tb}_incoming"

    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {staging_schema}"))

        table_exists = conn.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = :schema AND table_name = :table)"
            ),
            {"schema": staging_schema, "table": staging_tb},
        ).scalar()

    if not table_exists:
        # loads everything for the first run
        logger.info(f"Creating {staging_schema}.{staging_tb}")
        df.to_sql(
            staging_tb, engine, schema=staging_schema,
            if_exists="fail", index=False, chunksize=5000,
        )
        logger.info(f"Created table with {len(df):,} rows")
        return len(df)

    # Not first run: stage incoming rows, then insert only the new ones
    logger.info(f"Staging {len(df):,} incoming rows into temp table {temp_tb}")
    df.to_sql(
        temp_tb, engine, schema=staging_schema,
        if_exists="replace", index=False, chunksize=5000,
    )

    col_list = ", ".join(df.columns)

    insert_sql = f"""
        INSERT INTO {staging_schema}.{staging_tb} ({col_list})
        SELECT {col_list} FROM {staging_schema}.{temp_tb}
        EXCEPT
        SELECT {col_list} FROM {staging_schema}.{staging_tb}
    """

    with engine.begin() as conn:
        result = conn.execute(text(insert_sql))
        conn.execute(text(f"DROP TABLE {staging_schema}.{temp_tb}"))
        total_rows = conn.execute(
            text(f"SELECT count(*) FROM {staging_schema}.{staging_tb}")
        ).scalar()

    logger.info(
        f"Inserted {result.rowcount:,} new rows, "
        f"{total_rows:,} total rows in {staging_schema}.{staging_tb}"
    )
    return total_rows
 
 
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