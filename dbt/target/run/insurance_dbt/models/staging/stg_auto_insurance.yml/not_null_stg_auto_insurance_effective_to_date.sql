
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select effective_to_date
from INSURANCE_DB.ANALYTICS.stg_auto_insurance
where effective_to_date is null



  
  
      
    ) dbt_internal_test