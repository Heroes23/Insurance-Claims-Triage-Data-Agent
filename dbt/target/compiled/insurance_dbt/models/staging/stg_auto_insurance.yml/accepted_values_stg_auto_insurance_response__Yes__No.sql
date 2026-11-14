
    
    

with all_values as (

    select
        response as value_field,
        count(*) as n_records

    from INSURANCE_DB.ANALYTICS.stg_auto_insurance
    group by response

)

select *
from all_values
where value_field not in (
    'Yes','No'
)


