
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select sales_channel
from INSURANCE_DB.ANALYTICS.mart_segment_performance
where sales_channel is null



  
  
      
    ) dbt_internal_test