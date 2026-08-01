-- models/marts/core/dim_date.sql
select distinct
    {{ dbt_utils.generate_surrogate_key(['price_date']) }} as date_key,
    price_date,
    extract(year from price_date) as year,
    extract(month from price_date) as month,
    extract(quarter from price_date) as quarter,
    to_char(price_date, 'Month') as month_name
from {{ ref('staging_prices') }}