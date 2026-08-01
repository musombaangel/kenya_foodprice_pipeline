with stg as (
    select * from {{ ref('staging_prices') }}
),

dates as (select * from {{ ref('dim_date') }}),
commodities as (select * from {{ ref('dim_commodity') }}),
markets as (select * from {{ ref('dim_market') }})

select
    d.date_key,
    c.commodity_key,
    m.market_key,
    stg.priceflag,
    stg.pricetype,
    stg.currency,
    stg.price,
    stg.usdprice
from stg
join dates d on stg.price_date = d.price_date
join commodities c on stg.commodity = c.commodity and stg.clean_unit = c.unit
join markets m on stg.market = m.market and stg.admin1 = m.admin1 and stg.admin2 = m.admin2