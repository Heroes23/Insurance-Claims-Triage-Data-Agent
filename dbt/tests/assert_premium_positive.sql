-- Fails if any policy has a zero or negative monthly premium.
select
    customer_id,
    monthly_premium_auto
from {{ ref('stg_auto_insurance') }}
where monthly_premium_auto <= 0