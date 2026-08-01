WITH raws AS (
    SELECT * FROM {{ source('raw_data', 'raw_food_prices') }}
),

renamed AS (
    SELECT
        date::date AS price_date,
        admin1,
        admin2,
        market,
        COALESCE(latitude, -2.5990) AS latitude,
        COALESCE(longitude, 40.33) AS longitude,
        commodity,
        unit,
        priceflag,
        pricetype,
        currency,
        price::numeric AS raw_price,
        usdprice::numeric AS raw_usdprice,
        --regexp pattern to extract numeric part of the units
        NULLIF(REGEXP_REPLACE(unit, '[^0-9.]', '', 'g'), '')::numeric AS unit_multiplier,
        TRIM(REGEXP_REPLACE(unit, '^[0-9.]+\s*', '')) AS clean_unit
    FROM raws
),

standardized AS (
    SELECT
        *,
        --standardizing the units
        CASE
            WHEN unit_multiplier > 0 THEN raw_price / unit_multiplier
            ELSE raw_price
        END AS price,
        CASE
            WHEN unit_multiplier > 0 THEN raw_usdprice / unit_multiplier
            ELSE raw_usdprice
        END AS usdprice
    FROM renamed
)

SELECT *
FROM standardized