select distinct
    {{ dbt_utils.generate_surrogate_key(['market', 'admin1', 'admin2']) }} as market_key,
    market,
    admin1,
    admin2,
    latitude,
    longitude
from {{ ref('staging_prices') }}