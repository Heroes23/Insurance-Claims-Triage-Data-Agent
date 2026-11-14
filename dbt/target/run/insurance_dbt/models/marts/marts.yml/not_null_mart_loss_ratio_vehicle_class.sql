
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select vehicle_class
from INSURANCE_DB.ANALYTICS.mart_loss_ratio
where vehicle_class is null



  
  
      
    ) dbt_internal_test