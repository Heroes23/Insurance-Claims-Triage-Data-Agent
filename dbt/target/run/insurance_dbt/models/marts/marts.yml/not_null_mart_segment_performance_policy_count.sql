
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select policy_count
from INSURANCE_DB.ANALYTICS.mart_segment_performance
where policy_count is null



  
  
      
    ) dbt_internal_test