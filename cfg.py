# -*- coding = utf-8 -*-
"""
Created on Mon Sep 28 05:22:41 2015

@author: Dan
"""


# Designate global default values
# ---------------------------------
# Default ZIP is the ZIP code that is used until one is provided by consumer
DefaultZip = "90650"

# All Gloabl parameters of the form Lowest{SOMETHING}Anywhere and
#   Lowest{SOMETHING}Anywhere are for data validation purposes.  Any entered
#   value of {SOMETHING} outside the range is considered invalid and will be
#   oblitirated and replaced with a system guess.
#   Also, {SOMETHING}Round represents an automatic rounding system guesses
#
# FICO-Income guess model
# The model guesses FICO if income is given or guesses income if FICO is given
# It uses a straight line fit
# Income is always *monthly*
# The slope and intecepts (from income to FICO) are provided
# The guessed quantity is always bounded between a lower and an upper bound
# 640-800 for FICO, $2500-$7500/month for Income
# The guesses quantity is rounded to a set granularity step
# integer for FICO (granularity=1), $100 increments for Income
SlopeFicoFromIncome = 0.00074811*12
InterceptFicoFromIncome = 657.7013707
LowestFicoFromIncome = 640
HighstFicoFromIncome = 800
FicoRound = 1
LowestFicoAnywhere = 400
HighestFicoAnywhere = 900
LowestIncomeFromFico = 2500
HighstIncomeFromFico = 7500
LowestIncomeAnywhere = 0
HighestIncomeAnywhere = 100000
IncomeRound = 100

# The guess formula for debt service expense
# Debt expense guess is a fixed percent of monthly income (10%)
# Guess is rounded to a set granularity step ($25 increment)
DebtPercentofIncome = 0.10
DebtRound = 25

# The guess formula for Trade In value (if there is a Trade In)
# Trade In value is a fixed number of income months (2.0 months income)
# Guess is rounded to a set granularity step ($500 increment)
TradeInIncomeMonths = 2.0
TradeInRound = 500
LowestTradeInAnywhere = 1
HighestTradeInAnywhere = 250000

# The guess formulas for ideal and maximum down payment
# Ideal Down Payment is a fixed number of income months (1.0 months income),
#   with a minimum of $0 and a maximum of $5000
# Maximum Down Payment is a fixed number of income months (2.0 months income)
#   with a minimum of $2000 and a maximum of $20,000
# Both guesses are rounded to a set granularity step ($100 increment)
UpfrontWantedIncomeMonths = 1.0
LowestUpfrontWanted = 0.0
HighestUpfrontWanted = 5000.0
UpfrontMaxIncomeMonths = 2.0
LowestUpfrontMax = 2000.0
HighestUpfrontMax = 20000.0
UpfrontRound = 100
LowestUpfrontAnywhere = 0
HighestUpfrontAnywhere = 250000

# The guess formulas for ideal and maximum monthly payment
# Ideal Monthly Payment is a fixed percent of monthly income (8%),
#   with a minimum of $100 and a maximum of $2500
# Maximum Monthly Payment is a fixed percent of monthly income (18%),
#   with a minimum of $200 and a maximum of $5000
# Both guesses are rounded to a set granularity step ($10 increment)
MonthlyWantedPercentofIncome = 0.08
LowestMonthlyWanted = 100.0
HighestMonthlyWanted = 2500.0
MonthlyMaxPercentofIncome = 0.18
LowestMonthlyMax = 200.0
HighestMonthlyMax = 5000.0
MonthlyRound = 10
LowestMonthlyAnywhere = 0
HighestMonthlyAnywhere = 10000

# The guess for loan term wanted by the consumer (always = 72)
TermWanted = '72'
TermRound = 12
LowestTermAnywhere = 12
HighestTermAnywhere = 84

# To avoid cluttering the Make, Model, and Trim menues with many rare choices
# (like Aston Martin), a cutoff is set.  Only the most popular (in the
# database) Make-Model-Trims combinations generate their own menue entries;
# the rest are collectively identified as "other."  The cut-off determines
# what percent of the total vehicle population will have menue entries.
# The cut-off is set at 80% for prototyping (to keep clutter farther down),
# and will be raised to 97% for the ALPHA system
#TrimTopPct = 0.97
TrimTopPct = 0.80

# If all guessing mechanisms to surmise the make-model-trim desired by the
# consumer are unable to generate a guess; the universal default is the most
# popular combination in the data base (Ford F-150 XLT)
DefaultMake = "FORD"
DefaultModel = "F150"
DefaultTrim = "XLT"

# The number of vehicles presented to the consumer in each curation row (4)
SelectionsShown = 4

# Shipping cost estimation model
# The model estimates cost based on distance (in miles) only
# The model is a combination of two straight-line fits.
# For short distances (under 600 miles):
#   Shipping Cost = $131.89 + $0.917 per mile
# For long distances (over 600 miles):
#   Shipping Cost = $483.24 + $0.368 per mile
ShippingBreakPoint = 600
ShippingLowSlope = 0.916867018
ShippingLowIntercept = 131.8910586
ShippingHighSlope = 0.367545642
ShippingHighIntercept = 483.242475
ShippingMissing = 500

# For data integrity purposes, vehicles with selling price below $3000
# are considered invalid and not displayed
LowestValidSellingPrice = '3000'

SALT = """1btR 7SL_rdKfA*WP&_[$'4^Tw3.I"""
# Designate file location of database
# -----------------------------------
FnameDB = "data/PrototypeDB.db"
UserDBFile = "data/UserDB.db"
ConsumersShelve = "data/ConsumersShelve"

