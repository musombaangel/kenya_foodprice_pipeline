select *
from {{ ref('dim_market') }}
where
    latitude is null
    or longitude is null
    or latitude < -90 or latitude > 90
    or longitude < -180 or longitude > 180
    or (latitude = 0 and longitude = 0)