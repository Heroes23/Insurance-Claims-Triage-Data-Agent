
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        coverage as value_field,
        count(*) as n_records

    from INSURANCE_DB.ANALYTICS.stg_auto_insurance
    group by coverage

)

select *
from all_values
where value_field not in (
    'Basic','Extended','Premium'
)



  
  
      
    ) dbt_internal_test