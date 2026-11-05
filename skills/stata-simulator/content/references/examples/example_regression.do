* Example Stata Do-File: Regression Analysis
* Demonstrates regression commands

* Set working directory
cd "/path/to/data"

* Load data
use "analysis_data.dta", clear

* Data preparation
describe
summarize

* Check for missing values
codebook

* Generate derived variables
generate log_income = log(income)
generate age_sq = age^2

* Simple linear regression
regress income education age

* Multiple regression with controls
regress income education age age_sq gender

* Logistic regression
regress满意 binary_satisfaction price quality service

* Display summary
display "Regression analysis completed"
display "R-squared values indicate model fit"

* Save results
save "analysis_results.dta", replace
