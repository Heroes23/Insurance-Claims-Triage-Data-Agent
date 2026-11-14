with source as (

    select * from {{ source('raw', 'auto_insurance_batches') }}

),

casted as (

    select
        trim(customer)                                  as customer_id,
        trim(state)                                     as state,
        try_to_double(customer_lifetime_value)          as customer_lifetime_value,
        trim(response)                                  as response,
        trim(coverage)                                  as coverage,
        trim(education)                                 as education,

        case
            when length(split_part(effective_to_date, '/', 3)) = 2
                then try_to_date(effective_to_date, 'MM/DD/YY')
            else try_to_date(effective_to_date, 'MM/DD/YYYY')
        end                                             as effective_to_date,

        trim(employment_status)                         as employment_status,
        trim(gender)                                    as gender,
        try_to_number(income)                           as income,
        trim(location_code)                             as location_code,
        trim(marital_status)                            as marital_status,
        try_to_number(monthly_premium_auto)             as monthly_premium_auto,
        try_to_number(months_since_last_claim)          as months_since_last_claim,
        try_to_number(months_since_policy_inception)    as months_since_policy_inception,
        try_to_number(number_of_open_complaints)        as number_of_open_complaints,
        try_to_number(number_of_policies)               as number_of_policies,
        trim(policy_type)                               as policy_type,
        trim(policy)                                    as policy,
        trim(renew_offer_type)                          as renew_offer_type,
        trim(sales_channel)                             as sales_channel,
        try_to_double(total_claim_amount)               as total_claim_amount,
        trim(vehicle_class)                             as vehicle_class,
        trim(vehicle_size)                              as vehicle_size,
        try_to_date(batch_date)                         as batch_date

    from source

)

select
    *,
    monthly_premium_auto * months_since_policy_inception as estimated_earned_premium
from casted