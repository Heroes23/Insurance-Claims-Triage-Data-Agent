
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Fails if any policy has a zero or negative monthly premium.
select
    customer_id,
    monthly_premium_auto
from INSURANCE_DB.ANALYTICS.stg_auto_insurance
where monthly_premium_auto <= 0
  
  
      
    ) dbt_internal_test