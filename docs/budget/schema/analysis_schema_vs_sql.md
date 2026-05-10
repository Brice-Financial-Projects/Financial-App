# Analysis Schema vs SQL

This document compares the analysis schema used in our budgeting application with SQL queries for data retrieval and manipulation. It aims to provide insights into the advantages and limitations of each approach, helping developers make informed decisions when working with the application's data.

## User Table
| Diagram Column | SQL Column    | Match / Notes |
| -------------- | ------------- | ------------- |
| User ID        | id            | ✅ Exact match |
| username       | username      | ✅ Exact match |
| email          | email         | ✅ Exact match |
| password_hash  | password_hash | ✅ Exact match |
| created_at     | created_at    | ✅ Exact match |
| is_admin       | is_admin      | ✅ Exact match |

## Profiles Table
| Diagram Column           | SQL Column                     | Match / Notes                              |
| ------------------------ | ------------------------------ | ------------------------------------------ |
| id                       | id                             | ✅ Exact match                              |
| user_id                  | user_id                        | ✅ Exact match                              |
| first_name               | first_name                     | ✅ Exact match                              |
| last_name                | last_name                      | ✅ Exact match                              |
| date_of_birth            | date_of_birth                  | ✅ Exact match                              |
| is_blind                 | is_blind                       | ✅ Exact match                              |
| is_student               | is_student                     | ✅ Exact match                              |
| state                    | state                          | ✅ Exact match                              |
| filing_status            | filing_status                  | ✅ Exact match                              |
| num_dependents           | num_dependents                 | ✅ Exact match                              |
| income_type              | income_type                    | ✅ Exact match                              |
| pay_cycle                | pay_cycle                      | ✅ Exact match                              |
| fed_add_withholding      | federal_additional_withholding | ⚠ Minor name difference                    |
| state_add_withholding    | state_additional_withholding   | ⚠ Minor name difference                    |
| retire_contribution_type | retirement_contribution_type   | ⚠ Minor name difference (`retirement_...`) |
| retire_contribution      | retirement_contribution        | ⚠ Minor name difference                    |
| health_ins_prem          | health_insurance_premium       | ⚠ Minor name difference                    |
| hsa_contribution         | hsa_contribution               | ✅ Exact match                              |
| fsa_contribution         | fsa_contribution               | ✅ Exact match                              |
| other_pretax_benefits    | other_pretax_benefits          | ✅ Exact match                              |
| benefit_deductions       | benefit_deductions             | ✅ Exact match                              |


## Budgets Table
| Diagram Column      | SQL Column              | Match / Notes           |
| ------------------- | ----------------------- | ----------------------- |
| id                  | id                      | ✅ Exact match           |
| user_id             | user_id                 | ✅ Exact match           |
| profile_id          | profile_id              | ✅ Exact match           |
| name                | name                    | ✅ Exact match           |
| gross_income        | gross_income            | ✅ Exact match           |
| retire_contribution | retirement_contribution | ⚠ Minor name difference |
| benefit_deduct      | benefit_deductions      | ⚠ Minor name difference |
| status              | status                  | ✅ Exact match           |
| created_at          | created_at              | ✅ Exact match           |
| updated_at          | updated_at              | ✅ Exact match           |


## Budget Items Table
| Diagram Column | SQL Column        | Match / Notes                               |
| -------------- | ----------------- | ------------------------------------------- |
| id             | id                | ✅ Exact match                               |
| budget_id      | budget_id         | ✅ Exact match                               |
| category       | category          | ✅ Exact match                               |
| name           | name              | ✅ Exact match                               |
| min_payment    | minimum_payment   | ⚠ Name difference (`min_payment` in SQL)    |
| prefer_payment | preferred_payment | ⚠ Name difference (`prefer_payment` in SQL) |


## Gross Income Table
| Diagram Column | SQL Column    | Match / Notes |
| -------------- | ------------- | ------------- |
| id             | id            | ✅ Exact match |
| budget_id      | budget_id     | ✅ Exact match |
| category       | category      | ✅ Exact match |
| source         | source        | ✅ Exact match |
| gross_income   | gross_income  | ✅ Exact match |
| frequency      | frequency     | ✅ Exact match |
| tax_type       | tax_type      | ✅ Exact match |
| state_tax_ref  | state_tax_ref | ✅ Exact match |
| created_at     | created_at    | ✅ Exact match |


## Other Income Table
| Diagram Column | SQL Column | Match / Notes |
| -------------- | ---------- | ------------- |
| id             | id         | ✅ Exact match |
| budget_id      | budget_id  | ✅ Exact match |
| category       | category   | ✅ Exact match |
| source         | source     | ✅ Exact match |
| amount         | amount     | ✅ Exact match |
| frequency      | frequency  | ✅ Exact match |
| created_at     | created_at | ✅ Exact match |


## Summary of Differences:

- Mostly naming differences (e.g., fed_add_withholding → federal_additional_withholding, benefit_deduct → benefit_deductions). Functionally equivalent.
- `budget_items` column names min_payment / prefer_payment are slightly shorter than the diagram.
- All relationships and foreign keys are present.

> ✅ Overall, this SQL will produce a schema fully compatible with the diagram, with only minor naming adjustments needed if an exact match is needed with the field names.
