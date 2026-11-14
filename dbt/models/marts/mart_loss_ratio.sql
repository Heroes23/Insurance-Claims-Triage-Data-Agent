select
    state,
    coverage,
    vehicle_class,
    count(*)                                              as policy_count,
    sum(total_claim_amount)                               as total_claim_amount,
    sum(estimated_earned_premium)                         as estimated_earned_premium,
    sum(total_claim_amount)
        / nullif(sum(estimated_earned_premium), 0)        as estimated_loss_ratio
from {{ ref('stg_auto_insurance') }}
group by 1, 2, 3