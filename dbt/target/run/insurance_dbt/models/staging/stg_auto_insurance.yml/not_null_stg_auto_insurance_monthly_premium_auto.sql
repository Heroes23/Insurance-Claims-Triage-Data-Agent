
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select monthly_premium_auto
from INSURANCE_DB.ANALYTICS.stg_auto_insurance
where monthly_premium_auto is null



  
  
      
    ) dbt_internal_test