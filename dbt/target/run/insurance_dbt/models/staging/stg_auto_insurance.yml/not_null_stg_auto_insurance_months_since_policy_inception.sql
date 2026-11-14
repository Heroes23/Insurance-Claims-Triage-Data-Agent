
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select months_since_policy_inception
from INSURANCE_DB.ANALYTICS.stg_auto_insurance
where months_since_policy_inception is null



  
  
      
    ) dbt_internal_test