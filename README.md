# Kenya Food Price Pipeline

An ETL pipeline that ingests raw food price data for Kenyan markets and transforms it into an analytics-ready dimensional model, using dbt Core and PostgreSQL.



## Problem Definition
The goal of this project is to track prices of food to determine how volatile they are through time across various regions.



## Architecture
The logic follows an ETL pipeline
1. Raw data is extracted as a CSV and loaded into PostgreSQL with minimal changes.
2. Staging models in dbt clean and standardize the data.
3. Staging tests act as a quality gate before the data moves further downstream.
4. Core and mart DBT models transform the staged data into a star schema for analysis.



## Tech Stack

| Tool | Purpose |
|------|---------|
| **dbt Core** | Transformation and modeling |
| **PostgreSQL** | Data warehouse |
| **Prefect** | Orchestration of the pipeline |
| **pandas** | Data extraction and cleaning |
| **Metabase** | Dashboarding and visualization |
| **python-dotenv** | Managing credentials and environment variables |

---

## Project Structure

```
kenya_foodprice_pipeline/
├── .gitignore
├── README.md
├── errors.md
├── food_project_dbt/
│   ├── dbt_project.yml
│   ├── README.md
│   ├── packages.yml
│   ├── package-lock.yml
│   ├── models/
│   ├── macros/
│   ├── analyses/
│   ├── seeds/
│   ├── snapshots/
│   └── tests/
├── modular_scripts/
│   ├── config.py
│   ├── extract.py
│   ├── clean.py
│   ├── validate.py
│   ├── dbt_runner.py
│   └── combined_pipeline.py
├── scripts/
│   ├── load_data.py
│   ├── clean.py
│   └── eda.ipynb
├── queries/
│   └── analytical_sql3.3_reqs.sql
├── sheets/
│   ├── wfp_food_prices_ken.csv
│   └── wfp_cleaned.csv
└── logs/
    └── dbt.log
```

---

## Raw Data Schema

The raw data pulled has the following structure:

| Column | Type | Notes |
|--------|------|-------|
| date | date | |
| admin1 | varchar(30) | Region |
| admin2 | varchar(30) | Sub-region |
| market | varchar(100) | |
| market_id | integer | |
| latitude | numeric(9,6) | |
| category | varchar(200) | Commodity category |
| commodity_id | integer | |
| unit | varchar(30) | |
| priceflag | varchar(25) | |
| pricetype | varchar(25) | |
| currency | varchar(3) | |
| price | numeric(10,2) | Local currency |
| usdprice | numeric(10,2) | USD equivalent |
| longitude | numeric(9,6) | |
| commodity | varchar(30) | |



## Data Cleaning

Initial cleaning was performed in `scripts/clean.py`, with all issues and resolutions documented in `errors.md`. Key issues addressed:
- Null values
- Inconsistent or non-standardized units
- Data type mismatches



## Exploratory Queries
Queries can be found under `./queries`

The following queries were run to build an understanding of the dataset:

1. **Latest entries per market** — filtering to isolate the most recent price entry for each market.  

2. **Price distribution** — minimum, maximum, and average price aggregations.  

3. **Commodity density** — identifying high-density commodities using a threshold of 10 entries.  

4. **Temporal trends** — comparing price movement across months and years.  


## ETL Pipeline

To keep the codebase organized, the pipeline was broken into modular scripts, all found in `modular_scripts/`. Each script handles one part of the process, and Prefect is used to orchestrate them together. All modules are tied together in `combined_pipeline.py`.

| Script | Function |
|--------|----------|
| `config.py` | Stores pipeline variables, including database configuration |
| `extract.py` | Confirms data availability and extracts it |
| `clean.py` | Handles unit standardization, null values, and data type reconciliation |
| `validate.py` | Confirms all known data issues are resolved before loading |
| `dbt_runner.py` | Runs dbt to stage the data, perform schema checks, and load it downstream |


## Dimensional Model

The raw data was restructured into a star schema, split into the following tables:

### `fct_prices` — Fact table
Contains all foreign keys and price details.

| Column | Type |
|--------|------|
| date_key | text |
| commodity_key | text |
| market_key | text |
| priceflag | varchar(25) |
| pricetype | varchar(25) |
| currency | varchar(3) |
| price | numeric |
| usdprice | numeric |

### `dim_commodity` 
Contains all commodity details

| Column | Type |
|--------|------|
| commodity_key | text |
| commodity | varchar(30) |
| unit | text |

### `dim_date` 
Date breakdown for temporal analysis

| Column | Type |
|--------|------|
| date_key | text |
| price_date | date |
| year | numeric |
| month | numeric |
| quarter | numeric |
| month_name | text |

### `dim_market` 
Cotains market details

| Column | Type |
|--------|------|
| market_key | text |
| market | varchar(100) |
| admin1 | varchar(30) |
| admin2 | varchar(30) |
| latitude | numeric |
| longitude | numeric |



## Data Quality Tests

**Generic tests:**
Found under `food_project_dbt\models\core\__star_schema.yml`
- `unique` and `not_null` tests performed on all primary keys
- `not_null` test performed on all foreign keys

**Singular tests:**
Found under `food_project_dbt\tests`
1. Test to ensure all prices are positive
2. Test to confirm valid coordinates


## Visualization

Dashboarding is done in Metabase. The dashboard focuses on maize price trends.