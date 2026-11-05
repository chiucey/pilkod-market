* Example Stata Do-File: Basic Data Analysis
* This is a sample do-file demonstrating common Stata commands

* Load the dataset
use "auto.dta", clear

* Describe the dataset
describe

* List first 10 observations
list in 1/10

* Generate summary statistics
summarize

* Summarize specific variables
summarize price mpg weight

* Calculate correlations
correlate price mpg weight length

* Create a new variable
generate log_price = log(price)

* Replace values
replace log_price = 0 if missing(log_price)

* List variables
list price log_price in 1/5

* Sort by price
sort price

* Display results
display "Analysis complete!"
