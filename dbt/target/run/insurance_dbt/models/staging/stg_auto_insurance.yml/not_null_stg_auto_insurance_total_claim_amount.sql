
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_claim_amount
from INSURANCE_DB.ANALYTICS.stg_auto_insurance
where total_claim_amount is null



  
  
      
    ) dbt_internal_test