
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select state
from INSURANCE_DB.ANALYTICS.mart_loss_ratio
where state is null



  
  
      
    ) dbt_internal_test