
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select vehicle_size
from INSURANCE_DB.ANALYTICS.stg_auto_insurance
where vehicle_size is null



  
  
      
    ) dbt_internal_test