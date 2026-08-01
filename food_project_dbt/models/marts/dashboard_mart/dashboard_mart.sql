{{ config(materialized='view') }}

SELECT
    d.year,
    d.month,
    c.commodity,
    m.admin1,
    AVG(f.price) AS avg_price,
    AVG(f.usdprice) AS avg_usdprice,
    COUNT(*) AS observation_count
FROM {{ ref('fct_prices') }} f
JOIN {{ ref('dim_date') }} d
    ON f.date_key = d.date_key
JOIN {{ ref('dim_commodity') }} c
    ON f.commodity_key = c.commodity_key
JOIN {{ ref('dim_market') }} m
    ON f.market_key = m.market_key
GROUP BY 1, 2, 3, 4