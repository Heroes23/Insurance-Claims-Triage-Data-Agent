
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select coverage
from INSURANCE_DB.ANALYTICS.stg_auto_insurance
where coverage is null



  
  
      
    ) dbt_internal_test