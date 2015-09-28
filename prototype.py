# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 03:08:50 2015

@author: Dan

This file contains the Prototype Project

Protocol to upload to PythonAnywhere
------------------------------------

1. In origin machine, zip together the static and templates directories and
    the file Prototype_Main.py
    Name the zipped file "Prototype.zip" (replacing any prior such file)
2. Go to PythonAnywhere login page:  https://www.pythonanywhere.com/login/
    USERNAME = dshoham@carzumer.com  /  PASSWORD = carzumer
3. Click FILES (top left)
4. Upload the file "Prototype.zip" from the main directory
5. Press the "DASHBOARD" link (upper right)
6. Click CONSOLES
7. Kill all active consoles (under YOUR CONSOLES:)
8. Click Bash
     A console will open with a ~ $ prompt.
9. Type: "unzip filename.zip"
     A long series of "inflating: ... " lines will appear
     If you are asked "replace [something]? respond "A" (for All)
10. Type "Python Prototype_Main.py"
    This will start the service and print out various SQL code
11. Click "DASHBOARD" (again)
12. Click WEB
13. Press the big green button "RELOAD".  This should do it!
14. Go to danshoham.pythonanywhere.com to see it live

"""

# Import section
# --------------
import web # This is web.py -- central to the prototype
import os  # This connects with the operating system for file management
import collections  # Provides some functions for managing arrays and lists
import sqlite3 # This is the SQL engine in use.
import math # needed for trigonometric computations in geo-distance functions


# Designate global default values
# ---------------------------------
# Default ZIP is the ZIP code that is used until one is provided by consumer
G_DefaultZip = "90650"

# All Gloabl parameters of the form G_Lowest{SOMETHING}Anywhere and
#   G_Lowest{SOMETHING}Anywhere are for data validation purposes.  Any entered
#   value of {SOMETHING} outside the range is considered invalid and will be
#   oblitirated and replaced with a system guess.
#   Also, G_{SOMETHING}Round represents an automatic rounding system guesses
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
G_SlopeFicoFromIncome = 0.00074811*12
G_InterceptFicoFromIncome = 657.7013707
G_LowestFicoFromIncome = 640
G_HighstFicoFromIncome = 800
G_FicoRound = 1
G_LowestFicoAnywhere = 400
G_HighestFicoAnywhere = 900
G_LowestIncomeFromFico = 2500
G_HighstIncomeFromFico = 7500
G_LowestIncomeAnywhere = 0
G_HighestIncomeAnywhere = 100000
G_IncomeRound = 100

# The guess formula for debt service expense
# Debt expense guess is a fixed percent of monthly income (10%)
# Guess is rounded to a set granularity step ($25 increment)
G_DebtPercentofIncome = 0.10
G_DebtRound = 25

# The guess formula for Trade In value (if there is a Trade In)
# Trade In value is a fixed number of income months (2.0 months income)
# Guess is rounded to a set granularity step ($500 increment)
G_TradeInIncomeMonths = 2.0
G_TradeInRound = 500
G_LowestTradeInAnywhere = 1
G_HighestTradeInAnywhere = 250000

# The guess formulas for ideal and maximum down payment
# Ideal Down Payment is a fixed number of income months (1.0 months income),
#   with a minimum of $0 and a maximum of $5000
# Maximum Down Payment is a fixed number of income months (2.0 months income)
#   with a minimum of $2000 and a maximum of $20,000
# Both guesses are rounded to a set granularity step ($100 increment)
G_UpfrontWantedIncomeMonths = 1.0
G_LowestUpfrontWanted = 0.0
G_HighestUpfrontWanted = 5000.0
G_UpfrontMaxIncomeMonths = 2.0
G_LowestUpfrontMax = 2000.0
G_HighestUpfrontMax = 20000.0
G_UpfrontRound = 100
G_LowestUpfrontAnywhere = 0
G_HighestUpfrontAnywhere = 250000

# The guess formulas for ideal and maximum monthly payment
# Ideal Monthly Payment is a fixed percent of monthly income (8%),
#   with a minimum of $100 and a maximum of $2500
# Maximum Monthly Payment is a fixed percent of monthly income (18%),
#   with a minimum of $200 and a maximum of $5000
# Both guesses are rounded to a set granularity step ($10 increment)
G_MonthlyWantedPercentofIncome = 0.08
G_LowestMonthlyWanted = 100.0
G_HighestMonthlyWanted = 2500.0
G_MonthlyMaxPercentofIncome = 0.18
G_LowestMonthlyMax = 200.0
G_HighestMonthlyMax = 5000.0
G_MonthlyRound = 10
G_LowestMonthlyAnywhere = 0
G_HighestMonthlyAnywhere = 10000

# The guess for loan term wanted by the consumer (always = 72)
G_TermWanted = '72'
G_TermRound = 12
G_LowestTermAnywhere = 12
G_HighestTermAnywhere = 84

# To avoid cluttering the Make, Model, and Trim menues with many rare choices
# (like Aston Martin), a cutoff is set.  Only the most popular (in the
# database) Make-Model-Trims combinations generate their own menue entries;
# the rest are collectively identified as "other."  The cut-off determines
# what percent of the total vehicle population will have menue entries.
# The cut-off is set at 80% for prototyping (to keep clutter farther down),
# and will be raised to 97% for the ALPHA system
#G_TrimTopPct = 0.97
G_TrimTopPct = 0.80

# If all guessing mechanisms to surmise the make-model-trim desired by the
# consumer are unable to generate a guess; the universal default is the most
# popular combination in the data base (Ford F-150 XLT)
G_DefaultMake = "FORD"
G_DefaultModel = "F150"
G_DefaultTrim = "XLT"

# The number of vehicles presented to the consumer in each curation row (4)
G_SelectionsShown = 4

# Shipping cost estimation model
# The model estimates cost based on distance (in miles) only
# The model is a combination of two straight-line fits.
# For short distances (under 600 miles):
#   Shipping Cost = $131.89 + $0.917 per mile
# For long distances (over 600 miles):
#   Shipping Cost = $483.24 + $0.368 per mile
G_ShippingBreakPoint = 600
G_ShippingLowSlope = 0.916867018
G_ShippingLowIntercept = 131.8910586
G_ShippingHighSlope = 0.367545642
G_ShippingHighIntercept = 483.242475
G_ShippingMissing = 500


# Designate file location of database
# -----------------------------------
FnameDB = "data/PrototypeDB.db"


# Global Functions
# ----------------


def isNull(v):
    return (v == "") or (v == None)


def fixNull(v, fix=""):
    if isNull(v):
        return fix
    else:
        return v


def fixZero(v, fix=""):
    if isNull(v) or (str(v) == "0"):
        return fix
    else:
        return v


def float0(s):
    if (s == "") or (s == None) or (s == "#N/A") or (s == "."):
        return 0
    else:
        try:
            return max(0, float(s))
        except ValueError:
            return 0
        except:
            print "Unexpected Error in float0:"
            print "s = " + str(s)
            raise


def strRound(v, multiple=1, minimum=0, maximum=1000000):
    # Returns a string value of v rounded to nearest (integer) multiple
    # This function is used when guesses are made.  Since consumer selections
    # are always stored as strings, the value is converted out of its string
    # form, rounded, and converted back.
    # Will return blank for error conditions
    if isNull(v): return ""
    try:
        numeric = int(float(v)/multiple + 0.5) * multiple
        if (numeric >= minimum) and (numeric <= maximum):
            return str(numeric)
        else:
            return ""
    except ValueError:
        return ""
    except:
        print "Unexpected error in strRound:"
        print "v = " + str(v)
        print "multiple = " + str(multiple)
        print "minimum = " + str(minimum)
        print "maximum = " + str(maximum)
        raise


# Classes
# -------

class byZIP (object):
    # Reads, from a database, various tables by ZIP5
    # There is only one member of this class (MyZip)
    # MyZip is initialized once (at startup), and is then used many times
    # Each table is turned into a dictionary, with the ZIP as the key
    # and the look-up value as the value.
    # After initialization, calling MyZip.TableName[ZipCode] will return
    # the table look-up for that zip code.
    # For example:  MyZip.ST2['92024'] will return 'CA' (the US state)
    # The tables are:
    #   Income  -- median income
    #   ST2     -- 2 letter US state
    #   ST2Offset--The number of FICO points that state is above (or below,
    #              when negative) above the modeled number for its median
    #              income.  (Used to calculate FICO guess from income)
    #   FICO3   -- The modeled FICO guess for the Zip (used for FICO guess)
    #   Latitude, Longitude -- Geodesic coordinates of the zip code (used to
    #                          compute distances from dealers to consumers)
    #   TaxRate -- Sales tax rate in effect
    #   TradeInTaxCredit -- 1 for states that give Sales Tax Credit for Trade-
    #                       In's, 0 for states that do not
    def __init__(self):
        MyDB = sqlite3.connect(FnameDB)
        cur = MyDB.cursor()
        MyScript = """SELECT ZIP, Income, state, ST2Offset, FICO3,
                          Latitude, Longitude, SalesTax, TradeInTaxCredit
                      FROM ZipLatLon;"""
        cur.execute(MyScript)
        Results = cur.fetchall()
        MyDB.commit()
        MyDB.close()
        self.Income = {}
        self.ST2 = {}
        self.ST2offset = {}
        self.FICO3 = {}
        self.Latitude = {}
        self.Longitude = {}
        self.TaxRate = {}
        self.TradeInTaxCredit = {}
        for row in Results:
            self.Income.update({row[0]: float0(row[1])/12})
            self.ST2.update({row[0]: row[2]})
            self.ST2offset.update({row[0]: float0(row[3])})
            self.FICO3.update({row[0]: row[4]})
            self.Latitude.update({row[0]: row[5]})
            self.Longitude.update({row[0]: row[6]})
            self.TaxRate.update({row[0]: row[7]})
            self.TradeInTaxCredit.update({row[0]: row[8]})


class APRTable (object):
    # Reads, from database, a table of APR by FICO, LTV, and Term
    # There is only one member of this class (MyAPR)
    # MyAPR is initialized once (at startup), and is then used many times
    # Two dictionaries are available: APRGrid and MonthlyGrid
    # APRGrid is a dictionary from the 3-tuplet of (FICO, LTV, Term) to APR
    # Each of the 3 quantities is on an equispaced grid.
    # The class elements LowFico, HighFico, and StepFico define the gridpoints
    #   (Likewise LowLTV, HighLTV and StepLTV; and LowTerm, HighTerm, StepTerm)
    # For example, MyAPR.APRGrid[(690, 0.9, 72)] will provide the APR for
    #   a 72 months term loan at 90% LTV to a FICO 690 borrower
    # Similarly, MonthlyGrid will provide the monthly payment (as a percentage
    #   of loan amount) for a given FICO-LTV-Term tuplet
    # The Methods GetAPR and GetMonthly will return the APR and Monthly,
    #   respectively, for any numeric FICO and LTV; even if not on the grid.
    #   (Term must always be on the grid)
    # For example: MyAPR.GetAPR(711, 0.92, 60) will provide the APR for a
    #    60 months term loan at 90% LTV to a FICO 710 borrower.
    # Both methods return 0 for erroneous and unfixable parameters
    def __init__(self):
        MyDB = sqlite3.connect(FnameDB)
        cur = MyDB.cursor()
        MyScript = """SELECT FICO, LTV, Term, APR, Monthly
                      FROM APR;"""
        cur.execute(MyScript)
        Results = cur.fetchall()
        MyDB.commit()
        MyDB.close()
        self.APRGrid = {(0,0,0): 0}
        self.MonthlyGrid = {(0,0,0): 0}
        self.LowFico = int(Results[0][0])
        self.HighFico = self.LowFico
        self.StepFico = 1000
        self.LowLTV = int(Results[0][1])
        self.HighLTV = self.LowLTV
        self.StepLTV = 1000
        self.LowTerm = int(Results[0][2])
        self.HighTerm = self.LowTerm
        self.StepTerm = 1000

        for row in Results:
            Fico = int(row[0])
            LTV = int(row[1])
            Term = int(row[2])
            APR = float(row[3])
            Monthly = float(row[4])
            self.APRGrid.update({(Fico, LTV, Term): APR})
            self.MonthlyGrid.update({(Fico, LTV, Term): Monthly})
            self.HighFico = max(self.HighFico, Fico)
            self.HighLTV = max(self.HighLTV, LTV)
            self.HighTerm = max(self.HighTerm, Term)
            if Fico > self.LowFico:
                self.StepFico = min(self.StepFico, Fico - self.LowFico)
            if LTV > self.LowLTV:
                self.StepLTV = min(self.StepLTV, LTV - self.LowLTV)
            if Term > self.LowTerm:
                self.StepTerm = min(self.StepTerm, Term - self.LowTerm)


    def CleanDeal(self, sFICO, pLTV, sTerm):
        # This function will clean up the sFICO, pLTV, and sTerm
        # parameters, so they can be used to find APR and Monthly payment
        # If uncleanable, return 0-0-0; else, return Fico-LTV-Term
        # The returned values will correspond to a grid point on the
        # tabulated APRGrid and MonthlyGrid dictionaries
        try:
            if isNull(sFICO):
                FICO = self.LowFico
            else:
                FICO = max(self.LowFico, min(self.HighFico, float(sFICO)))
                FICO = int(round((FICO - self.LowFico)/self.StepFico) *
                            self.StepFico + self.LowFico)

            LTV = max(self.LowLTV, min(self.HighLTV, 100.0 * pLTV))
            LTV = int(round((LTV - self.LowLTV)/self.StepLTV) *
                        self.StepLTV + self.LowLTV)

            Term = int(fixNull(sTerm,G_TermWanted))
            if (Term < self.LowTerm) or (Term > self.HighTerm) or \
                ( (Term - self.LowTerm) % self.StepTerm != 0):
                    return (0,0,0)

            return (FICO, LTV, Term)
        except ValueError:
            return  (0,0,0)
        except:
            print "Unexpected error in CleanDeal:"
            print "sFICO = " + str(sFICO)
            print "pLTV = " + str(pLTV)
            print "sTerm = " + str(sTerm)
            raise


    def GetAPR(self, sFICO, pLTV, sTerm):
        # Returns the tabulated APR for a prospective loan
        # Will return 0 for error conditions (uncleanable inputs)
        return self.APRGrid[self.CleanDeal(sFICO, pLTV, sTerm)]


    def GetMonthly(self, sFICO, pLTV, sTerm):
        # Returns the tabulated Monthly payment for a prospective loan
        #   (as a percentage of loan amount)
        # Will return 0 for error conditions (uncleanable inputs)
        return self.MonthlyGrid[self.CleanDeal(sFICO, pLTV, sTerm)]


class TrimTop (object):
    # Reads, from a database, The list of all Make-Model-Trim combinations
    # There is only one member of this class (MMList)
    # MMList is initialized once (at startup), and is then used many times
    # A global setting G_TrimTopPct (80%) determines which combination will
    #   be incorporated into the menus (all others will fall under "others")
    #   This is to prevent the menues from being cluttered with rare choices
    # In the database, field "CUM_PCT_NEW" provides the prevalence of each
    #   Make-Model-Trim combination.  If it is <= 80%, the combination is
    #   sufficiently common to generate menue choices for the consumer
    # The class generates two dictionaries: MakesDict and ModelsDict
    # The MakesDict dictionary provides a mapping from the Make to an array of
    #   Models.  Only Makes common enough to meet the threshold have entries,
    #   and only common-enough Models are represented in the array.
    #   For example: MMList.MakesDict['HYUNDAI'] returns ['ACCENT', 'AZERA' , 'ELANTRA', 'SONATA']
    # Likewise, the ModelsDict dictionary provides a mapping from each
    #   represented Make-Model combination (represented as MAKE(MODEL) ) to an
    #   array of represented Trims.
    #   For example: MMList.ModelsDict['HYUNDAI(ELANTRA)'] returns ['', 'GLS PZEV', 'LIM PZEV']
    def __init__(self):

        MyDB = sqlite3.connect(FnameDB)
        cur = MyDB.cursor()
        MyScript = """SELECT NUMBER, STD_MAKE, STD_MODEL, STD_TRIM,
                          COUNT_NEW, COUNT_ALL, PCT_NEW, CUM_PCT_NEW
                      FROM Trim_Top;"""
        cur.execute(MyScript)
        Results = cur.fetchall()
        MyDB.commit()
        MyDB.close()

        self.MakesDict = {}
        self.ModelsDict = {}

        for TrimRow in Results:
            try:
                Number = str(TrimRow[0])
                STD_Make = str(TrimRow[1])
                STD_Model = str(TrimRow[2])
                STD_Trim = str(TrimRow[3])
                Count_New = str(TrimRow[4])
                Count_All = str(TrimRow[5])
                Pct_New = str(TrimRow[6])
                sPct_Cum = str(TrimRow[7])
                MakeMod = STD_Make + "(" + STD_Model +")"
                Pct_Cum = float(sPct_Cum)
            except ValueError:
                Pct_Cum = 2
            except:
                print "Unexpected error in TrimTop:"
                print "Number = " + Number
                print "STD_Make = " + STD_Make
                print "STD_Model = " + STD_Model
                print "STD_Trim = " + STD_Trim
                print "Count_New = " + Count_New
                print "Count_All = " + Count_All
                print "Pct_New = " + Pct_New
                print "sPct_Cum = " + sPct_Cum
                print "MakeMod = " + MakeMod
                raise

            if Pct_Cum <= G_TrimTopPct:
                if STD_Make not in self.MakesDict:
                    self.MakesDict[STD_Make] = []
                if STD_Model not in self.MakesDict[STD_Make]:
                    self.MakesDict[STD_Make].append(STD_Model)
                if MakeMod not in self.ModelsDict:
                    self.ModelsDict[MakeMod] = []
                if STD_Trim not in self.ModelsDict[MakeMod]:
                    self.ModelsDict[MakeMod].append(STD_Trim)


class UserField (object):
    # UserFields are created by the ConsumerInfo class.  Multiple fields are
    #   defined for each ConsumerInfo class member.  Each represents some
    #   consumer-supplied details (for example, Income)
    # Each UserField has 5 elements:
    #   Value:      Containing the value of the field (string)
    #   isGuess:    A boolean stating if the value is a system-generated guess
    #               or a quantity supplied by the consumer
    #   GuessBasis: A string detailing how the guess was generated
    #   isFocus:    A boolean identifying if the field should have the input
    #               Focus on the browser (only one field may at any time)
    #   Label:      The text on the web site for the input field label
    Value = ""
    isGuess = True
    isFocus = False
    GuessBasis = "Default is Blank"

    def __init__(self, Label):
        self.Label = Label

    def __repr__(self):
        if self.isGuess:
            GuessText = "Guess - " + self.GuessBasis
        else:
            GuessText = "User Input"
        return "%s = %s [%s] " % (self.Label, self.Value, GuessText)


    def UpdateField(self, PostedValue, FoundFocus, AvailFocus):
        # Will update a field based on posted information from web user
        # If nothing was posted (PostedValue == "") then the field retains
        #   it's prior value and guess status.
        # Otherwise, the PostedValue is stored as the Field Value
        # There is logic to determine where the input focus should be next
        # It should be on the first un-entered (isGuess = True) field
        #   following the most recently modified (entered, cleared, or changed)
        #   field. Booleans AvailFocus and FoundFocus keep track, as fields
        #   are scanned in order, if the focus has already been assigned
        #   (AvailFocus = False) and if a changed field has been discovered
        #   (foundfocus = True) making the focus ready to be assigned to the
        #   next unfilled field.  Both Booleans are updated and returned along
        #   with the updated field
        Blank = (PostedValue == "")
        self.isFocus = FoundFocus and AvailFocus and Blank
        AvailFocus = AvailFocus and not(self.isFocus)
        FoundFocus = FoundFocus or not(Blank)
        if not(Blank):
            self.Value = PostedValue
            self.isGuess = False
        return (self, FoundFocus, AvailFocus)


class ConsumerInfo (object):
    # The ConsumerInfo class holds all information supplied by the consumer
    #   regarding their preferences and details.  When information has not
    #   been supplied by the consumer, system-generated guesses are used.
    # Each member of the class represent one unique consumer.
    # At this time, only one consumer (MyConsumer) is created, but it is
    # intended that many members of this class (representing unique consumers)
    # will exist simultenously.
    # The ConsumerInfo class supports the method MakeGuesses, which applies
    #   the system-guess logic to every isGuess field.
    # All fields are of type UserField (see above) which include a .Value
    #   element storing the actual value (entered or guessed)
    # All field values are stored as strings (Yes/No questions as "Y" or "N")
    # The following components are defined within each ConsumerInfo member:
    #   Fico        -- The FICO score of the consumer.  Right now, it is
    #                   user-entered, but intended to be generated through
    #                   a soft bureua hit.
    #   Income      -- Gross Monthly Income of the consumer.
    #   DebtService -- Monthly debt service expense (entered or from Bureau)
    #   isHomeowner -- A Y/N toggle answering if consumer is a homeowner
    #   isCosigner  -- Y/N toggle answering if there is a co-signer
    #   Cosigner    -- The FICO of the Co-signer (if any)
    #   isTradeIn   -- Y/N toggle answering if there is a Trade-In
    #   TradeInValue-- The value of the Trade-In (if any).  Right now, it is
    #                   user-entered, but intended to be generated through a
    #                   dedictaed valuation interrogative and algorithm
    #   TradeInPayoff--The amount required to pay off an auto loan (if any)
    #                   on the Trade-In (if any)
    #   UpFrontWant -- The consumer-indicated desired down payment amount
    #   UpFrontMax  -- The consumer-indicated maximum available down payment
    #   MonthlyWant -- The consumer-indicated desired monthly payment amount
    #   MonthlyMax  -- The consumer-indicated maximum available monthly payment
    #   TermWant    -- The consumer-indicated desired loan Term (in months)
    #   Zip         -- The consumer Zip code
    #   Latitude, Longitude -- Geodesic coordinates of consumer zip code
    #                           (computed from zip code; never entered)
    #                           (used to compute transport distance and costs)
    #   TaxRate     -- The applicable Sales Tax rate at the consumer's zip
    #                           (computed from zip code; never entered)
    #   TradeInTaxCredit -- =1 for states that give sales tax credit for Trade-
    #                       in, =0 elsewhere (from zip, never entered)
    Fico = UserField("FICO Score")
    Income = UserField("Monthly Gross Income")
    DebtService = UserField("Monthly Expenses")
    isHomeowner = UserField("Homeowner?")
    isCosigner = UserField("Co-Signer Available?")
    Cosigner = UserField("Co-Signer FICO")
    isTradeIn = UserField("Trade-In Available?")
    TradeInValue = UserField("Trade-In Value")
    TradeInPayoff = UserField("Trade-In Loan Payoff")
    UpfrontWant = UserField("Down Payment Wanted")
    UpfrontMax = UserField("Down Payment Maximum")
    MonthlyWant = UserField("Monthly Payment Wanted")
    MonthlyMax = UserField("Monthly Payment Maximum")
    TermWant = UserField("Loan Term (months) Wanted")

    Latitude = UserField("Latitude")
    Longitude = UserField("Longitude")
    TaxRate = UserField("Sales Tax Rate")
    TradeInTaxCredit = UserField("Sales Tax Credit for Trade-In")

    def __init__(self, OriginZip):
        # The process of creating a new member of the ConsumerInfo class
        # takes one, optional, parameter: The Zip code of the consumer.
        # It is intended that this code will be surmised from the
        # connectivity mechanism of the browser GET query.  If not available,
        # it will default to the global G_DefaultZip (90650)
        self.Zip = UserField("Zip Code")
        self.Zip.isFocus = True
        if isNull(OriginZip):
            self.Zip.Value = G_DefaultZip
            self.Zip.GuessBasis = "Global Default Zip"
        else:
            self.Zip.Value = OriginZip
            self.Zip.GuessBasis = "Origin Zip"

    def __repr__(self):
        return "%s\n"*19 % (
            self.Zip,
            self.Fico,
            self.Income,
            self.DebtService,
            self.isHomeowner,
            self.isCosigner,
            self.Cosigner,
            self.isTradeIn,
            self.TradeInValue,
            self.TradeInPayoff,
            self.UpfrontWant,
            self.UpfrontMax,
            self.MonthlyWant,
            self.MonthlyMax,
            self.TermWant,
            self.Latitude,
            self.Longitude,
            self.TaxRate,
            self.TradeInTaxCredit
        )


    def MakeGuesses(self, ZIPTable):
        # This is the main code section for affecting system guesses.
        # It is a method applied against members of the ConsumerInfo class.
        # When this method is called, all data fields that are not user-entered
        #   (isGuess = True) will be (re)evaluated in light of all other
        #   information so as to make the best guesses possible
        # In general, only fields with isGuess = True are affected;
        #   However, in some situation even entered values (isGuess = False)
        #   are overridden (for example if a Maximum is set below the ideal)
        # Also, entered values that fail data validity checking are cleared
        #   and revert to guess status
        #
        # This method requires a prepared ZIPTable (MyZIP, the only member of
        #   the byZIP class should be initialized prior to the first call to
        #   MakeGuesses, and used each time).
        #
        # The following logic is used to generate guesses:
        # ------------------------------------------------
        #   Zip: Use global default (G_DefaultZip = 90650)
        #
        #   Latitude, Longitude, TaxRate, TradeInTaxCredit: Lookup from Zip
        #       (note: latitude, Longitude, TaxRate, TradeInTaxCredit get the
        #       same isGuess status as zip)
        #
        #   Fico: If no actual Income was provided, lookup table from Zip
        #           If income is provided, apply income->fico model
        #           the model uses a linear fit from income to fico and then
        #           modifies that fit with a US-State-specific offset
        #           The final result is rounded, lower-, and upper- bounded.
        #             The following global parameters define the model
        #             G_SlopeFicoFromIncome = 0.00074811*12
        #             G_InterceptFicoFromIncome = 657.7013707
        #             G_LowestFicoFromIncome = 640
        #             G_HighstFicoFromIncome = 800
        #             G_FicoRound = 1
        #
        #   Income: If no actual Fico was provided, lookup from Zip
        #           If fico is provided, apply income->fico model in reverse
        #           The final result is rounded, lower-, and upper- bounded.
        #             G_LowestIncomeFromFico = 2500
        #             G_HighstIncomeFromFico = 7500
        #             G_IncomeRound = 100
        #
        #   DebtService: 10% of Income (actual or guessed), rounded to nearest $25
        #
        #   isHomeOwner: Guess is always "N"
        #
        #   isCosigner: If there is an actual entry for Cosigner, then
        #                   isCosigner is set to "Y" and the entry is not
        #                   considered a guess (isCosigner.isGuess = False)
        #               Otherwise, isCosigner is set to "N"
        #
        #   Cosigner: If isCosigner (actual or guessed) is "N" then set to ""
        #               Otherwise, use the Zip Fico lookup table
        #
        #   isTradeIn: If there is an actual entry for either TradeInValue or
        #               TradeInPayoff, then isTRadeIn is set to "Y" and the
        #               entry is nor considered a guess (isTradeIn.isGuess = False)
        #               Otherwise, isTradeIn is set to "N"
        #
        #   TradeInValue: If isTradeIn is "N" then set to ""
        #                   Otherwise, 2.0 * Monthly Income rounded to nearest $500
        #                   note: If a value was entered for TradeInPayoff,
        #                   then isTradeIn will automatically set to "Y",
        #                   which will trigger then income-based computation
        #
        #   TradeInPayoff: If isTradeIn is "N" then set to ""
        #                   Otherwise, $0 (will be updated)
        #
        #   UpfrontWant: If UpfrontMax is entered, use that number
        #                   else, Set to 1.0 * Month Income (actual or guess),
        #                   between $0 and $5000, rounded to nearest $100
        #
        #   UpfrontMax: If UpfrontWant is entered, use that number
        #                   else, Set to 2.0 * Month Income (actual or guess),
        #                   between $2000 and $20,000, rounded to nearest $100
        #               If both UpfrontWant and UpfrontMax are entered, and
        #                   UpfrontMax < UpfrontWant (not a logical entry),
        #                   then UpfrontMax is overwritten with UpfrontWant
        #
        #   MonthlyWant: If MonthlyMax is entered, use that number
        #                   else, Set to 8% * Month Income (actual or guess),
        #                   between $100 and $2500, rounded to nearest $10
        #
        #   MonthlyMax: If MonthlyWant is entered, use that number
        #                   else, Set to 18% * Month Income (actual or guess),
        #                   between $200 and $5000, rounded to nearest $10
        #               If both MonthlyWant and MonthlyMax are entered, and
        #                   MonthlyMax < MonthlyWant (not a logical entry),
        #                   then MonthlyMax is overwritten with MonthlyWant
        #
        #   TermWant:   Guess is always 72

        ###### DATA VALIDATION FOR ALL USER ENTERED FIELDS #####
        self.Zip.isGuess = self.Zip.isGuess or \
                            (self.Zip.Value not in ZIPTable.Income)

        self.Fico.Value = strRound(self.Fico.Value,
                                      1,
                                      G_LowestFicoAnywhere,
                                      G_HighestFicoAnywhere)
        self.Fico.isGuess = self.Fico.isGuess or isNull(self.Fico.Value)

        self.Income.Value = strRound(self.Income.Value,
                                      1,
                                      G_LowestIncomeAnywhere,
                                      G_HighestIncomeAnywhere)
        self.Income.isGuess = self.Income.isGuess or isNull(self.Income.Value)

        self.DebtService.Value = strRound(self.DebtService.Value,
                                          1,
                                          G_LowestIncomeAnywhere,
                                          G_HighestIncomeAnywhere)
        self.DebtService.isGuess = self.DebtService.isGuess or isNull(self.DebtService.Value)


        self.Cosigner.Value = strRound(self.Cosigner.Value,
                                          1,
                                          G_LowestFicoAnywhere,
                                          G_HighestFicoAnywhere)
        self.Cosigner.isGuess = self.Cosigner.isGuess or isNull(self.Cosigner.Value)

        self.TradeInValue.Value = strRound(self.TradeInValue.Value,
                                              1,
                                              G_LowestTradeInAnywhere,
                                              G_HighestTradeInAnywhere)
        self.TradeInValue.isGuess = self.TradeInValue.isGuess or isNull(self.TradeInValue.Value)

        self.TradeInPayoff.Value = strRound(self.TradeInPayoff.Value,
                                              1,
                                              G_LowestTradeInAnywhere,
                                              G_HighestTradeInAnywhere)
        self.TradeInPayoff.isGuess = self.TradeInPayoff.isGuess or isNull(self.TradeInPayoff.Value)

        self.UpfrontWant.Value = strRound(self.UpfrontWant.Value,
                                              1,
                                              G_LowestUpfrontAnywhere,
                                              G_HighestUpfrontAnywhere)
        self.UpfrontWant.isGuess = self.UpfrontWant.isGuess or isNull(self.UpfrontWant.Value)

        self.UpfrontMax.Value = strRound(self.UpfrontMax.Value,
                                              1,
                                              G_LowestUpfrontAnywhere,
                                              G_HighestUpfrontAnywhere)
        self.UpfrontMax.isGuess = self.UpfrontMax.isGuess or isNull(self.UpfrontMax.Value)

        self.MonthlyWant.Value = strRound(self.MonthlyWant.Value,
                                              1,
                                              G_LowestMonthlyAnywhere,
                                              G_HighestMonthlyAnywhere)
        self.MonthlyWant.isGuess = self.MonthlyWant.isGuess or isNull(self.MonthlyWant.Value)

        self.MonthlyMax.Value = strRound(self.MonthlyMax.Value,
                                              1,
                                              G_LowestMonthlyAnywhere,
                                              G_HighestMonthlyAnywhere)
        self.MonthlyMax.isGuess = self.MonthlyMax.isGuess or isNull(self.MonthlyMax.Value)

        self.TermWant.Value = strRound(self.TermWant.Value,
                                              G_TermRound,
                                              G_LowestTermAnywhere,
                                              G_HighestTermAnywhere)
        self.TermWant.isGuess = self.TermWant.isGuess or isNull(self.TermWant.Value)

        ###### SYSTEM GUESS ALGORITHMS BEGIN HERE #####
        if self.Zip.isGuess:
            self.Zip.Value = G_DefaultZip
            self.Zip.GuessBasis = "Default Zip Code"

        self.Latitude.Value = ZIPTable.Latitude[self.Zip.Value]
        self.Latitude.isGuess = self.Zip.isGuess
        self.Latitude.GuessBasis = "Table lookup from Zip"

        self.Longitude.Value = ZIPTable.Longitude[self.Zip.Value]
        self.Longitude.isGuess = self.Zip.isGuess
        self.Longitude.GuessBasis = "Table lookup from Zip"

        self.TaxRate.Value = ZIPTable.TaxRate[self.Zip.Value]
        self.TaxRate.isGuess = self.Zip.isGuess
        self.TaxRate.GuessBasis = "Table lookup from Zip"

        self.TradeInTaxCredit.Value = ZIPTable.TradeInTaxCredit[self.Zip.Value]
        self.TradeInTaxCredit.isGuess = self.Zip.isGuess
        self.TradeInTaxCredit.GuessBasis = "Table lookup from Zip"


        if self.Fico.isGuess:
            if self.Income.isGuess:
                self.Fico.Value = strRound(
                                  ZIPTable.FICO3[self.Zip.Value],
                                  G_FicoRound,
                                  G_LowestFicoAnywhere,
                                  G_HighestFicoAnywhere)
                self.Fico.GuessBasis = "from Zip-based model"
            else:
                self.Fico.Value = strRound(
                                  max(G_LowestFicoFromIncome,
                                  min(G_HighstFicoFromIncome,
                                      G_SlopeFicoFromIncome *
                                      float(self.Income.Value) +
                                      G_InterceptFicoFromIncome +
                                      ZIPTable.ST2offset[self.Zip.Value])),
                                      G_FicoRound,
                                      G_LowestFicoAnywhere,
                                      G_HighestFicoAnywhere)
                self.Fico.GuessBasis = "from ACTUAL Income, offset by State"

        if self.Income.isGuess:
            if self.Fico.isGuess:
                self.Income.Value = strRound(ZIPTable.Income[self.Zip.Value],
                                             G_IncomeRound,
                                             G_LowestIncomeAnywhere,
                                             G_HighestIncomeAnywhere)
                self.Income.GuessBasis = "from Zip Median table"
            else:
                self.Income.Value = strRound(
                                    max(G_LowestIncomeFromFico,
                                    min(G_HighstIncomeFromFico,
                                        (float(self.Fico.Value) -
                                         ZIPTable.ST2offset[self.Zip.Value] -
                                         G_InterceptFicoFromIncome) /
                                        G_SlopeFicoFromIncome)),
                                    G_IncomeRound,
                                    G_LowestIncomeAnywhere,
                                    G_HighestIncomeAnywhere)
                self.Income.GuessBasis = "from ACTUAL FICO, offset by State"

        if self.DebtService.isGuess:
            self.DebtService.Value = strRound(
                                      float(self.Income.Value) *
                                      G_DebtPercentofIncome,
                                      G_DebtRound,
                                      G_LowestIncomeAnywhere,
                                      G_HighestIncomeAnywhere)
            self.DebtService.GuessBasis = "percent of Income"

        if self.isHomeowner.isGuess:
            self.isHomeowner.Value = "N"
            self.isHomeowner.GuessBasis = "Default is No"

        if self.Cosigner.isGuess:
            if self.isCosigner.isGuess:
                self.isCosigner.Value = "N"
                self.isCosigner.GuessBasis = "Default is No"
            if self.isCosigner.Value == "N":
                self.Cosigner.Value = ""
                self.Cosigner.GuessBasis = "There is no CoSigner"
            else:
                self.Cosigner.Value = strRound(
                                      ZIPTable.FICO3[self.Zip.Value],
                                      G_FicoRound,
                                      G_LowestFicoAnywhere,
                                      G_HighestFicoAnywhere)
                self.Cosigner.GuessBasis = "from Zip-based model"
        else:
                self.isCosigner.isGuess = False
                self.isCosigner.Value = "Y"
                self.isCosigner.GuessBasis = "An ACTUAL CoSigner Fico exists"

        if self.TradeInValue.isGuess and self.TradeInPayoff.isGuess:
            if self.isTradeIn.isGuess:
                self.isTradeIn.Value = "N"
                self.isTradeIn.GuessBasis = "Default is No"
        else:
            self.isTradeIn.isGuess = False
            self.isTradeIn.Value = "Y"
            self.isTradeIn.GuessBasis = "An ACTUAL Trade-In Value or Payoff exists"

        if self.TradeInValue.isGuess:
            if self.isTradeIn.Value == "N":
                self.TradeInValue.Value = ""
                self.TradeInValue.GuessBasis = "There is no Trade-In"
            else:
                self.TradeInValue.Value = strRound(
                                    float(self.Income.Value) *
                                    G_TradeInIncomeMonths,
                                    G_TradeInRound,
                                    G_LowestTradeInAnywhere,
                                    G_HighestTradeInAnywhere)
                self.TradeInValue.GuessBasis = "Months of Income"

        if self.TradeInPayoff.isGuess:
            if self.isTradeIn.Value == "N":
                self.TradeInPayoff.Value = ""
                self.TradeInPayoff.GuessBasis = "There is no Trade-In"
            else:
                self.TradeInPayoff.Value = "0"
                self.TradeInPayoff.GuessBasis = "Set to $0, will be updated"

        if self.UpfrontWant.isGuess:
            if self.UpfrontMax.isGuess:
                self.UpfrontWant.Value = strRound(
                                          max(G_LowestUpfrontWanted,
                                          min(G_HighestUpfrontWanted,
                                          float(self.Income.Value) *
                                          G_UpfrontWantedIncomeMonths)),
                                          G_UpfrontRound,
                                          G_LowestUpfrontAnywhere,
                                          G_HighestUpfrontAnywhere)
                self.UpfrontWant.GuessBasis = "Months of Income"
            else:
                self.UpfrontWant.Value = self.UpfrontMax.Value
                self.UpfrontWant.GuessBasis = "ACTUAL Upfront Maximum"

        if self.UpfrontMax.isGuess:
            if self.UpfrontWant.isGuess:
                self.UpfrontMax.Value = strRound(
                                          max(G_LowestUpfrontMax,
                                          min(G_HighestUpfrontMax,
                                          float(self.Income.Value) *
                                          G_UpfrontMaxIncomeMonths)),
                                          G_UpfrontRound,
                                          G_LowestUpfrontAnywhere,
                                          G_HighestUpfrontAnywhere)
                self.UpfrontMax.GuessBasis = "Months of Income"
            else:
                self.UpfrontMax.Value = self.UpfrontWant.Value
                self.UpfrontMax.GuessBasis = "ACTUAL Upfront Wanted"
        elif float(self.UpfrontMax.Value) < float(self.UpfrontWant.Value):
            self.UpfrontMax.Value = self.UpfrontWant.Value
            self.UpfrontMax.isGuess = True
            self.UpfrontMax.GuessBasis = "OVER-WRITE Max to Equal Wanted"

        if self.MonthlyWant.isGuess:
            if self.MonthlyMax.isGuess:
                self.MonthlyWant.Value = strRound(
                                          max(G_LowestMonthlyWanted,
                                          min(G_HighestMonthlyWanted,
                                          (float(self.Income.Value) -
                                          float(self.DebtService.Value))*
                                          G_MonthlyWantedPercentofIncome)),
                                          G_MonthlyRound,
                                          G_LowestMonthlyAnywhere,
                                          G_HighestMonthlyAnywhere)
                self.MonthlyWant.GuessBasis = "Percent of Income"
            else:
                self.MonthlyWant.Value = self.MonthlyMax.Value
                self.MonthlyWant.GuessBasis = "ACTUAL Monthly Maximum"

        if self.MonthlyMax.isGuess:
            if self.MonthlyWant.isGuess:
                self.MonthlyMax.Value = strRound(
                                          max(G_LowestMonthlyMax,
                                          min(G_HighestMonthlyMax,
                                          (float(self.Income.Value) -
                                          float(self.DebtService.Value))*
                                          G_MonthlyMaxPercentofIncome)),
                                          G_MonthlyRound,
                                          G_LowestMonthlyAnywhere,
                                          G_HighestMonthlyAnywhere)
                self.MonthlyMax.GuessBasis = "Percent of Income"
            else:
                self.MonthlyMax.Value = self.MonthlyWant.Value
                self.MonthlyMax.GuessBasis = "ACTUAL Monthly Wanted"

        elif float(self.MonthlyMax.Value) < float(self.MonthlyWant.Value):
            self.MonthlyMax.Value = self.MonthlyWant.Value
            self.MonthlyMax.isGuess = True
            self.MonthlyMax.GuessBasis = "OVER-WRITE Max to Equal Wanted"

        if self.TermWant.isGuess:
            self.TermWant.Value = G_TermWanted
            self.TermWant.GuessBasis = "Always defaults to 72"


class SearchFilter(object):
    # Create a class that holds one serach filter
    isGuess = True
    isFocus = False
    isOther = False
    GuessBasis = "Default is Check-All"

    def __init__(self, TableLabel):
        self.Choices = {}
        self.TableLabel = TableLabel

    def __repr__(self):
        if self.isGuess:
            GuessText = "Guess - " + self.GuessBasis
        else:
            GuessText = "User Selection"
        return "%s = %s Other:%s [%s] " % \
            (self.TableLabel, self.Choices, self.isOther, GuessText)


class FilterArray(object):
    # Creates a class that holds the entire array of search filters
    Filter = {"1Year": SearchFilter("Year"),
              "2Make": SearchFilter("Make"),
              "3Model": SearchFilter("Model"),
              "4Trim": SearchFilter("Trim"),
              "5Color": SearchFilter("Ext_Color_Generic"),
              "6Options": SearchFilter("Options"),
              "7Filter1": SearchFilter("F1"),
              "8Filter2": SearchFilter("F2")
              }

    Filter["1Year"].Choices.update({"2012": True, "2013": True, "2014": True})
    Filter["5Color"].Choices.update({"Black": True,
                                    "White": True,
                                    "Silver": True,
                                    "Gray": True,
                                    "Red": True,
                                    "Blue": True,
                                    "Brown": True
                                    })

    def __init__(self, MMList,
                 DMake=G_DefaultMake,
                 DModel=G_DefaultModel,
                 DTrim=G_DefaultTrim):
        for AvailableMake in MMList.MakesDict.keys():
            self.Filter["2Make"].Choices.update({AvailableMake: False})
        self.Filter["2Make"].Choices[DMake] = True
        self.Filter["2Make"].isGuess = True
        self.Filter["2Make"].GuessBasis = "Default is one popular Make checked"
        self.Filter["3Model"].Choices[DModel] = True
        self.Filter["3Model"] = self.FixModel(MMList)
        self.Filter["3Model"].isGuess = True
        self.Filter["3Model"].GuessBasis = "Default is one popular Model checked"
        self.Filter["4Trim"].Choices[DTrim] = True
        self.Filter["4Trim"] = self.FixTrim(MMList)
        self.Filter["4Trim"].isGuess = True
        self.Filter["4Trim"].GuessBasis = "Default is one popular Trim checked"

    def __repr__(self):
        Outstring = ""
        for FilterName in self.Filter:
            Outstring = Outstring + str(self.Filter[FilterName]) + "\n"
        return Outstring

    def FixModel(self, MMList):
        # Update the Models Filter Choices in light of the selected Makes
        # 1. Create a new Model Filter
        # 2. Loop through all selected Makes
        #       2A. For each Make, loop through all available models
        #           2Aa. Create entry in new Model filter for model
        #           2Ab. If Model exist in original Model filer, copy checkbox
        #           2Ab. If not, set checkbox to FALSE
        NewModelFilter = SearchFilter("Model")
        for CheckedMake in self.Filter["2Make"].Choices:
            if self.Filter["2Make"].Choices[CheckedMake]:
                for AvailableModel in MMList.MakesDict[CheckedMake]:
                    NewModelFilter.Choices.update({AvailableModel:
                        self.Filter["3Model"].Choices.get(AvailableModel, False) })
        NewModelFilter.isOther = self.Filter["3Model"].isOther
        return NewModelFilter

    def FixTrim(self, MMList):
        # Update the Trims Filter Choices in light of the selected Models
        # 1. Create a new Trim Filter
        # 2. Loop through all selected Makes
        #       2A. For each checked Make, loop through all selected Models
        #           2Aa. Construct MMKey = 'MAKE(MODEL)'
        #           2Ab. Loop through all Trims for MMKey
        #               2Abi. Create entry in new Trim filter for trim
        #               2Abii. If trim exist in original trim filer, copy checkbox
        #               2Abiii. If not, set checkbox to FALSE
        NewTrimFilter = SearchFilter("Trim")
        for CheckedMake in self.Filter["2Make"].Choices:
            if self.Filter["2Make"].Choices[CheckedMake]:
                for AvailableModel in MMList.MakesDict[CheckedMake]:
                    if self.Filter["3Model"].Choices.get(AvailableModel, False):
                        MMKey = CheckedMake + '(' + AvailableModel + ')'
                        for AvailableTrim in MMList.ModelsDict[MMKey]:
                            NewTrimFilter.Choices.update({AvailableTrim:
                                self.Filter["4Trim"].Choices.get(AvailableTrim, False)})
        NewTrimFilter.isOther = self.Filter["4Trim"].isOther
        return NewTrimFilter


class OneVehicle(object):
    # A member of this class is a vehicle available for sale
    # FieldNames is an ordered list of Fields describing the Vehicle
    # Properties is a dictionary from each FieldName to it's value
    def __init__(self, FieldNames, FieldValues):
        self.Properties = {}
        for i in range(len(FieldNames)):
            self.Properties.update({FieldNames[i]: FieldValues[i]})
        self.FieldNames = FieldNames

    def __repr__(self):
        Outstring = "[* "
        for Property in self.FieldNames:
            Outstring = Outstring + Property + ": " + \
                        str(self.Properties[Property]) + " "
        return Outstring + "*]"


class VehicleArray(object):
    # This is an array of all Vehciles that passed the filter

    def __init__(self, FilterArray, MyConsumer, MyAPR):
        HardArray, SoftArray = \
            FetchFilteredInventory(FilterArray, MyConsumer, MyAPR)
        FieldNames = GetFieldsNames("Inventory_Hard")
        self.HardVehicles = []
        for FetchedVehicle in HardArray:
            self.HardVehicles.append(OneVehicle(FieldNames, FetchedVehicle))
        self.SoftVehicles = []
        for FetchedVehicle in SoftArray:
            self.SoftVehicles.append(OneVehicle(FieldNames, FetchedVehicle))

    def __repr__(self):
        Outstring = "Hard Filtered Vehicles:\n"
        for HardVehicle in self.HardVehicles:
            Outstring = Outstring + str(HardVehicle) + "\n"
        Outstring = Outstring + "Soft Filtered Vehicles:\n"
        for SoftVehicle in self.SoftVehicles:
            Outstring = Outstring + str(SoftVehicle) + "\n"
        return Outstring


class Index(object):
    def GET(self):
        return render.CarZumerBrowse(MyConsumer, MyFilterArray, MySelections)

    def POST(self):
        form = web.input(Zip="",
                         UpfrontWant="",
                         UpfrontMax="",
                         MonthlyWant="",
                         MonthlyMax="",
                         TermWant="",
                         Fico="",
                         Income="",
                         DebtService="",
                         isHomeowner="",
                         isCosigner="",
                         Cosigner="",
                         isTradeIn="",
                         TradeInValue="",
                         TradeInPayoff="",
                         AllCheckList=[],
                         ClearCheckList=[],
                         OtherCheckList=[],
                         DetailedCheckList=[])

        FoundFocus = False
        AvailFocus = True

        MyConsumer.Zip, FoundFocus, AvailFocus =  \
            MyConsumer.Zip.UpdateField(form.Zip, FoundFocus, AvailFocus)
        MyConsumer.UpfrontWant, FoundFocus, AvailFocus =  \
            MyConsumer.UpfrontWant.UpdateField(form.UpfrontWant, FoundFocus, AvailFocus)
        MyConsumer.UpfrontMax, FoundFocus, AvailFocus =  \
            MyConsumer.UpfrontMax.UpdateField(form.UpfrontMax, FoundFocus, AvailFocus)
        MyConsumer.MonthlyWant, FoundFocus, AvailFocus =  \
            MyConsumer.MonthlyWant.UpdateField(form.MonthlyWant, FoundFocus, AvailFocus)
        MyConsumer.MonthlyMax, FoundFocus, AvailFocus =  \
            MyConsumer.MonthlyMax.UpdateField(form.MonthlyMax, FoundFocus, AvailFocus)
        MyConsumer.TermWant, FoundFocus, AvailFocus =  \
            MyConsumer.TermWant.UpdateField(form.TermWant, FoundFocus, AvailFocus)

        MyConsumer.Fico, FoundFocus, AvailFocus =  \
            MyConsumer.Fico.UpdateField(form.Fico, FoundFocus, AvailFocus)
        MyConsumer.Income, FoundFocus, AvailFocus =  \
            MyConsumer.Income.UpdateField(form.Income, FoundFocus, AvailFocus)
        MyConsumer.DebtService, FoundFocus, AvailFocus =  \
            MyConsumer.DebtService.UpdateField(form.DebtService, FoundFocus, AvailFocus)
        MyConsumer.Cosigner, FoundFocus, AvailFocus =  \
            MyConsumer.Cosigner.UpdateField(form.Cosigner, FoundFocus, AvailFocus)

        MyConsumer.TradeInValue, FoundFocus, AvailFocus =  \
            MyConsumer.TradeInValue.UpdateField(form.TradeInValue, FoundFocus, AvailFocus)
        MyConsumer.TradeInPayoff, FoundFocus, AvailFocus =  \
            MyConsumer.TradeInPayoff.UpdateField(form.TradeInPayoff, FoundFocus, AvailFocus)

        MyConsumer.isHomeowner, FoundFocus, AvailFocus =  \
            MyConsumer.isHomeowner.UpdateField(form.isHomeowner, FoundFocus, AvailFocus)
        MyConsumer.isCosigner, FoundFocus, AvailFocus =  \
            MyConsumer.isCosigner.UpdateField(form.isCosigner, FoundFocus, AvailFocus)
        MyConsumer.isTradeIn, FoundFocus, AvailFocus =  \
            MyConsumer.isTradeIn.UpdateField(form.isTradeIn, FoundFocus, AvailFocus)

        MyConsumer.Zip.isFocus = AvailFocus

        MyConsumer.MakeGuesses(MyZip)

        # Code to unpack the AllCheckList
        for AvailableFilter in MyFilterArray.Filter:
            isCheckAll = AvailableFilter in form.AllCheckList
            isCheckClear = AvailableFilter in form.ClearCheckList
            MyFilterArray.Filter[AvailableFilter].isFocus = \
                isCheckAll or isCheckClear
            MyFilterArray.Filter[AvailableFilter].isOther = \
                isCheckAll or (not(isCheckClear) and \
                AvailableFilter in form.OtherCheckList)
            # Code to unpack the DetailedCheckList
            for AvailableChoice in MyFilterArray.Filter[AvailableFilter].Choices:
                MyFilterArray.Filter[AvailableFilter].Choices[AvailableChoice] = \
                isCheckAll or (not(isCheckClear) and \
                (AvailableFilter + " " + AvailableChoice) in form.DetailedCheckList)

        MyFilterArray.Filter["3Model"] = MyFilterArray.FixModel(MMList)
        MyFilterArray.Filter["4Trim"] = MyFilterArray.FixTrim(MMList)

        # Code to serach the database for matching entries
        MySelections = VehicleArray(MyFilterArray, MyConsumer, MyAPR)

        return render.CarZumerBrowse(MyConsumer, MyFilterArray, MySelections)


def GetFieldsNames(TableName):
        MyDB = sqlite3.connect(FnameDB)
        cur = MyDB.cursor()
        cur.execute("SELECT * FROM " + TableName + " LIMIT 1;")
        Results = [description[0] for description in cur.description]
        MyDB.commit()
        MyDB.close()
        return Results

def FetchFilteredInventory(FilterArray, MyConsumer, MyAPR):
        # Code to serach the inventory database for matching entries
        MyDB = sqlite3.connect(FnameDB)
        cur = MyDB.cursor()
        MyDB.create_function("SQL_BestSellingPrice", 2, SQL_BestSellingPrice)
        MyDB.create_function("SQL_BestInvoicePrice", 3, SQL_BestInvoicePrice)
        MyDB.create_function("SQL_Distance", 4, SQL_Distance)
        MyDB.create_function("SQL_SalesTax", 4, SQL_SalesTax)
        MyDB.create_function("SQL_Transport", 1, SQL_Transport)
        MyDB.create_function("SQL_CashCost", 3, SQL_CashCost)
        MyDB.create_function("SQL_FindAPR", 7, SQL_FindAPR)
        MyDB.create_function("SQL_FindMonthly", 7, SQL_FindMonthly)
        MyDB.create_function("SQL_FindDown", 7, SQL_FindDown)

        MyScript1 = """
           DROP TABLE IF EXISTS Inventory_Filtered1;
           CREATE TABLE Inventory_Filtered1 AS
           SELECT I.*,
           CashCost AS Down0,
           0 AS Monthly0,
           DownWant AS Down1,
           SQL_FindMonthly(SellingPrice, Invoice, CashCost,
                                           TradeIn, Payoff,
                                           DownWant, Fico) AS Monthly1,
           DownMax AS Down2,
           SQL_FindMonthly(SellingPrice, Invoice, CashCost,
                                           TradeIn, Payoff,
                                           DownMax, Fico) AS Monthly2,
           SQL_FindDown(SellingPrice, Invoice, CashCost,
                                      TradeIn, Payoff,
                                      MonthlyWant, Fico) AS Down3,
           MonthlyWant AS Monthly3,
           SQL_FindDown(SellingPrice, Invoice, CashCost,
                                          TradeIn, Payoff,
                                          MonthlyMax, Fico) AS Down4,
           MonthlyMax AS Monthly4,
           '0' as Down5,
           SQL_FindMonthly(SellingPrice, Invoice, CashCost,
                                           TradeIn, Payoff,
                                           '0', Fico) AS Monthly5
           FROM
           (SELECT *,
           SQL_Transport(DistanceMiles) AS TransportCost,
           SQL_CashCost(BestSellingPrice, DistanceMiles, SalesTax) AS CashCost

           FROM
           (SELECT *,
           SQL_Distance(DealerLatitude, DealerLongitude,
                ConsumerLatitude, ConsumerLongitude) AS DistanceMiles,

           SQL_SalesTax(BestSellingPrice, TaxRate,
                TradeInValue, TradeInTaxCredit) AS SalesTax

           FROM
           (SELECT VIN, YEAR, MAKE, Model, Trim,
           Year_STD, Make_STD, Model_STD, Trim_STD,
           Ext_Color_Generic AS Color,
           SellingPrice, Invoice,
           CAST(ABS(RANDOM() % 10000) AS TEXT) AS RandomNumber,
           DealerZip,
           Latitude,
           Longitude,
           Latitude AS DealerLatitude,
           Longitude AS DealerLongitude,
           SQL_BestSellingPrice(SellingPrice, Invoice) AS BestSellingPrice,
           """ + \
           MyConsumer.Latitude.Value + " AS ConsumerLatitude, \n" + \
           MyConsumer.Longitude.Value + " AS ConsumerLongitude, \n" + \
           MyConsumer.TaxRate.Value + " AS TaxRate, \n\'" + \
           MyConsumer.TradeInValue.Value + "\' AS TradeInValue, \n" + \
           MyConsumer.TradeInTaxCredit.Value + " AS TradeInTaxCredit, \n\'" + \
           MyConsumer.Fico.Value + "\' AS Fico, \n\'" + \
           MyConsumer.UpfrontWant.Value + "\' AS DownWant, \n\'" + \
           MyConsumer.UpfrontMax.Value + "\' AS DownMax, \n\'" + \
           MyConsumer.MonthlyWant.Value + "\' AS MonthlyWant, \n\'" + \
           MyConsumer.MonthlyMax.Value + "\' AS MonthlyMax, \n\'" + \
           MyConsumer.TermWant.Value + "\' AS TermWant, \n\'" + \
           MyConsumer.TradeInValue.Value + "\' AS TradeIn, \n\'" + \
           MyConsumer.TradeInPayoff.Value + """\' AS Payoff

           FROM Inventory_STD))) AS I\n """

        HardFilter =   MakeFilterSQLTable(cur, FilterArray,
                           "Year_Filter", "Year_In", "Year_STD", "1Year") + \
                       MakeFilterSQLTable(cur, FilterArray,
                           "Make_Filter", "Make_In", "Make_STD", "2Make") + \
                       MakeFilterSQLTable(cur, FilterArray,
                           "Model_Filter", "Model_In", "Model_STD", "3Model") + \
                       MakeFilterSQLTable(cur, FilterArray,
                           "Trim_Filter", "Trim_In", "Trim_STD", "4Trim") + \
                       MakeFilterSQLTable(cur, FilterArray,
                           "Color_Filter", "Color_In", "Color", "5Color")

        SoftFilter = " WHERE Down4 <= DownMax \n "

        HardOrder =   " \n ORDER BY CashCost ASC LIMIT 25; \n"

        SoftOrder =   " \n ORDER BY RandomNumber LIMIT 25; \n "

        HardDestination = """ DROP TABLE IF EXISTS Inventory_Hard;
                           CREATE TABLE Inventory_Hard AS """

        SoftDestination = """ DROP TABLE IF EXISTS Inventory_Soft;
                           CREATE TABLE Inventory_Soft AS """

        MyScript2 = """ SELECT *,
                           '' as APR0,
                           SQL_FindAPR(SellingPrice, Invoice, CashCost,
                                       TradeIn, Payoff, Down1, Fico) AS APR1,
                           SQL_FindAPR(SellingPrice, Invoice, CashCost,
                                       TradeIn, Payoff, Down2, Fico) AS APR2,
                           SQL_FindAPR(SellingPrice, Invoice, CashCost,
                                       TradeIn, Payoff, Down3, Fico) AS APR3,
                           SQL_FindAPR(SellingPrice, Invoice, CashCost,
                                       TradeIn, Payoff, Down4, Fico) AS APR4,
                           SQL_FindAPR(SellingPrice, Invoice, CashCost,
                                       TradeIn, Payoff, Down5, Fico) AS APR5

                       FROM Inventory_Filtered1 """

        HardFilterScript = MyScript1 + HardFilter + HardOrder + \
                             HardDestination + MyScript2 + HardOrder

        SoftFilterScript = MyScript1 + SoftFilter + SoftOrder + \
                            SoftDestination + MyScript2 + SoftOrder

        print "HardFilterScript = "
        print HardFilterScript

        # print "SoftFilterScript = "
        # print SoftFilterScript

        cur.executescript(HardFilterScript)
        cur.execute("SELECT * FROM Inventory_Hard LIMIT " +
                    str(G_SelectionsShown))
        HardResults = cur.fetchall()


        cur.executescript(SoftFilterScript)
        cur.execute("SELECT * FROM Inventory_Soft LIMIT " +
                    str(G_SelectionsShown))
        SoftResults = cur.fetchall()

        MyDB.commit()
        MyDB.close()
        return HardResults, SoftResults


def MakeFilterSQLTable(cur, FilterArray, \
                       TableName, FieldName, InventoryField, FilterName):
    # With an already opened SQL database (pointed to by cur),
    # Create a table with one field, listing all checked filter options
    cur.execute("DROP TABLE IF EXISTS " + TableName)
    cur.execute("CREATE TABLE " + TableName + "(" + FieldName + " TEXT);")
    AnyChecked = False
    for AvailableChoice in FilterArray.Filter[FilterName].Choices:
        AnyChecked = AnyChecked or \
                     FilterArray.Filter[FilterName].Choices[AvailableChoice]
    if AnyChecked:
        for AvailableChoice in FilterArray.Filter[FilterName].Choices:
            if FilterArray.Filter[FilterName].Choices[AvailableChoice]:
                cur.execute("INSERT INTO " + TableName + "(" + FieldName +
                            ") VALUES (\'" + AvailableChoice + "\');")
        Results = "INNER JOIN " + TableName + " ON I." + InventoryField +\
                  " = " + TableName + "." + FieldName + "\n"
    else:
        Results = ""
    return Results


def SQL_Distance(slat1, slon1, slat2, slon2):
    # Find the Geo-distance between two pairs of latitude and longitude coords
    # Logic: Great Circle formula on a spherical Earth
    if isNull(slat1) or isNull(slon1) or isNull(slat2) or isNull(slon2):
           return ""
    try:
        lat1 = float(slat1)
        lon1 = float(slon1)
        lat2 = float(slat2)
        lon2 = float(slon2)
        R = 3956 # Earth Radius in miles
        dLat = math.radians(lat2 - lat1) # Convert Degrees 2 Radians
        dLon = math.radians(lon2 - lon1)
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)
        a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        Results = R * c
        return str(int(round(Results)))
    except ValueError:
        return ""
    except:
        print "Unexpected error in SQL_Distance:"
        print "slat1 = " + str(slat1)
        print "slon1 = " + str(slon1)
        print "slat2 = " + str(slat2)
        print "slon2 = " + str(slon2)
        raise


def SQL_BestSellingPrice(sSellingPrice, sInvoice):
    # Data Cleaning process to ascertain the vehcile selling price
    # Logic: If SellingPrice is clean and >0, use it
    #       Else, if Invoice is clean, use it,
    #       Else, use "0" (for lack of a better alternative)
    try:
        Results = float(fixZero(sSellingPrice, fixZero(sInvoice, 0)))
        return str(int(round(Results)))
    except ValueError:
        return ""
    except:
        print "Unexpected error in SQL_SalesTax:"
        print "sSellingPrice = " + str(sSellingPrice)
        print "sInvoice = " + str(sInvoice)
        raise


def SQL_BestInvoicePrice(sSellingPrice, sInvoice, iCashCost):
    # Data Cleaning process to ascertain the vehcile Invoice price
    # Logic: If Inmvoice is clean and >0, use it
    #       Else, if SellingPrice is clean, use it,
    #       Else, use CashCost (for lack of a better alternative)
    try:
        Results = float(fixZero(sInvoice, fixZero(sSellingPrice, iCashCost)))
        return str(int(round(Results)))
    except ValueError:
        return ""
    except:
        print "Unexpected error in SQL_SalesTax:"
        print "sSellingPrice = " + str(sSellingPrice)
        print "sInvoice = " + str(sInvoice)
        print "iCashCost = " + str(iCashCost)
        raise


def SQL_SalesTax(sBestSellingPrice, sTaxRate, sTradeIn, sTradeInCredit):
    # Find the actual ($ amount) of sales tax on a prospective transaction
    # In some states, the sales tax applies the the entire selling price,
    #   whereas in others, it only applies to the difference between the
    #   purchase price of the new vehicle and Trade-in value
    #   The parameter sTradeInCredit is 0 for the former and 1 for the latter
    # Logic: SalesTax = TaxRate * (SellingPrice - TradeIn * TradeInCredit)
    #           (SalesTax is never negative)
    try:
        Results = max( 0, float0(sTaxRate) * \
                  (float0(sBestSellingPrice) - \
                   float0(sTradeIn) * float0(sTradeInCredit) ) )
        return str(int(round(Results)))
    except ValueError:
        return "0"
    except:
        print "Unexpected error in SQL_SalesTax:"
        print "sBestSellingPrice = " + str(sBestSellingPrice)
        print "sTaxRate = " + str(sTaxRate)
        print "sTradeIn = " + str(sTradeIn)
        print "sTradeInCredit = " + str(sTradeInCredit)
        raise


def SQL_Transport(sDistance):
    # Find the cost of transporting a vehicle between two pairs of coords
    # Logic: Apply Transport Cost Model to find $ cost as function of distance
    #        Transport Cost Model uses two seperate straight-line fits:
    #        A short distance fit (under 600 miles) and a long distance one
    #        Global variables supply the intercept and slope for each fit
    try:
        Distance = float0(sDistance)
        if Distance < G_ShippingBreakPoint:
            Results = G_ShippingLowIntercept + G_ShippingLowSlope * Distance
        else:
            Results = G_ShippingHighIntercept + G_ShippingHighSlope * Distance
        return str(int(round(Results)))
    except ValueError:
        return ""
    except:
        print "Unexpected error in SQL_Transport:"
        print "sDistance = " + str(sDistance)
        raise


def SQL_CashCost(sBestSellingPrice, sDistance, sTax):
    # Find the Cash Cost of a vehicle
    # Logic: CashCost = SellingPrice + Transport + SalesTax
    #       Transport is computed using SQL_Transport() from coords
    #       SalesTax is computed using SQL_SalesTax() from price, tradeIn, Rate
    try:
        TransportCost = float0(fixZero(SQL_Transport(sDistance), G_ShippingMissing))
        SalesTax = float0(sTax)
        SellingPrice = float0(sBestSellingPrice)
        Results = SellingPrice + TransportCost + SalesTax
        return int(round(Results))
    except ValueError:
        return 0
    except:
        print "Unexpected error in SQL_CashCost:"
        print "sBestSellingPrice = " + str(sBestSellingPrice)
        print "sDistance = " + str(sDistance)
        print "sTax = " + str(sTax)
        raise


def SQL_FindAPR(sSellingPrice, sInvoice, iCashCost, sTradeIn, sPayoff, sDownCash, sFico):
    # Find the APR for a given DownCash figure
    # Logic: LoanAmount = Price - [ DownCash + TradeIn - TradeInPayoff ]
    #        LTV = LoanAmount / Invoice
    #        Use LTV and FICO to find APR in the APR table
    try:
        Invoice = float(fixZero(sInvoice, fixZero(sSellingPrice, iCashCost)))
        if Invoice == 0:
            return "0"
        TradeInNet = float(fixNull(sTradeIn, 0)) - float(fixNull(sPayoff, 0))
        DownPayment = float(fixNull(sDownCash, 0)) + TradeInNet
        LoanAmount = iCashCost - DownPayment
        LTV = LoanAmount / Invoice
        sFico = fixNull(sFico, str(G_LowestFicoAnywhere))
        Results = MyAPR.GetAPR(sFico, LTV, MyConsumer.TermWant.Value)
        return str(Results)
    except ValueError:
        return ""
    except:
        print "Unexpected error in SQL_FindAPR:"
        print "sSellingPrice = " + str(sSellingPrice)
        print "sInvoice = " + str(sInvoice)
        print "iCashCost = " + str(iCashCost)
        print "sTradeIn = " + str(sTradeIn)
        print "sPayoff = " + str(sPayoff)
        print "sDownCash = " + str(sDownCash)
        print "sFico = " + str(sFico)
        raise


def SQL_FindMonthly(sSellingPrice, sInvoice, iCashCost, sTradeIn, sPayoff, sDownCash, sFico):
    # Find required MonthlyPayments for a given DownCash figure
    # Logic: LoanAmount = Price - [ DownCash + TradeIn - TradeInPayoff ]
    #        LTV = LoanAmount / Invoice
    #        Use LTV and FICO to find [Monthly%] in the M72 table
    #        The M72 tables incorporates the active APR grid
    #        Monthly% is the Monthly payment as a % of LoanAmount
    #        MonthlyPayment = [Monthly%] * LoanAmount
    try:
        Invoice = float(fixZero(sInvoice, fixZero(sSellingPrice, iCashCost)))
        if Invoice == 0:
            return "0"
        TradeInNet = float(fixNull(sTradeIn, 0)) - float(fixNull(sPayoff, 0))
        DownPayment = float(fixNull(sDownCash, 0)) + TradeInNet
        LoanAmount = iCashCost - DownPayment
        LTV = LoanAmount / Invoice
        sFico = fixNull(sFico, str(G_LowestFicoAnywhere))
        Results = MyAPR.GetMonthly(sFico, LTV, MyConsumer.TermWant.Value) * LoanAmount
        return str(int(round(Results)))
    except ValueError:
        return ""
    except:
        print "Unexpected error in SQL_FindMonthly:"
        print "sSellingPrice = " + str(sSellingPrice)
        print "sInvoice = " + str(sInvoice)
        print "iCashCost = " + str(iCashCost)
        print "sTradeIn = " + str(sTradeIn)
        print "sPayoff = " + str(sPayoff)
        print "sDownCash = " + str(sDownCash)
        print "sFico = " + str(sFico)
        raise


def SQL_FindDown(sSellingPrice, sInvoice, iCashCost, sTradeIn, sPayoff, sMonthly, sFico):
    # Find required DownCash for a given MonthlyPayment figure
    # This is the reverse of SQL_DealUpfront()
    # Note: This one is tricky, since APR computation requires knowing LTV,
    #       but LTV is driven by DownCash -- which is the solution we seek
    #       It is assumed that APR is monotone increasing with LTV
    #
    # Logic: Try each LTV granularity possibility starting with the lowest LTV
    #       The list length is the number of LTV granulations (=17)
    #       For each LTV in the list:
    #           Use FICO and LTV to find [Monthly%] in the M72 Table
    #           LoanAmount = MonthlyPayment / [%Monthly]
    #           ConsequentLTV = LoanAmount / Invoice
    #           If ConsequentLTV > LTV, not a solution; continue to next LTV
    #       If reached highest LTV, and still not a solution; use highest LTV
    #       Once a solution is found (or using highest):
    #           DownCash = Price - LoanAmount - [TradeIn - TradeInPayoff]
    try:
        Invoice = float(fixZero(sInvoice, fixZero(sSellingPrice, iCashCost)))
        if Invoice == 0:
            return "0"
        TradeInNet = float(fixNull(sTradeIn, 0)) - float(fixNull(sPayoff, 0))
        Monthly = float(fixNull(sMonthly, 0))
        sFico = fixNull(sFico, str(G_LowestFicoAnywhere))

        NeedSolution = True
        TryLTV = MyAPR.LowLTV
        while TryLTV <= MyAPR.HighLTV and NeedSolution:
            LoanAmount = Monthly / MyAPR.GetMonthly(sFico, TryLTV, MyConsumer.TermWant.Value)
            NeedSolution = (LoanAmount / Invoice) > TryLTV
            TryLTV += MyAPR.StepLTV

        Results = iCashCost - LoanAmount - TradeInNet
        return str(int(round(Results)))
    except ValueError:
        return ""
    except:
        print "Unexpected error in SQL_FindDown:"
        print "sSellingPrice = " + str(sSellingPrice)
        print "sInvoice = " + str(sInvoice)
        print "iCashCost = " + str(iCashCost)
        print "sTradeIn = " + str(sTradeIn)
        print "sPayoff = " + str(sPayoff)
        print "sMonthly = " + str(sMonthly)
        print "sFico = " + str(sFico)
        raise


def ListSort(L):
    return sorted(L)
# Begin Main

# print "*** Start ***"
MMList = TrimTop()
# upload Trim_Top table
if False:
    print "*** Dictionary from Makes to Models ***"
    print MMList.MakesDict
    print "*** List of Makes ***"
    print MMList.MakesDict.keys()
    print "*** Dictionary from Makes(Models) to Trims ***"
    print MMList.ModelsDict
    print "*** List of Makes(Models) ***"
    print MMList.ModelsList

MyFilterArray = FilterArray(MMList)
# MyFilterArray.Filter["Model"] = MyFilterArray.FixModel(MMList)
# Generate a Filter Array
if False:
    print "*** MyFilterArray ***"
    print MyFilterArray

MyZip = byZIP()
# upload Zip tables from database

MyAPR = APRTable()
# Upload APR table from database

MyConsumer = ConsumerInfo("")
# Create a variable holding consumer information
# print "*** Showing MyConsumer before making guesses ***"
# print MyConsumer
MyConsumer.MakeGuesses(MyZip)
# print "*** Showing MyConsumer after making guesses ***"
# print MyConsumer
# print "*** Finished ***"
MySelections = VehicleArray(MyFilterArray, MyConsumer, MyAPR)
# Now, lets start the web app


urls = (  '/', 'Index')

app = web.application(urls, globals())
application = app.wsgifunc()  # Activate this line in PythonAnywhere!

render = web.template.render('templates/',
                             base="layout",
                             globals={'WebSort': ListSort})

if __name__ == "__main__":
    app.run()
