
    
    

with all_values as (

    select
        state as value_field,
        count(*) as n_records

    from INSURANCE_DB.ANALYTICS.stg_auto_insurance
    group by state

)

select *
from all_values
where value_field not in (
    'Arizona','California','Nevada','Oregon','Washington'
)


