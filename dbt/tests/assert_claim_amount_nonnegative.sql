-- Fails if any policy has a negative total claim amount.
select
    customer_id,
    total_claim_amount
from {{ ref('stg_auto_insurance') }}
where total_claim_amount < 0