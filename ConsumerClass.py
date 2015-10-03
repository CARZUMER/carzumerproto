# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 06:43:04 2015

@author: Dan
"""

import cfg
from StringClean import isNull, fixNull, fixZero, float0, strRound
from ReadZip import MyZip
import sha
import time

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

    def __init__(self, OriginZip):
        # The process of creating a new member of the ConsumerInfo class
        # takes one, optional, parameter: The Zip code of the consumer.
        # It is intended that this code will be surmised from the
        # connectivity mechanism of the browser GET query.  If not available,
        # it will default to the global cfg.DefaultZip (90650)
        self.ConsumerID = str(sha.new(repr(time.time())).hexdigest())
        self.CreateTime = time.time()
        self.CreateTimeStamp = time.asctime()
        self.LastAccessed = self.CreateTime
        self.LastAccessedTimeStamp = self.CreateTimeStamp
        self.Message = "New Session (Logged Out)"
        self.username = ""
        self.loggedIn = "N"

        self.Zip = UserField("Zip Code")
        self.Zip.isFocus = True
        if isNull(OriginZip):
            self.Zip.Value = cfg.DefaultZip
            self.Zip.GuessBasis = "Global Default Zip"
        else:
            self.Zip.Value = OriginZip
            self.Zip.GuessBasis = "Origin Zip"

        self.Fico = UserField("FICO Score")
        self.Income = UserField("Monthly Gross Income")
        self.DebtService = UserField("Monthly Expenses")
        self.isHomeowner = UserField("Homeowner?")
        self.isCosigner = UserField("Co-Signer Available?")
        self.Cosigner = UserField("Co-Signer FICO")
        self.isTradeIn = UserField("Trade-In Available?")
        self.TradeInValue = UserField("Trade-In Value")
        self.TradeInPayoff = UserField("Trade-In Loan Payoff")
        self.UpfrontWant = UserField("Down Payment Wanted")
        self.UpfrontMax = UserField("Down Payment Maximum")
        self.MonthlyWant = UserField("Monthly Payment Wanted")
        self.MonthlyMax = UserField("Monthly Payment Maximum")
        self.TermWant = UserField("Loan Term (months) Wanted")

        self.Latitude = UserField("Latitude")
        self.Longitude = UserField("Longitude")
        self.TaxRate = UserField("Sales Tax Rate")
        self.TradeInTaxCredit = UserField("Sales Tax Credit for Trade-In")

        self.MakeGuesses()

    def __repr__(self):
        return "%s\n"*20 % (
            self.ConsumerID,
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

    def MakeGuesses(self):
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
        # This method requires a prepared MyZip (MyZIP, the only member of
        #   the byZIP class should be initialized prior to the first call to
        #   MakeGuesses, and used each time).
        #
        # The following logic is used to generate guesses:
        # ------------------------------------------------
        #   Zip: Use global default (cfg.DefaultZip = 90650)
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
        #             cfg.SlopeFicoFromIncome = 0.00074811*12
        #             cfg.InterceptFicoFromIncome = 657.7013707
        #             cfg.LowestFicoFromIncome = 640
        #             cfg.HighstFicoFromIncome = 800
        #             cfg.FicoRound = 1
        #
        #   Income: If no actual Fico was provided, lookup from Zip
        #           If fico is provided, apply income->fico model in reverse
        #           The final result is rounded, lower-, and upper- bounded.
        #             cfg.LowestIncomeFromFico = 2500
        #             cfg.HighstIncomeFromFico = 7500
        #             cfg.IncomeRound = 100
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
                            (self.Zip.Value not in MyZip.Income)

        self.Fico.Value = strRound(self.Fico.Value,
                                      1,
                                      cfg.LowestFicoAnywhere,
                                      cfg.HighestFicoAnywhere)
        self.Fico.isGuess = self.Fico.isGuess or isNull(self.Fico.Value)

        self.Income.Value = strRound(self.Income.Value,
                                      1,
                                      cfg.LowestIncomeAnywhere,
                                      cfg.HighestIncomeAnywhere)
        self.Income.isGuess = self.Income.isGuess or isNull(self.Income.Value)

        self.DebtService.Value = strRound(self.DebtService.Value,
                                          1,
                                          cfg.LowestIncomeAnywhere,
                                          cfg.HighestIncomeAnywhere)
        self.DebtService.isGuess = self.DebtService.isGuess or isNull(self.DebtService.Value)


        self.Cosigner.Value = strRound(self.Cosigner.Value,
                                          1,
                                          cfg.LowestFicoAnywhere,
                                          cfg.HighestFicoAnywhere)
        self.Cosigner.isGuess = self.Cosigner.isGuess or isNull(self.Cosigner.Value)

        self.TradeInValue.Value = strRound(self.TradeInValue.Value,
                                              1,
                                              cfg.LowestTradeInAnywhere,
                                              cfg.HighestTradeInAnywhere)
        self.TradeInValue.isGuess = self.TradeInValue.isGuess or isNull(self.TradeInValue.Value)

        self.TradeInPayoff.Value = strRound(self.TradeInPayoff.Value,
                                              1,
                                              cfg.LowestTradeInAnywhere,
                                              cfg.HighestTradeInAnywhere)
        self.TradeInPayoff.isGuess = self.TradeInPayoff.isGuess or isNull(self.TradeInPayoff.Value)

        self.UpfrontWant.Value = strRound(self.UpfrontWant.Value,
                                              1,
                                              cfg.LowestUpfrontAnywhere,
                                              cfg.HighestUpfrontAnywhere)
        self.UpfrontWant.isGuess = self.UpfrontWant.isGuess or isNull(self.UpfrontWant.Value)

        self.UpfrontMax.Value = strRound(self.UpfrontMax.Value,
                                              1,
                                              cfg.LowestUpfrontAnywhere,
                                              cfg.HighestUpfrontAnywhere)
        self.UpfrontMax.isGuess = self.UpfrontMax.isGuess or isNull(self.UpfrontMax.Value)

        self.MonthlyWant.Value = strRound(self.MonthlyWant.Value,
                                              1,
                                              cfg.LowestMonthlyAnywhere,
                                              cfg.HighestMonthlyAnywhere)
        self.MonthlyWant.isGuess = self.MonthlyWant.isGuess or isNull(self.MonthlyWant.Value)

        self.MonthlyMax.Value = strRound(self.MonthlyMax.Value,
                                              1,
                                              cfg.LowestMonthlyAnywhere,
                                              cfg.HighestMonthlyAnywhere)
        self.MonthlyMax.isGuess = self.MonthlyMax.isGuess or isNull(self.MonthlyMax.Value)

        self.TermWant.Value = strRound(self.TermWant.Value,
                                              cfg.TermRound,
                                              cfg.LowestTermAnywhere,
                                              cfg.HighestTermAnywhere)
        self.TermWant.isGuess = self.TermWant.isGuess or isNull(self.TermWant.Value)

        ###### SYSTEM GUESS ALGORITHMS BEGIN HERE #####
        if self.Zip.isGuess:
            self.Zip.Value = cfg.DefaultZip
            self.Zip.GuessBasis = "Default Zip Code"

        self.Latitude.Value = MyZip.Latitude[self.Zip.Value]
        self.Latitude.isGuess = self.Zip.isGuess
        self.Latitude.GuessBasis = "Table lookup from Zip"

        self.Longitude.Value = MyZip.Longitude[self.Zip.Value]
        self.Longitude.isGuess = self.Zip.isGuess
        self.Longitude.GuessBasis = "Table lookup from Zip"

        self.TaxRate.Value = MyZip.TaxRate[self.Zip.Value]
        self.TaxRate.isGuess = self.Zip.isGuess
        self.TaxRate.GuessBasis = "Table lookup from Zip"

        self.TradeInTaxCredit.Value = MyZip.TradeInTaxCredit[self.Zip.Value]
        self.TradeInTaxCredit.isGuess = self.Zip.isGuess
        self.TradeInTaxCredit.GuessBasis = "Table lookup from Zip"


        if self.Fico.isGuess:
            if self.Income.isGuess:
                self.Fico.Value = strRound(
                                  MyZip.FICO3[self.Zip.Value],
                                  cfg.FicoRound,
                                  cfg.LowestFicoAnywhere,
                                  cfg.HighestFicoAnywhere)
                self.Fico.GuessBasis = "from Zip-based model"
            else:
                self.Fico.Value = strRound(
                                  max(cfg.LowestFicoFromIncome,
                                  min(cfg.HighstFicoFromIncome,
                                      cfg.SlopeFicoFromIncome *
                                      float(self.Income.Value) +
                                      cfg.InterceptFicoFromIncome +
                                      MyZip.ST2offset[self.Zip.Value])),
                                      cfg.FicoRound,
                                      cfg.LowestFicoAnywhere,
                                      cfg.HighestFicoAnywhere)
                self.Fico.GuessBasis = "from ACTUAL Income, offset by State"

        if self.Income.isGuess:
            if self.Fico.isGuess:
                self.Income.Value = strRound(MyZip.Income[self.Zip.Value],
                                             cfg.IncomeRound,
                                             cfg.LowestIncomeAnywhere,
                                             cfg.HighestIncomeAnywhere)
                self.Income.GuessBasis = "from Zip Median table"
            else:
                self.Income.Value = strRound(
                                    max(cfg.LowestIncomeFromFico,
                                    min(cfg.HighstIncomeFromFico,
                                        (float(self.Fico.Value) -
                                         MyZip.ST2offset[self.Zip.Value] -
                                         cfg.InterceptFicoFromIncome) /
                                        cfg.SlopeFicoFromIncome)),
                                    cfg.IncomeRound,
                                    cfg.LowestIncomeAnywhere,
                                    cfg.HighestIncomeAnywhere)
                self.Income.GuessBasis = "from ACTUAL FICO, offset by State"

        if self.DebtService.isGuess:
            self.DebtService.Value = strRound(
                                      float(self.Income.Value) *
                                      cfg.DebtPercentofIncome,
                                      cfg.DebtRound,
                                      cfg.LowestIncomeAnywhere,
                                      cfg.HighestIncomeAnywhere)
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
                                      MyZip.FICO3[self.Zip.Value],
                                      cfg.FicoRound,
                                      cfg.LowestFicoAnywhere,
                                      cfg.HighestFicoAnywhere)
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
                                    cfg.TradeInIncomeMonths,
                                    cfg.TradeInRound,
                                    cfg.LowestTradeInAnywhere,
                                    cfg.HighestTradeInAnywhere)
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
                                          max(cfg.LowestUpfrontWanted,
                                          min(cfg.HighestUpfrontWanted,
                                          float(self.Income.Value) *
                                          cfg.UpfrontWantedIncomeMonths)),
                                          cfg.UpfrontRound,
                                          cfg.LowestUpfrontAnywhere,
                                          cfg.HighestUpfrontAnywhere)
                self.UpfrontWant.GuessBasis = "Months of Income"
            else:
                self.UpfrontWant.Value = self.UpfrontMax.Value
                self.UpfrontWant.GuessBasis = "ACTUAL Upfront Maximum"

        if self.UpfrontMax.isGuess:
            if self.UpfrontWant.isGuess:
                self.UpfrontMax.Value = strRound(
                                          max(cfg.LowestUpfrontMax,
                                          min(cfg.HighestUpfrontMax,
                                          float(self.Income.Value) *
                                          cfg.UpfrontMaxIncomeMonths)),
                                          cfg.UpfrontRound,
                                          cfg.LowestUpfrontAnywhere,
                                          cfg.HighestUpfrontAnywhere)
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
                                          max(cfg.LowestMonthlyWanted,
                                          min(cfg.HighestMonthlyWanted,
                                          (float(self.Income.Value) -
                                          float(self.DebtService.Value))*
                                          cfg.MonthlyWantedPercentofIncome)),
                                          cfg.MonthlyRound,
                                          cfg.LowestMonthlyAnywhere,
                                          cfg.HighestMonthlyAnywhere)
                self.MonthlyWant.GuessBasis = "Percent of Income"
            else:
                self.MonthlyWant.Value = self.MonthlyMax.Value
                self.MonthlyWant.GuessBasis = "ACTUAL Monthly Maximum"

        if self.MonthlyMax.isGuess:
            if self.MonthlyWant.isGuess:
                self.MonthlyMax.Value = strRound(
                                          max(cfg.LowestMonthlyMax,
                                          min(cfg.HighestMonthlyMax,
                                          (float(self.Income.Value) -
                                          float(self.DebtService.Value))*
                                          cfg.MonthlyMaxPercentofIncome)),
                                          cfg.MonthlyRound,
                                          cfg.LowestMonthlyAnywhere,
                                          cfg.HighestMonthlyAnywhere)
                self.MonthlyMax.GuessBasis = "Percent of Income"
            else:
                self.MonthlyMax.Value = self.MonthlyWant.Value
                self.MonthlyMax.GuessBasis = "ACTUAL Monthly Wanted"

        elif float(self.MonthlyMax.Value) < float(self.MonthlyWant.Value):
            self.MonthlyMax.Value = self.MonthlyWant.Value
            self.MonthlyMax.isGuess = True
            self.MonthlyMax.GuessBasis = "OVER-WRITE Max to Equal Wanted"

        if self.TermWant.isGuess:
            self.TermWant.Value = cfg.TermWanted
            self.TermWant.GuessBasis = "Always defaults to 72"


#MyConsumer = ConsumerInfo("")
#MyConsumer0 = ConsumerInfo("")