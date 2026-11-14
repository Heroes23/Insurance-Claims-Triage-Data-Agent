
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  

-- Warns if months since last claim exceeds months since policy inception,
-- which is logically impossible (a claim can't predate the policy).
select
    customer_id,
    months_since_last_claim,
    months_since_policy_inception
from INSURANCE_DB.ANALYTICS.stg_auto_insurance
where months_since_last_claim > months_since_policy_inception
  
  
      
    ) dbt_internal_test