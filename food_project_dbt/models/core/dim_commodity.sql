select distinct
    {{ dbt_utils.generate_surrogate_key(['commodity', 'clean_unit']) }} as commodity_key,
    commodity,
    clean_unit as unit
from {{ ref('staging_prices') }}