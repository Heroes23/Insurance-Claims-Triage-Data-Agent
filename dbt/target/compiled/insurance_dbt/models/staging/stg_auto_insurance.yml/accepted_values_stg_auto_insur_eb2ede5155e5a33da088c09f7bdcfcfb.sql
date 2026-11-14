
    
    

with all_values as (

    select
        vehicle_size as value_field,
        count(*) as n_records

    from INSURANCE_DB.ANALYTICS.stg_auto_insurance
    group by vehicle_size

)

select *
from all_values
where value_field not in (
    'Small','Medsize','Large'
)


