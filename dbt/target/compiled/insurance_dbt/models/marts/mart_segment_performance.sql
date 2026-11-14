select
    sales_channel,
    renew_offer_type,
    count(*)                                              as policy_count,
    avg(customer_lifetime_value)                          as avg_customer_lifetime_value,
    avg(monthly_premium_auto)                             as avg_monthly_premium,
    avg(total_claim_amount)                               as avg_total_claim_amount,
    count_if(response = 'Yes') / nullif(count(*), 0)      as renewal_response_rate
from INSURANCE_DB.ANALYTICS.stg_auto_insurance
group by 1, 2