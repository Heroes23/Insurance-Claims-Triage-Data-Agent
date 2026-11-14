
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select renew_offer_type
from INSURANCE_DB.ANALYTICS.mart_segment_performance
where renew_offer_type is null



  
  
      
    ) dbt_internal_test