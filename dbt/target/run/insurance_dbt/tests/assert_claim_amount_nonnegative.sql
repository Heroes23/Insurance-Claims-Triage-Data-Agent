
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Fails if any policy has a negative total claim amount.
select
    customer_id,
    total_claim_amount
from INSURANCE_DB.ANALYTICS.stg_auto_insurance
where total_claim_amount < 0
  
  
      
    ) dbt_internal_test