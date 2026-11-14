
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select response
from INSURANCE_DB.ANALYTICS.stg_auto_insurance
where response is null



  
  
      
    ) dbt_internal_test