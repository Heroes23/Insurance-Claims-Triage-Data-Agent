
    
    

with all_values as (

    select
        policy_type as value_field,
        count(*) as n_records

    from INSURANCE_DB.ANALYTICS.stg_auto_insurance
    group by policy_type

)

select *
from all_values
where value_field not in (
    'Corporate Auto','Personal Auto','Special Auto'
)


